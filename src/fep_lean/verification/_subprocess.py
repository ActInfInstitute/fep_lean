"""Bounded capture with private, cooperative, root-owned POSIX groups.

Only groups created by the private broker can be signalled. Raw unregistered
detached sessions are outside descendant cleanup, but cannot hold capture open
indefinitely after cancellation. Other platforms receive direct-child cleanup.
"""

from __future__ import annotations

import base64
import contextlib
import json
import locale
import math
import os
import secrets
import selectors
import signal
import socket
import struct
import subprocess
import sys
import tempfile
import threading
import time
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import Any, Final, Literal, overload

__all__ = ["run_process_group"]
_REAP_TIMEOUT_S: Final = 0.5
_CHANNEL_TIMEOUT_S: Final = 5.0
_MAX_FRAME_BYTES: Final = 32 * 1024 * 1024
_SOCKET_ENV: Final = "FEP_LEAN_PROCESS_OWNER_SOCKET"
_TOKEN_ENV: Final = "FEP_LEAN_PROCESS_OWNER_TOKEN"

# The actual tool inherits this new group. Its leader stays alive (or unreaped
# on external death) until the root kills/deregisters it. No client supplies a
# PID, signal, executable code or import path to this guard.
_GUARD_PROGRAM = r"""
import json, os, socket, struct, subprocess, sys
channel = socket.socket(fileno=int(sys.argv[1]))
os.set_inheritable(channel.fileno(), False)
def receive(n):
    parts = []
    while n:
        part = channel.recv(n)
        if not part:
            raise EOFError('launch channel closed')
        parts.append(part)
        n -= len(part)
    return b''.join(parts)
size = struct.unpack('!I', receive(4))[0]
if not 0 < size <= 33554432:
    raise ValueError('invalid launch frame')
command = json.loads(receive(size))
try:
    result = {'returncode': subprocess.Popen(command).wait()}
except OSError as error:
    result = {'oserror': [error.errno, error.strerror, error.filename]}
data = json.dumps(result, allow_nan=False).encode('utf-8')
channel.sendall(struct.pack('!I', len(data)) + data)
channel.recv(1)
"""


def _valid_timeout(timeout: object) -> bool:
    """Keep None unbounded; refuse malformed budgets before any allocation."""
    if timeout is None:
        return True
    if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
        return False
    try:
        # The remote capture channel adds the existing drain allowance before
        # socket.settimeout. Stay within Python's exposed wait representation.
        return (
            timeout > 0
            and math.isfinite(timeout)
            and timeout + 2 * _REAP_TIMEOUT_S <= threading.TIMEOUT_MAX
        )
    except OverflowError:
        return False


def _frame_bytes(value: Any) -> bytes:
    data = json.dumps(value, allow_nan=False).encode("utf-8")
    if not 0 < len(data) <= _MAX_FRAME_BYTES:
        raise ValueError("process supervision frame exceeds its bound")
    return struct.pack("!I", len(data)) + data


def _send_frame(channel: socket.socket, value: Any) -> None:
    channel.sendall(_frame_bytes(value))


def _read_frame(channel: socket.socket, header: bytes = b"") -> Any:
    def receive(count: int) -> bytes:
        parts = []
        while count:
            part = channel.recv(count)
            if not part:
                raise OSError("process supervision channel closed")
            parts.append(part)
            count -= len(part)
        return b"".join(parts)

    if len(header) > 4:
        raise ValueError("invalid process supervision frame header")
    count = struct.unpack("!I", header + receive(4 - len(header)))[0]
    if not 0 < count <= _MAX_FRAME_BYTES:
        raise ValueError("invalid process supervision frame length")
    return json.loads(receive(count))


def _text(data: bytes) -> str:
    return (
        data.decode(locale.getpreferredencoding(False))
        .replace("\r\n", "\n")
        .replace("\r", "\n")
    )


class _Group:
    def __init__(
        self,
        process: subprocess.Popen[bytes],
        channel: socket.socket,
        *,
        scope_token: str,
        parent: _Group | None,
    ):
        self.process = process
        self.channel = channel
        self.scope_token = scope_token
        self.parent = parent
        self.children: set[_Group] = set()
        self.finished = threading.Event()
        self.expired = threading.Event()
        self.cancel = threading.Event()
        self.outcome: dict[str, Any] | None = None
        self.error: BaseException | None = None


