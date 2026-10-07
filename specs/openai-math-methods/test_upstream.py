"""Negative controls for an optional, static upstream reference adapter."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import tracemalloc
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location(
    "math_upstream", Path(__file__).with_name("upstream.py")
)
assert SPEC and SPEC.loader
upstream = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(upstream)


def write_lock(tmp_path: Path, lock: dict) -> Path:
    path = tmp_path / "lock.json"
    path.write_text(json.dumps(lock), encoding="utf-8")
    return path


@pytest.mark.parametrize("path", ["../escape", "/absolute", "a//b", "a/./b", "a\\b"])
def test_unsafe_paths_rejected(tmp_path: Path, path: str) -> None:
    lock = upstream.load_lock()
    lock["reviewed_files"][0]["path"] = path
    with pytest.raises(ValueError, match="unsafe"):
        upstream.load_lock(write_lock(tmp_path, lock))


def test_duplicate_file_or_json_key_rejected(tmp_path: Path) -> None:
    lock = upstream.load_lock()
    lock["reviewed_files"].append(lock["reviewed_files"][0])
    with pytest.raises(ValueError, match="duplicate"):
        upstream.load_lock(write_lock(tmp_path, lock))
    path = tmp_path / "duplicate.json"
    path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate JSON"):
        upstream.load_lock(path)


def test_wrong_repository_and_unpinned_url_rejected(tmp_path: Path) -> None:
    lock = upstream.load_lock()
    lock["repository"] = "https://example.org/math"
    with pytest.raises(ValueError, match="repository"):
        upstream.load_lock(write_lock(tmp_path, lock))
    lock = upstream.load_lock()
    lock["reviewed_files"][0]["url"] = lock["reviewed_files"][0]["url"].replace(
        lock["commit"], "main"
    )
    with pytest.raises(ValueError, match="exact reviewed"):
        upstream.load_lock(write_lock(tmp_path, lock))


def test_real_checkout_identity_and_byte_controls(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    def git(*args: str) -> str:
        return subprocess.run(
            ["git", "-C", str(tmp_path), *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
            env=upstream.git_environment(),
        ).stdout.strip()

    git("init", "--quiet")
    source = tmp_path / "README.md"
    blob = b"public reference fixture\n"
    source.write_bytes(blob)
    git("add", "README.md")
    git(
        "-c",
        "user.name=Reference Test",
        "-c",
        "user.email=test@example.invalid",
        "-c",
        "commit.gpgsign=false",
        "-c",
        "core.hooksPath=/dev/null",
        "commit",
        "--quiet",
        "-m",
        "fixture",
    )
    lock = upstream.load_lock()
    lock["commit"] = git("rev-parse", "HEAD")
    lock["reviewed_files"] = [
        {
            "path": "README.md",
            "bytes": len(blob),
            "sha256": hashlib.sha256(blob).hexdigest(),
            "git_blob_sha1": hashlib.sha1(
                b"blob " + str(len(blob)).encode() + b"\0" + blob
            ).hexdigest(),
            "url": f"{upstream.REPOSITORY}/blob/{lock['commit']}/README.md",
        }
    ]
    assert upstream.compare_checkout(lock, tmp_path) == ()
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    subprocess.run(
        ["git", "-C", str(foreign), "init", "--quiet"],
        check=True,
        capture_output=True,
        env=upstream.git_environment(),
        timeout=10,
    )
    monkeypatch.setenv("GIT_DIR", str(foreign / ".git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(foreign))
    monkeypatch.setenv("GIT_INDEX_FILE", str(foreign / "injected-index"))
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_CONFIG_KEY_0", "core.worktree")
    monkeypatch.setenv("GIT_CONFIG_VALUE_0", str(foreign))
    assert upstream.compare_checkout(lock, tmp_path) == ()
    assert git("rev-parse", "HEAD") == lock["commit"]
    assert os.environ["GIT_DIR"] == str(foreign / ".git")
    assert not (foreign / "injected-index").exists()
    with source.open("wb") as stream:
        stream.truncate(16 * 1024 * 1024)
    tracemalloc.start()
    try:
        assert upstream.compare_checkout(lock, tmp_path) == (
            "reviewed source drift: README.md",
        )
        peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()
    assert peak < 1_000_000, (
        "a small pinned file must not allocate its oversized replacement"
    )
    source.write_bytes(blob + b"mutation")
    assert upstream.compare_checkout(lock, tmp_path) == (
        "reviewed source drift: README.md",
    )
    source.unlink()
    source.symlink_to(tmp_path / "lock.json")
    assert upstream.compare_checkout(lock, tmp_path) == (
        "symlink in reviewed path: README.md",
    )
    lock["commit"] = "0" * 40
    assert "upstream HEAD differs" in upstream.compare_checkout(lock, tmp_path)[0]


def test_blob_identity_and_byte_limit_rejected(tmp_path: Path) -> None:
    lock = upstream.load_lock()
    lock["reviewed_files"][0]["git_blob_sha1"] = "not-a-pin"
    with pytest.raises(ValueError, match="blob identity"):
        upstream.load_lock(write_lock(tmp_path, lock))
    lock = upstream.load_lock()
    lock["reviewed_files"][0]["bytes"] = upstream.MAX_REVIEWED_FILE_BYTES + 1
    with pytest.raises(ValueError, match="size"):
        upstream.load_lock(write_lock(tmp_path, lock))


def test_check_is_read_only_and_explicit_about_unchecked_bytes(
    capsys: pytest.CaptureFixture[str],
) -> None:
    original = upstream.LOCK.read_bytes()
    assert upstream.main(["--check"]) == 0
    assert upstream.LOCK.read_bytes() == original
    output = capsys.readouterr().out
    assert "upstream bytes not rechecked" in output
    assert "no proof or execution acceptance" in output
