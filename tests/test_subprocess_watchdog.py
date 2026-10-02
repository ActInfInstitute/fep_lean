"""The timeout backstop kills live probes and cancels after normal completion."""

from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from fep_lean.verification import _subprocess
from tests._support import lean_runner


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