class _Broker:
    def __init__(self) -> None:
        self.directory = tempfile.TemporaryDirectory(prefix="fep-pg-", dir="/tmp")
        self.address = str(Path(self.directory.name) / "owner.sock")
        # Retained for compatibility with rejection controls, never allocation.
        self.token = secrets.token_hex(32)
        self.lock = threading.RLock()
        self.groups: set[_Group] = set()
        self.scopes: dict[str, _Group] = {}
        self.issued_tokens = {self.token}
        self.connections: set[socket.socket] = set()
        self.workers: set[threading.Thread] = set()
        self.closed = False
        self.listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.listener.bind(self.address)
        self.listener.listen()
        self.listener.settimeout(0.05)
        self.server = threading.Thread(target=self._serve, daemon=True)
        self.server.start()

    def release(self, group: _Group, *, cancelled: bool = False) -> None:
        with self.lock:
            if group not in self.groups:
                return
            pending, subtree = [group], []
            while pending:
                current = pending.pop()
                if current in self.groups:
                    subtree.append(current)
                    pending.extend(current.children)
            # Revoke the entire registered subtree before another request can
            # acquire the lock. Only fresh groups created here grant authority.
            for current in subtree:
                self.groups.remove(current)
                self.scopes.pop(current.scope_token)
            for current in reversed(subtree):
                if cancelled or current is not group:
                    current.expired.set()
                if current.parent is not None:
                    current.parent.children.discard(current)
                current.children.clear()
                # The unreaped guard reserves its original group identity;
                # neither a supplied PID nor a process census grants authority.
                with contextlib.suppress(ProcessLookupError):
                    os.killpg(current.process.pid, signal.SIGKILL)
                current.cancel.set()
                with contextlib.suppress(OSError):
                    current.channel.shutdown(socket.SHUT_RDWR)
                current.channel.close()

    def _scope(self, token: str) -> _Group:
        with self.lock:
            group = self.scopes.get(token)
            if self.closed or group is None or group not in self.groups:
                raise ValueError("inactive process supervision scope")
            return group

    def abort(self) -> None:
        with self.lock:
            self.closed = True
            for group in tuple(self.groups):
                self.release(group, cancelled=True)

    def close(self) -> None:
        self.abort()
        self.listener.close()
        with self.lock:
            for connection in tuple(self.connections):
                with contextlib.suppress(OSError):
                    connection.shutdown(socket.SHUT_RDWR)
                connection.close()
        self.server.join(timeout=_REAP_TIMEOUT_S)
        deadline = time.monotonic() + _REAP_TIMEOUT_S
        with self.lock:
            workers = tuple(self.workers)
        for worker in workers:
            worker.join(timeout=max(0, deadline - time.monotonic()))
        if any(worker.is_alive() for worker in workers):
            raise OSError("process supervision workers did not finish bounded cleanup")
        self.directory.cleanup()

    def _serve(self) -> None:
        while not self.closed:
            try:
                connection, _ = self.listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            with self.lock:
                if self.closed:
                    connection.close()
                    return
                self.connections.add(connection)
            worker = threading.Thread(
                target=lambda c=connection: self._request(c), daemon=True
            )
            with self.lock:
                self.workers.add(worker)
            worker.start()

    def _request(self, connection: socket.socket) -> None:
        descriptors: list[int] = []
        try:
            connection.settimeout(_CHANNEL_TIMEOUT_S)
            header, descriptors, flags, _ = socket.recv_fds(connection, 4, 3)
            for descriptor in descriptors:
                os.set_inheritable(descriptor, False)
            if flags & socket.MSG_CTRUNC:
                raise ValueError("truncated process supervision descriptors")
            request = _read_frame(connection, header)
            if (
                not isinstance(request, dict)
                or set(request)
                != {"token", "command", "cwd", "env", "timeout", "capture"}
                or not isinstance(request["token"], str)
                or not isinstance(request["command"], list)
                or not request["command"]
                or any(type(v) is not str for v in request["command"])
                or type(request["cwd"]) is not str
                or not isinstance(request["env"], dict)
                or any(
                    type(k) is not str or type(v) is not str
                    for k, v in request["env"].items()
                )
                or type(request["capture"]) is not bool
                or not _valid_timeout(request["timeout"])
            ):
                raise ValueError("invalid process supervision request")
            if len(descriptors) != (1 if request["capture"] else 3):
                raise ValueError("invalid process supervision descriptors")
            parent = self._scope(request["token"])
            connection.settimeout(_REAP_TIMEOUT_S)

            def forward(name: str, data: bytes) -> None:
                _send_frame(
                    connection,
                    {
                        "kind": "stream",
                        "pipe": name,
                        "data": base64.b64encode(data).decode("ascii"),
                    },
                )

            # Inherited descriptors belong to the requesting caller. Captured
            # streams travel as bounded raw-byte frames, never one giant result.
            result = self.run(
                request["command"],
                cwd=request["cwd"],
                env=request["env"],
                timeout=request["timeout"],
                capture=request["capture"],
                root=False,
                parent=parent,
                forward=forward if request["capture"] else None,
                stdin=descriptors[0],
                output_fds=None
                if request["capture"]
                else (descriptors[1], descriptors[2]),
            )
            response = {
                "kind": "completed",
                "returncode": result.returncode,
                "stdout_bytes": len(result.stdout) if request["capture"] else 0,
                "stderr_bytes": len(result.stderr) if request["capture"] else 0,
            }
        except subprocess.TimeoutExpired as error:
            response = {
                "kind": "timeout",
                "timeout": error.timeout,
                "stdout_bytes": len(error.output) if error.output else 0,
                "stderr_bytes": len(error.stderr) if error.stderr else 0,
            }
        except OSError as error:
            response = {"kind": "oserror", "error": [error.errno, str(error)]}
        except (ValueError, TypeError, KeyError, RecursionError) as error:
            response = {"kind": "error", "error": str(error)}
        try:
            _send_frame(connection, response)
        except (OSError, ValueError):
            pass  # The owning outer worker can exit or be cancelled first.
        finally:
            for descriptor in descriptors:
                os.close(descriptor)
            with self.lock:
                self.connections.discard(connection)
                self.workers.discard(threading.current_thread())
            connection.close()

    def run(
        self,
        command: Sequence[str],
        *,
        cwd: str | os.PathLike[str],
        env: Mapping[str, str],
        timeout: float | None,
        capture: bool,
        root: bool,
        parent: _Group | None = None,
        forward: Callable[[str, bytes], None] | None = None,
        stdin: int | None = None,
        output_fds: tuple[int, int] | None = None,
    ) -> subprocess.CompletedProcess[Any]:
        deadline = None if timeout is None else time.monotonic() + timeout
        with self.lock:
            if self.closed:
                raise subprocess.TimeoutExpired(
                    list(command),
                    timeout if timeout is not None else _REAP_TIMEOUT_S,
                )
            if (root and parent is not None) or (
                not root
                and (
                    parent is None
                    or parent not in self.groups
                    or self.scopes.get(parent.scope_token) is not parent
                )
            ):
                raise ValueError("inactive process supervision scope")
            scope_token = secrets.token_hex(32)
            if scope_token in self.issued_tokens:
                raise OSError("process supervision scope capability collision")
            self.issued_tokens.add(scope_token)
            local, child = socket.socketpair()
            child_environment = {
                **env,
                _SOCKET_ENV: self.address,
                _TOKEN_ENV: scope_token,
            }
            try:
                process = subprocess.Popen(
                    [
                        sys.executable,
                        "-I",
                        "-S",
                        "-c",
                        _GUARD_PROGRAM,
                        str(child.fileno()),
                    ],
                    cwd=str(cwd),
                    env=child_environment,
                    stdin=stdin,
                    stdout=subprocess.PIPE
                    if capture
                    else (output_fds[0] if output_fds else None),
                    stderr=subprocess.PIPE
                    if capture
                    else (output_fds[1] if output_fds else None),
                    start_new_session=True,
                    pass_fds=(child.fileno(),),
                )
                group = _Group(process, local, scope_token=scope_token, parent=parent)
                self.groups.add(group)
                self.scopes[scope_token] = group
                if parent is not None:
                    parent.children.add(group)
            except BaseException:
                local.close()
                child.close()
                raise
        child.close()

        def outcome() -> None:
            try:
                payload = _read_frame(local)
                if not isinstance(payload, dict) or set(payload) not in (
                    {"returncode"},
                    {"oserror"},
                ):
                    raise ValueError("invalid process guard outcome")
                group.outcome = payload
            except (OSError, ValueError, TypeError, RecursionError) as error:
                group.error = error
            finally:
                self.release(group)
                group.finished.set()
                if root:
                    self.abort()

        def watchdog() -> None:
            remaining = (
                None if deadline is None else max(0, deadline - time.monotonic())
            )
            if group.cancel.wait(remaining):
                return
            group.expired.set()
            if root:
                self.abort()
            else:
                self.release(group, cancelled=True)

        guard_reader = threading.Thread(target=outcome, daemon=True)
        timer = threading.Thread(target=watchdog, daemon=True)
        reader_started = False
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        streams = [p for p in (process.stdout, process.stderr) if p is not None]
        try:
            timer.start()
            _send_frame(local, list(command))  # Register before actual tool launch.
            guard_reader.start()
            reader_started = True
            with selectors.DefaultSelector() as selector:
                for name, pipe in (
                    ("stdout", process.stdout),
                    ("stderr", process.stderr),
                ):
                    if pipe is not None:
                        os.set_blocking(pipe.fileno(), False)
                        selector.register(pipe, selectors.EVENT_READ, name)
                drain_deadline = None
                while True:
                    now = time.monotonic()
                    if (
                        deadline is not None
                        and now >= deadline
                        and not group.cancel.is_set()
                    ):
                        group.expired.set()
                        if root:
                            self.abort()
                        else:
                            self.release(group, cancelled=True)
                    if group.cancel.is_set() and drain_deadline is None:
                        drain_deadline = now + _REAP_TIMEOUT_S
                    if group.finished.is_set() and not selector.get_map():
                        break
                    if drain_deadline is not None and now >= drain_deadline:
                        group.expired.set()  # Reject incomplete held-pipe capture.
                        break
                    if not selector.get_map():
                        group.finished.wait(0.01)
                        continue
                    for key, _ in selector.select(0.01):
                        chunk = os.read(key.fd, 65536)
                        if chunk:
                            buffers[key.data].extend(chunk)
                            if forward is not None:
                                forward(key.data, chunk)
                        else:
                            selector.unregister(key.fileobj)
            self.release(group)
            process.wait(timeout=_REAP_TIMEOUT_S)
            if group.expired.is_set():
                raise subprocess.TimeoutExpired(
                    list(command),
                    timeout if timeout is not None else _REAP_TIMEOUT_S,
                    output=bytes(buffers["stdout"]),
                    stderr=bytes(buffers["stderr"]),
                )
            if group.error is not None:
                raise OSError(
                    "process guard closed without a complete outcome"
                ) from group.error
            assert group.outcome is not None
            if "oserror" in group.outcome:
                number, message, filename = group.outcome["oserror"]
                raise OSError(number, message, filename)
            return subprocess.CompletedProcess(
                list(command),
                group.outcome["returncode"],
                (
                    bytes(buffers["stdout"])
                    if forward
                    else _text(bytes(buffers["stdout"]))
                )
                if capture
                else None,
                (
                    bytes(buffers["stderr"])
                    if forward
                    else _text(bytes(buffers["stderr"]))
                )
                if capture
                else None,
            )
        except OSError:
            if group.expired.is_set():
                raise subprocess.TimeoutExpired(
                    list(command),
                    timeout if timeout is not None else _REAP_TIMEOUT_S,
                    output=bytes(buffers["stdout"]) if capture else None,
                    stderr=bytes(buffers["stderr"]) if capture else None,
                ) from None
            raise
        finally:
            self.release(group)
            for stream in streams:
                stream.close()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=_REAP_TIMEOUT_S)
            group.cancel.set()
            timer.join(timeout=_REAP_TIMEOUT_S)
            if reader_started:
                guard_reader.join(timeout=_REAP_TIMEOUT_S)


