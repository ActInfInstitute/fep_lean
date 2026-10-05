"""The timeout backstop kills live probes and cancels after normal completion."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from fep_lean.verification import _subprocess
from tests._support import lean_runner


@pytest.mark.parametrize("route", ["broker", "lease", "direct"])
@pytest.mark.parametrize(
    "timeout",
    [0, -1, True, False, float("inf"), float("-inf"), float("nan"), "1", 10**400],
)
def test_invalid_process_timeout_refuses_allocation_and_dispatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, route: str, timeout: Any
) -> None:
    environment = (
        {
            _subprocess._SOCKET_ENV: "synthetic-socket",
            _subprocess._TOKEN_ENV: "synthetic-token",
        }
        if route == "lease"
        else {}
    )
    monkeypatch.setattr(
        _subprocess,
        "os",
        SimpleNamespace(
            name="nt" if route == "direct" else "posix", environ=environment
        ),
    )

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("malformed timeout allocated a broker, channel or process")

    monkeypatch.setattr(_subprocess, "_Broker", unexpected)
    monkeypatch.setattr(_subprocess, "_remote", unexpected)
    monkeypatch.setattr(_subprocess.subprocess, "Popen", unexpected)
    with pytest.raises(ValueError, match="None or finite and positive"):
        _subprocess.run_process_group(
            ["must-not-launch"], cwd=tmp_path, timeout=timeout
        )


@pytest.mark.parametrize("route", ["broker", "lease", "direct"])
@pytest.mark.parametrize("timeout", [None, 0.5, 2])
def test_valid_process_timeout_preserves_each_dispatch_contract(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, route: str, timeout: float | None
) -> None:
    environment = (
        {
            _subprocess._SOCKET_ENV: "synthetic-socket",
            _subprocess._TOKEN_ENV: "synthetic-token",
        }
        if route == "lease"
        else {}
    )
    monkeypatch.setattr(
        _subprocess,
        "os",
        SimpleNamespace(
            name="nt" if route == "direct" else "posix", environ=environment
        ),
    )
    calls: list[tuple[str, float | None]] = []

    def completed(*args: Any, **kwargs: Any) -> Any:
        calls.append(("lease", kwargs["timeout"]))
        return subprocess.CompletedProcess(["accepted"], 0, "accepted", "")

    class Broker:
        def run(self, *args: Any, **kwargs: Any) -> Any:
            calls.append(("broker", kwargs["timeout"]))
            return subprocess.CompletedProcess(["accepted"], 0, "accepted", "")

        def close(self) -> None:
            pass

    class Process:
        returncode = 0
        stdout = stderr = None

        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass

        def communicate(self, *, timeout: float | None) -> tuple[str, str]:
            calls.append(("direct", timeout))
            return "accepted", ""

    monkeypatch.setattr(_subprocess, "_Broker", Broker)
    monkeypatch.setattr(_subprocess, "_remote", completed)
    monkeypatch.setattr(_subprocess.subprocess, "Popen", Process)
    assert (
        _subprocess.run_process_group(
            ["accepted"], cwd=tmp_path, timeout=timeout
        ).stdout
        == "accepted"
    )
    assert calls == [(route, timeout)]


@pytest.mark.parametrize("timeout", [0, -1, True, 10**400])
def test_authenticated_broker_rejects_invalid_timeout_before_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, timeout: Any
) -> None:
    import threading

    class Connection:
        def settimeout(self, timeout: float) -> None:
            pass

        def close(self) -> None:
            pass

    connection = Connection()
    descriptor = os.open(os.devnull, os.O_RDONLY)
    broker = object.__new__(_subprocess._Broker)
    broker.token = "synthetic-authenticated-token"
    broker.lock = threading.Lock()
    broker.connections = {connection}
    broker.workers = set()
    request = {
        "token": broker.token,
        "command": ["must-not-launch"],
        "cwd": str(tmp_path),
        "env": {},
        "timeout": timeout,
        "capture": True,
    }
    responses: list[dict[str, Any]] = []

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("authenticated invalid budget reached broker.run")

    monkeypatch.setattr(broker, "run", unexpected)
    monkeypatch.setattr(
        _subprocess.socket,
        "recv_fds",
        lambda *args: (b"", [descriptor], 0, None),
        raising=False,
    )
    monkeypatch.setattr(_subprocess, "_read_frame", lambda *args: request)
    monkeypatch.setattr(
        _subprocess, "_send_frame", lambda channel, value: responses.append(value)
    )
    broker._request(connection)
    assert responses == [
        {"kind": "error", "error": "invalid process supervision request"}
    ]
    assert not broker.connections


def _synthetic_scope_broker() -> tuple[Any, Any]:
    class Channel:
        closed = False

        def shutdown(self, how: int) -> None:
            pass

        def close(self) -> None:
            self.closed = True

    broker = object.__new__(_subprocess._Broker)
    broker.token = "a" * 64
    broker.lock = threading.RLock()
    broker.closed = False
    parent = _subprocess._Group(
        SimpleNamespace(pid=12345),
        Channel(),
        scope_token="b" * 64,
        parent=None,
    )
    broker.groups = {parent}
    broker.scopes = {parent.scope_token: parent}
    broker.issued_tokens = {broker.token, parent.scope_token, "c" * 64}
    return broker, parent


@pytest.mark.parametrize(
    "scope", ["active", "broker-wide", "unknown", "revoked", "replayed", "late"]
)
def test_broker_authenticates_only_a_live_scope_before_child_allocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, scope: str
) -> None:
    class Connection:
        closed = False

        def settimeout(self, timeout: float) -> None:
            pass

        def close(self) -> None:
            self.closed = True

    broker, parent = _synthetic_scope_broker()
    token = parent.scope_token
    if scope == "broker-wide":
        token = broker.token
    elif scope == "unknown":
        token = "d" * 64
    elif scope == "revoked":
        broker.groups.remove(parent)
    elif scope == "replayed":
        broker.groups.remove(parent)
        broker.scopes.clear()
    connection = Connection()
    broker.connections = {connection}
    broker.workers = set()
    descriptor = os.open(os.devnull, os.O_RDONLY)
    request = {
        "token": token,
        "command": ["must-not-launch"],
        "cwd": str(tmp_path),
        "env": {},
        "timeout": 1,
        "capture": True,
    }
    responses: list[dict[str, Any]] = []
    calls: list[Any] = []

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("inactive scope allocated a child channel or process")

    def run(command: Any, **kwargs: Any) -> Any:
        assert kwargs["root"] is False and kwargs["parent"] is parent
        calls.append(parent)
        if scope == "late":
            # Interpose at the actual authentication/registration boundary.
            broker.groups.remove(parent)
            broker.scopes.clear()
            return _subprocess._Broker.run(broker, command, **kwargs)
        assert scope == "active"
        return subprocess.CompletedProcess(command, 0, b"", b"")

    monkeypatch.setattr(broker, "run", run)
    monkeypatch.setattr(_subprocess.socket, "socketpair", unexpected)
    monkeypatch.setattr(_subprocess.subprocess, "Popen", unexpected)
    monkeypatch.setattr(
        _subprocess.socket,
        "recv_fds",
        lambda *args: (b"", [descriptor], 0, None),
        raising=False,
    )
    monkeypatch.setattr(_subprocess, "_read_frame", lambda *args: request)
    monkeypatch.setattr(
        _subprocess, "_send_frame", lambda channel, value: responses.append(value)
    )
    broker._request(connection)
    if scope == "active":
        assert responses == [
            {"kind": "completed", "returncode": 0, "stdout_bytes": 0, "stderr_bytes": 0}
        ]
    else:
        assert responses == [
            {"kind": "error", "error": "inactive process supervision scope"}
        ]
    assert calls == ([parent] if scope in {"active", "late"} else [])
    assert connection.closed and not broker.connections
    with pytest.raises(OSError):
        os.fstat(descriptor)


@pytest.mark.parametrize("token", ["a" * 64, "b" * 64, "c" * 64])
def test_scope_capabilities_are_never_reissued_before_allocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, token: str
) -> None:
    broker, parent = _synthetic_scope_broker()

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("reissued scope allocated a child channel or process")

    monkeypatch.setattr(_subprocess.secrets, "token_hex", lambda count: token)
    monkeypatch.setattr(_subprocess.socket, "socketpair", unexpected)
    monkeypatch.setattr(_subprocess.subprocess, "Popen", unexpected)
    with pytest.raises(OSError, match="scope capability collision"):
        broker.run(
            ["must-not-launch"],
            cwd=tmp_path,
            env={},
            timeout=1,
            capture=True,
            root=False,
            parent=parent,
        )
    assert broker.groups == {parent} and broker.scopes == {parent.scope_token: parent}


@pytest.mark.parametrize("cancelled", [False, True])
def test_scope_release_is_iterative_revokes_before_signals_and_preserves_siblings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, cancelled: bool
) -> None:
    broker, caller = _synthetic_scope_broker()
    channel_type = type(caller.channel)

    def add(parent: Any, index: int) -> Any:
        group = _subprocess._Group(
            SimpleNamespace(pid=20000 + index),
            channel_type(),
            scope_token=f"synthetic-{index}",
            parent=parent,
        )
        broker.groups.add(group)
        broker.scopes[group.scope_token] = group
        parent.children.add(group)
        return group

    sibling = add(caller, 0)
    ancestor = add(caller, 1)
    subtree = [ancestor]
    for index in range(2, 1102):
        subtree.append(add(subtree[-1], index))
    signals: list[int] = []

    def unexpected(*args: Any, **kwargs: Any) -> Any:
        pytest.fail("revoked descendant allocated a child channel or process")

    def signal_owned(pid: int, sig: int) -> None:
        assert broker.groups == {caller, sibling}
        assert set(broker.scopes) == {caller.scope_token, sibling.scope_token}
        with pytest.raises(ValueError, match="inactive process supervision scope"):
            broker.run(
                ["must-not-launch"],
                cwd=tmp_path,
                env={},
                timeout=1,
                capture=True,
                root=False,
                parent=subtree[-1],
            )
        signals.append(pid)

    # These are synthetic registered guards, never real or census-derived PIDs.
    monkeypatch.setattr(_subprocess, "os", SimpleNamespace(killpg=signal_owned))
    monkeypatch.setattr(_subprocess, "signal", SimpleNamespace(SIGKILL=9))
    monkeypatch.setattr(_subprocess.socket, "socketpair", unexpected)
    monkeypatch.setattr(_subprocess.subprocess, "Popen", unexpected)
    broker.release(ancestor, cancelled=cancelled)
    assert signals == [group.process.pid for group in reversed(subtree)]
    assert caller.children == {sibling}
    assert not caller.cancel.is_set() and not sibling.cancel.is_set()
    assert not caller.channel.closed and not sibling.channel.closed
    for group in subtree:
        assert group.cancel.is_set() and group.channel.closed and not group.children
        assert group.expired.is_set() == (cancelled or group is not ancestor)
        with pytest.raises(ValueError, match="inactive process supervision scope"):
            broker._scope(group.scope_token)


@pytest.mark.parametrize("owner", [lean_runner])
@pytest.mark.parametrize("deadline_first", [False, True])
def test_watchdog_cancellation_and_deadline(
    owner: Any, deadline_first: bool, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    callbacks: list[Any] = []
    kills: list[tuple[int, int]] = []

    class Thread:
        def __init__(self, *, target: Any, daemon: bool) -> None:
            self.target = target

        def start(self) -> None:
            if deadline_first:
                self.target()
            else:
                callbacks.append(self.target)

        def join(self) -> None:
            for callback in callbacks:
                callback()
            callbacks.clear()

    class Process:
        pid = 456
        returncode = 0

        def communicate(self, **kwargs: Any) -> tuple[str, str]:
            if deadline_first:
                assert kills == [(456, owner.signal.SIGKILL)]
            return "compiled", ""

    monkeypatch.setattr(owner.threading, "Thread", Thread)
    monkeypatch.setattr(owner.subprocess, "Popen", lambda *a, **kw: Process())
    monkeypatch.setattr(owner.os, "getpgid", lambda pid: pid)
    monkeypatch.setattr(owner.os, "killpg", lambda pid, sig: kills.append((pid, sig)))

    def run() -> Any:
        if owner is _subprocess:
            return owner.run_process_group(["fake"], cwd=tmp_path, timeout=0)
        return owner.run_lean_probe(
            tmp_path / "Probe.lean", import_root=tmp_path, cwd=tmp_path, timeout_s=0
        )

    if deadline_first:
        with pytest.raises(owner.subprocess.TimeoutExpired):
            run()
    else:
        assert run().stdout == "compiled"
    for callback in callbacks:
        callback()
    if not deadline_first:
        assert kills == [], "normal completion must cancel the group-kill backstop"


@pytest.mark.parametrize("check", [False, True])
def test_deadline_before_communicate_is_still_a_timeout(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, check: bool
) -> None:
    import subprocess
    import sys
    import time

    start = _subprocess.threading.Thread.start

    def delayed_start(thread: Any) -> None:
        start(thread)
        time.sleep(0.2)

    monkeypatch.setattr(_subprocess.threading.Thread, "start", delayed_start)
    with pytest.raises(subprocess.TimeoutExpired):
        _subprocess.run_process_group(
            [sys.executable, "-S", "-c", "import time; time.sleep(2)"],
            cwd=tmp_path,
            timeout=0.05,
            check=check,
        )


_SHARED_OWNER = Path(_subprocess.__file__).resolve()


def _load_shared() -> str:
    return (
        "import importlib.util\n"
        f"spec=importlib.util.spec_from_file_location('owned_process_helper',{str(_SHARED_OWNER)!r})\n"
        "helper=importlib.util.module_from_spec(spec)\nspec.loader.exec_module(helper)\n"
    )


@pytest.mark.skipif(os.name != "posix", reason="private guard requires POSIX")
def test_private_guard_excludes_site_without_changing_target_startup(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        _subprocess,
        "_GUARD_PROGRAM",
        "import sys;assert 'site' not in sys.modules\n" + _subprocess._GUARD_PROGRAM,
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-c", "import sys;print('site' in sys.modules)"],
        cwd=tmp_path,
        timeout=3,
        check=True,
    )
    assert result.stdout == "True\n"


def _status(pid: int) -> str:
    return subprocess.run(
        ["/bin/ps", "-o", "stat=", "-p", str(pid)],
        capture_output=True,
        text=True,
        check=False,
        timeout=1,
    ).stdout.strip()


def _sleeper_tree(tmp_path: Path) -> tuple[str, Path, Path]:
    child = tmp_path / "tool.json"
    grand = tmp_path / "grandchild.json"
    grand_program = (
        "import os,time,json;from pathlib import Path;"
        f"Path({str(grand)!r}).write_text(json.dumps([os.getpid(),os.getpgid(0)]));"
        "time.sleep(30)"
    )
    program = (
        "import os,sys,subprocess,time,json\nfrom pathlib import Path\n"
        f"Path({str(child)!r}).write_text(json.dumps([os.getpid(),os.getpgid(0)]))\n"
        f"subprocess.Popen([sys.executable,'-S','-c',{grand_program!r}])\n"
        f"while not Path({str(grand)!r}).exists(): time.sleep(.005)\n"
        "print('nested tool started',flush=True)\ntime.sleep(30)\n"
    )
    return program, child, grand


def _registered_sleeper_tree(tmp_path: Path) -> tuple[str, tuple[Path, ...]]:
    program, child, grand = _sleeper_tree(tmp_path)
    intermediate = tmp_path / "intermediate.json"
    nested = (
        _load_shared()
        + "import os,sys,json\nfrom pathlib import Path\n"
        + f"Path({str(intermediate)!r}).write_text(json.dumps([os.getpid(),os.getpgid(0)]))\n"
        + "print('intermediate registered',flush=True)\n"
        + f"helper.run_process_group([sys.executable,'-S','-c',{program!r}],cwd={str(tmp_path)!r},timeout=None)\n"
    )
    return nested, (intermediate, child, grand)


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
@pytest.mark.parametrize("returncode", [0, 7])
def test_three_registered_levels_release_on_parent_completion_and_crash(
    tmp_path: Path, returncode: int
) -> None:
    program, records = _registered_sleeper_tree(tmp_path)
    outer = (
        _load_shared()
        + "import os,sys,threading,time\nfrom pathlib import Path\n"
        + f"def inner():\n helper.run_process_group([sys.executable,'-S','-c',{program!r}],cwd={str(tmp_path)!r},timeout=None)\n"
        + "threading.Thread(target=inner,daemon=True).start()\n"
        + f"deadline=time.monotonic()+3\nwhile not Path({str(records[-1])!r}).exists() and time.monotonic()<deadline: time.sleep(.01)\n"
        + f"assert Path({str(records[-1])!r}).exists(),'registered descendants never reached readiness'\n"
        + "print('three registered levels started',flush=True)\n"
        + ("os._exit(7)\n" if returncode else "")
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=5
    )
    assert result.returncode == returncode, result.stderr
    assert result.stdout == "three registered levels started\n"
    for record in records:
        assert record.is_file(), "registered descendant never reached readiness"
        pid, pgid = json.loads(record.read_text())
        assert pgid != os.getpgrp()
        state = _status(pid)
        assert not state or state.startswith("Z"), (
            f"registered descendant still live: {pid}"
        )


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
def test_three_level_inner_deadline_preserves_live_caller_and_sibling(
    tmp_path: Path,
) -> None:
    program, records = _registered_sleeper_tree(tmp_path)
    ready, release = tmp_path / "sibling-ready", tmp_path / "release-sibling"
    sibling = (
        "import time\nfrom pathlib import Path\n"
        + f"Path({str(ready)!r}).write_text('ready')\n"
        + f"deadline=time.monotonic()+6\nwhile not Path({str(release)!r}).exists() and time.monotonic()<deadline: time.sleep(.01)\n"
        + f"assert Path({str(release)!r}).exists(),'sibling was never released'\n"
        + "print('sibling completed',flush=True)\n"
    )
    outer = (
        _load_shared()
        + "import sys,subprocess,threading,time,json\nfrom pathlib import Path\n"
        + "results=[]\nerrors=[]\n"
        + "def independent():\n try:\n"
        + f"  results.append(helper.run_process_group([sys.executable,'-S','-c',{sibling!r}],cwd={str(tmp_path)!r},timeout=8,check=True))\n"
        + " except BaseException as error: errors.append(error)\n"
        + "worker=threading.Thread(target=independent,daemon=True)\nworker.start()\n"
        + f"deadline=time.monotonic()+3\nwhile not Path({str(ready)!r}).exists() and time.monotonic()<deadline: time.sleep(.01)\n"
        + f"assert Path({str(ready)!r}).exists(),'sibling never reached readiness'\n"
        + f"try:\n helper.run_process_group([sys.executable,'-S','-c',{program!r}],cwd={str(tmp_path)!r},timeout=2)\n"
        + "except subprocess.TimeoutExpired as error:\n"
        + " assert error.timeout==2 and b'intermediate registered' in error.output\n"
        + "else: raise AssertionError('inner deadline did not expire')\n"
        + f"for name in {[str(record) for record in records]!r}:\n"
        + " pid,_=json.loads(Path(name).read_text())\n"
        + " state=subprocess.run(['/bin/ps','-o','stat=','-p',str(pid)],capture_output=True,text=True,check=False,timeout=1).stdout.strip()\n"
        + " assert not state or state.startswith('Z'),'owned inner descendant still live'\n"
        + "assert worker.is_alive() and not results and not errors,'inner cleanup cancelled its sibling'\n"
        + f"Path({str(release)!r}).write_text('release')\n"
        + "worker.join(timeout=3)\n"
        + "assert not worker.is_alive() and not errors\n"
        + "assert len(results)==1 and results[0].stdout=='sibling completed\\n'\n"
        + "print('outer caller and sibling survived',flush=True)\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=12, check=True
    )
    assert result.stdout == "outer caller and sibling survived\n"


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
@pytest.mark.parametrize("crash", [False, True])
def test_cooperative_outer_deadline_and_crash_stop_nested_groups(
    tmp_path: Path, crash: bool
) -> None:
    program, child, grand = _sleeper_tree(tmp_path)
    outer = (
        _load_shared()
        + "import os,sys,threading,time\nfrom pathlib import Path\n"
        + f"def inner():\n helper.run_process_group([sys.executable,'-S','-c',{program!r}],cwd={str(tmp_path)!r},timeout=None)\n"
    )
    if crash:
        outer += (
            "threading.Thread(target=inner,daemon=True).start()\n"
            f"deadline=time.monotonic()+3\nwhile not Path({str(grand)!r}).exists() and time.monotonic()<deadline: time.sleep(.01)\n"
            f"assert Path({str(grand)!r}).exists(),'owned grandchildren never reached readiness'\n"
            "os._exit(7)\n"
        )
    else:
        outer += "inner()\n"
    unrelated = subprocess.Popen(
        [sys.executable, "-S", "-c", "import time;time.sleep(30)"],
        start_new_session=True,
    )
    try:
        started = time.monotonic()
        if crash:
            result = _subprocess.run_process_group(
                [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=4
            )
            assert result.returncode == 7
        else:
            with pytest.raises(subprocess.TimeoutExpired):
                _subprocess.run_process_group(
                    [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=3
                )
        call_budget = 4 if crash else 3
        assert time.monotonic() - started < call_budget + 2, (
            "nested pipes outlived bounded cleanup allowance"
        )
        for record in (child, grand):
            assert record.is_file(), "owned descendant never reached readiness"
            pid, pgid = json.loads(record.read_text())
            assert pgid != os.getpgrp(), "tool entered the calling test's group"
            state = _status(pid)
            assert not state or state.startswith("Z"), (
                f"owned descendant still live: {pid}"
            )
        assert unrelated.poll() is None, "cleanup touched an unrelated session"
    finally:
        unrelated.kill()
        unrelated.wait(timeout=2)


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
def test_inner_deadline_preserves_outer_caller_and_partial_streams(
    tmp_path: Path,
) -> None:
    program, child, grand = _sleeper_tree(tmp_path)
    outer = (
        _load_shared()
        + "import sys,subprocess\n"
        + f"try:\n helper.run_process_group([sys.executable,'-S','-c',{program!r}],cwd={str(tmp_path)!r},timeout=2.5)\n"
        + "except subprocess.TimeoutExpired as error:\n"
        + " assert error.timeout==2.5\n"
        + " assert b'nested tool started' in error.output\n"
        + " print('outer caller survived',flush=True)\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=6, check=True
    )
    assert result.stdout == "outer caller survived\n"
    for record in (child, grand):
        assert record.is_file(), "owned descendant never reached readiness"
        pid, _ = json.loads(record.read_text())
        state = _status(pid)
        assert not state or state.startswith("Z")


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
@pytest.mark.parametrize("capture", [False, True])
def test_nested_normal_completion_preserves_output_and_check(
    tmp_path: Path, capture: bool
) -> None:
    outer = (
        _load_shared()
        + "import sys,subprocess\n"
        + f"result=helper.run_process_group([sys.executable,'-S','-c','print(\"inner complete\")'],cwd={str(tmp_path)!r},timeout=3,capture={capture!r},check=True)\n"
        + (
            "assert result.stdout=='inner complete\\n'\nprint(result.stdout,end='')\n"
            if capture
            else "assert result.stdout is None\n"
        )
        + f"try:\n helper.run_process_group([sys.executable,'-S','-c','import sys;print(\"failed output\");sys.exit(6)'],cwd={str(tmp_path)!r},timeout=3,check=True)\n"
        + "except subprocess.CalledProcessError as error:\n"
        + " assert error.returncode==6 and error.stdout=='failed output\\n'\n"
        + " print('check preserved')\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=8, check=True
    )
    assert result.stdout == "inner complete\ncheck preserved\n"


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
def test_nested_timeout_preserves_raw_incomplete_utf8_and_crlf(tmp_path: Path) -> None:
    stdout = b"raw\r\n\xe2"
    stderr = b"error\r\n\xff"
    tool = (
        f"import os,time;os.write(1,{stdout!r});os.write(2,{stderr!r});time.sleep(30)"
    )
    outer = (
        _load_shared()
        + "import sys,subprocess\n"
        + f"try:\n helper.run_process_group([sys.executable,'-S','-c',{tool!r}],cwd={str(tmp_path)!r},timeout=2)\n"
        + "except subprocess.TimeoutExpired as error:\n"
        + " assert error.timeout==2\n"
        + f" assert error.output=={stdout!r} and error.stderr=={stderr!r}\n"
        + " print('raw timeout preserved')\n"
        + "else: raise AssertionError('missing timeout')\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=5, check=True
    )
    assert result.stdout == "raw timeout preserved\n"


@pytest.mark.skipif(os.name != "posix", reason="cooperative ownership is POSIX")
def test_nested_capture_larger_than_frame_bound(tmp_path: Path) -> None:
    size = 33 * 1024 * 1024
    tool = (
        "import os\nchunk=b'a'*65536\n"
        f"for _ in range({size // 65536}):\n"
        " data=chunk\n while data:\n  data=data[os.write(1,data):]\n"
    )
    outer = (
        _load_shared()
        + "import sys\n"
        + f"result=helper.run_process_group([sys.executable,'-S','-c',{tool!r}],cwd={str(tmp_path)!r},timeout=10,check=True)\n"
        + f"assert result.stdout=='a'*{size} and result.stderr==''\n"
        + "print('large capture preserved')\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=15
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == "large capture preserved\n"


@pytest.mark.skipif(os.name != "posix", reason="descriptor inheritance is POSIX")
def test_nested_command_inherits_callers_stdin(tmp_path: Path) -> None:
    tool = "import sys;print(sys.stdin.read(),end='')"
    outer = (
        _load_shared()
        + "import os,sys\n"
        + "original=os.dup(0)\nreader,writer=os.pipe()\n"
        + "os.write(writer,b'caller input\\r\\n');os.close(writer)\n"
        + "os.dup2(reader,0);os.close(reader)\ntry:\n"
        + f" result=helper.run_process_group([sys.executable,'-S','-c',{tool!r}],cwd={str(tmp_path)!r},timeout=3,check=True)\n"
        + " assert result.stdout=='caller input\\n'\n"
        + "finally:\n os.dup2(original,0);os.close(original)\n"
        + "print('caller stdin preserved')\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=6, check=True
    )
    assert result.stdout == "caller stdin preserved\n"


@pytest.mark.skipif(os.name != "posix", reason="descriptor inheritance is POSIX")
def test_nested_uncaptured_output_uses_callers_live_descriptor(tmp_path: Path) -> None:
    output, signal = tmp_path / "caller-output", tmp_path / "continue"
    tool = (
        "import time\nfrom pathlib import Path\nprint('live progress',flush=True)\n"
        + f"deadline=time.monotonic()+2\nwhile not Path({str(signal)!r}).exists() and time.monotonic()<deadline: time.sleep(.01)\n"
        + f"assert Path({str(signal)!r}).exists(),'output was deferred or misdirected'\n"
        + "print('finished',flush=True)\n"
    )
    outer = (
        _load_shared()
        + "import os,sys,threading,time\nfrom pathlib import Path\n"
        + "original=os.dup(1)\n"
        + f"sink=os.open({str(output)!r},os.O_CREAT|os.O_WRONLY,0o600)\nos.dup2(sink,1);os.close(sink)\n"
        + "def observe():\n deadline=time.monotonic()+2\n"
        + f" while 'live progress' not in Path({str(output)!r}).read_text() and time.monotonic()<deadline: time.sleep(.01)\n"
        + f" if 'live progress' in Path({str(output)!r}).read_text(): Path({str(signal)!r}).touch()\n"
        + "observer=threading.Thread(target=observe);observer.start()\ntry:\n"
        + f" result=helper.run_process_group([sys.executable,'-S','-c',{tool!r}],cwd={str(tmp_path)!r},timeout=3,capture=False,check=True)\n"
        + " assert result.stdout is None and result.stderr is None\n"
        + "finally:\n os.dup2(original,1);os.close(original);observer.join()\n"
        + f"assert Path({str(output)!r}).read_text()=='live progress\\nfinished\\n'\n"
        + "print('live caller output preserved')\n"
    )
    result = _subprocess.run_process_group(
        [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=6, check=True
    )
    assert result.stdout == "live caller output preserved\n"


@pytest.mark.skipif(os.name != "posix", reason="private broker requires POSIX")
@pytest.mark.parametrize("lease", ["partial", "stale"])
def test_invalid_lease_refuses_fallback_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, lease: str
) -> None:
    marker = tmp_path / "must-not-launch"
    monkeypatch.setenv(_subprocess._SOCKET_ENV, str(tmp_path / "missing.sock"))
    if lease == "partial":
        monkeypatch.delenv(_subprocess._TOKEN_ENV, raising=False)
    else:
        monkeypatch.setenv(_subprocess._TOKEN_ENV, "synthetic-invalid-capability")
    with pytest.raises(OSError):
        _subprocess.run_process_group(
            [
                sys.executable,
                "-c",
                f"from pathlib import Path;Path({str(marker)!r}).touch()",
            ],
            cwd=tmp_path,
            timeout=1,
        )
    assert not marker.exists()


@pytest.mark.skipif(os.name != "posix", reason="private broker requires POSIX")
def test_broker_rejects_unauthenticated_and_pid_requests(tmp_path: Path) -> None:
    marker = tmp_path / "must-not-launch"
    broker = _subprocess._Broker()
    try:
        for forged_pid in (False, True):
            with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as channel:
                channel.connect(broker.address)
                request = {
                    "token": broker.token if forged_pid else "synthetic-wrong-token",
                    "command": [
                        sys.executable,
                        "-c",
                        f"from pathlib import Path;Path({str(marker)!r}).touch()",
                    ],
                    "cwd": str(tmp_path),
                    "env": {},
                    "timeout": 1,
                    "capture": True,
                }
                if forged_pid:
                    request["pid"] = os.getpid()
                _subprocess._send_frame(channel, request)
                assert _subprocess._read_frame(channel)["kind"] == "error"
        assert not marker.exists() and not broker.groups
    finally:
        broker.close()


@pytest.mark.skipif(os.name != "posix", reason="detached sessions require POSIX")
def test_unregistered_detached_pipe_has_bounded_drain(tmp_path: Path) -> None:
    # This raw detached child is explicitly outside cooperative cleanup. It has
    # its own short lifetime; the test never kills a PID learned from a census.
    record = tmp_path / "raw.json"
    detached = (
        "import os,time,json;from pathlib import Path;"
        f"Path({str(record)!r}).write_text(json.dumps([os.getpid(),os.getpgid(0)]));"
        "time.sleep(5)"
    )
    outer = (
        "import subprocess,sys,time\n"
        f"subprocess.Popen([sys.executable,'-S','-c',{detached!r}],start_new_session=True)\n"
        f"while not __import__('pathlib').Path({str(record)!r}).exists(): time.sleep(.005)\n"
        "print('partial raw output',flush=True)\ntime.sleep(30)\n"
    )
    started = time.monotonic()
    with pytest.raises(subprocess.TimeoutExpired) as error:
        _subprocess.run_process_group(
            [sys.executable, "-S", "-c", outer], cwd=tmp_path, timeout=2
        )
    assert time.monotonic() - started < 4
    assert error.value.timeout == 2
    assert b"partial raw output" in error.value.output
    assert record.is_file(), "detached pipe holder never reached readiness"
    pid, _ = json.loads(record.read_text())
    assert _status(pid) and not _status(pid).startswith("Z"), (
        "raw escape was falsely claimed killed"
    )
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline:
        state = _status(pid)
        if not state or state.startswith("Z"):
            break
        time.sleep(0.02)
    else:
        pytest.fail("test-owned short detached child did not finish")