def _remote(
    command: Sequence[str],
    *,
    cwd: str | os.PathLike[str],
    env: Mapping[str, str],
    timeout: float | None,
    capture: bool,
) -> subprocess.CompletedProcess[Any]:
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
        channel.settimeout(_CHANNEL_TIMEOUT_S)
        channel.connect(os.environ[_SOCKET_ENV])
        frame = _frame_bytes(
            {
                "token": os.environ[_TOKEN_ENV],
                "command": list(command),
                "cwd": os.fspath(cwd),
                "env": dict(env),
                "timeout": timeout,
                "capture": capture,
            },
        )
        # SCM_RIGHTS duplicates only the caller's inherited standard streams;
        # it grants no PID or signal authority to the broker client.
        sent = socket.send_fds(channel, [frame], [0] if capture else [0, 1, 2])
        channel.sendall(frame[sent:])
        channel.settimeout(
            None if timeout is None else max(0.001, timeout) + 2 * _REAP_TIMEOUT_S
        )
        buffers = {"stdout": bytearray(), "stderr": bytearray()}
        try:
            while True:
                result = _read_frame(channel)
                if not isinstance(result, dict) or result.get("kind") != "stream":
                    break
                if (
                    not capture
                    or set(result) != {"kind", "pipe", "data"}
                    or result["pipe"] not in buffers
                    or type(result["data"]) is not str
                ):
                    raise OSError("invalid process supervision stream")
                name = result["pipe"]
                buffers[name].extend(base64.b64decode(result["data"], validate=True))
        except TimeoutError:
            raise subprocess.TimeoutExpired(
                list(command),
                timeout if timeout is not None else _REAP_TIMEOUT_S,
                output=bytes(buffers["stdout"]) if capture else None,
                stderr=bytes(buffers["stderr"]) if capture else None,
            ) from None
    if not isinstance(result, dict):
        raise OSError("invalid process supervision response")
    if result.get("kind") == "timeout":
        _check_stream_sizes(result, buffers)
        raise subprocess.TimeoutExpired(
            list(command),
            result["timeout"],
            output=bytes(buffers["stdout"]) if capture else None,
            stderr=bytes(buffers["stderr"]) if capture else None,
        )
    if result.get("kind") == "oserror":
        raise OSError(*result["error"])
    if result.get("kind") != "completed":
        raise OSError("process supervision request rejected")
    _check_stream_sizes(result, buffers)
    return subprocess.CompletedProcess(
        list(command),
        result["returncode"],
        _text(bytes(buffers["stdout"])) if capture else None,
        _text(bytes(buffers["stderr"])) if capture else None,
    )


def _check_stream_sizes(
    result: Mapping[str, Any], buffers: Mapping[str, bytearray]
) -> None:
    for name in ("stdout", "stderr"):
        size = result.get(f"{name}_bytes")
        if type(size) is not int or size != len(buffers[name]):
            raise OSError("incomplete process supervision stream")


@overload
def run_process_group(
    command: Sequence[str],
    *,
    cwd: str | os.PathLike[str],
    env: Mapping[str, str] | None = ...,
    timeout: float | None,
    check: bool = ...,
    capture: Literal[True] = ...,
) -> subprocess.CompletedProcess[str]: ...


@overload
def run_process_group(
    command: Sequence[str],
    *,
    cwd: str | os.PathLike[str],
    env: Mapping[str, str] | None = ...,
    timeout: float | None,
    check: bool = ...,
    capture: Literal[False],
) -> subprocess.CompletedProcess[None]: ...


def run_process_group(
    command: Sequence[str],
    *,
    cwd: str | os.PathLike[str],
    env: Mapping[str, str] | None = None,
    timeout: float | None,
    check: bool = False,
    capture: bool = True,
) -> subprocess.CompletedProcess[str] | subprocess.CompletedProcess[None]:
    """Run an owned command and preserve text, check and typed timeout semantics.

    Cooperative nested helpers and same-group descendants are cleaned up.
    Unregistered detached sessions and non-POSIX descendants are not claimed.
    """
    if not _valid_timeout(timeout):
        raise ValueError("process timeout must be None or finite and positive")
    environment = dict(os.environ if env is None else env)
    lease = (_SOCKET_ENV in os.environ, _TOKEN_ENV in os.environ)
    if any(lease):
        if not all(lease) or os.name != "posix":
            raise OSError("incomplete or unsupported process supervision lease")
        result = _remote(
            command, cwd=cwd, env=environment, timeout=timeout, capture=capture
        )
    elif os.name == "posix":
        broker = _Broker()
        try:
            result = broker.run(
                command,
                cwd=cwd,
                env=environment,
                timeout=timeout,
                capture=capture,
                root=True,
            )
        finally:
            broker.close()
    else:
        # Direct-child only; no POSIX/cooperative-descendant guarantee.
        process = subprocess.Popen(
            list(command),
            cwd=str(cwd),
            env=environment,
            text=True,
            stdout=subprocess.PIPE if capture else None,
            stderr=subprocess.PIPE if capture else None,
        )
        try:
            stdout, stderr = process.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.communicate(timeout=_REAP_TIMEOUT_S)
            raise
        finally:
            if process.stdout is not None:
                process.stdout.close()
            if process.stderr is not None:
                process.stderr.close()
        result = subprocess.CompletedProcess(
            list(command), process.returncode, stdout, stderr
        )
    if check and result.returncode:
        raise subprocess.CalledProcessError(
            result.returncode, list(command), output=result.stdout, stderr=result.stderr
        )
    return result
