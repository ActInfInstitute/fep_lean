"""Validate the reference lock or compare a separately acquired upstream checkout.

This module never acquires dependencies or executes upstream code. Matching the
selected bytes is source inspection evidence, not a build or custody receipt.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

LOCK = Path(__file__).with_name("upstream.lock.json")
REPOSITORY = "https://github.com/openai/math"
MAX_REVIEWED_FILE_BYTES = 8 * 1024 * 1024
GIT_SELECTION_VARIABLES = frozenset(
    {
        "GIT_ALTERNATE_OBJECT_DIRECTORIES",
        "GIT_CONFIG",
        "GIT_CONFIG_PARAMETERS",
        "GIT_CONFIG_COUNT",
        "GIT_OBJECT_DIRECTORY",
        "GIT_DIR",
        "GIT_WORK_TREE",
        "GIT_IMPLICIT_WORK_TREE",
        "GIT_GRAFT_FILE",
        "GIT_INDEX_FILE",
        "GIT_NO_REPLACE_OBJECTS",
        "GIT_REPLACE_REF_BASE",
        "GIT_PREFIX",
        "GIT_SHALLOW_FILE",
        "GIT_COMMON_DIR",
        "GIT_NAMESPACE",
        "GIT_QUARANTINE_PATH",
        "GIT_CEILING_DIRECTORIES",
        "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    }
)


def git_environment() -> dict[str, str]:
    """Keep parent settings while selecting only the requested repository."""
    return {
        key: value
        for key, value in os.environ.items()
        if key not in GIT_SELECTION_VARIABLES
        and not key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
    }


def load_lock(path: Path = LOCK) -> dict[str, Any]:
    """Reject malformed pins, paths, duplicates, or noncanonical destinations."""

    def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    lock = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    if not isinstance(lock, dict) or lock.get("schema_version") != 1:
        raise ValueError("unsupported upstream reference schema")
    if lock.get("repository") != REPOSITORY:
        raise ValueError("unexpected upstream repository")
    commit = lock.get("commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("commit must be an exact Git SHA-1")
    if lock.get("integration") != "pinned-reference-corpus":
        raise ValueError("reference lock cannot authorize runtime integration")
    files = lock.get("reviewed_files")
    if not isinstance(files, list) or not files:
        raise ValueError("reviewed files must be nonempty")
    seen: set[str] = set()
    for entry in files:
        if not isinstance(entry, dict):
            raise TypeError("file record must be an object")
        name = entry.get("path")
        if not isinstance(name, str) or not name:
            raise ValueError("file record needs a relative path")
        parts = name.split("/")
        if (
            PurePosixPath(name).is_absolute()
            or "\\" in name
            or any(part in {"", ".", ".."} for part in parts)
            or name in seen
        ):
            raise ValueError(f"unsafe or duplicate reviewed path: {name}")
        seen.add(name)
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError(f"invalid digest: {name}")
        size = entry.get("bytes")
        if type(size) is not int or not 0 <= size <= MAX_REVIEWED_FILE_BYTES:
            raise ValueError(f"invalid size: {name}")
        blob_id = entry.get("git_blob_sha1")
        if not isinstance(blob_id, str) or not re.fullmatch(r"[0-9a-f]{40}", blob_id):
            raise ValueError(f"invalid commit-tree blob identity: {name}")
        if entry.get("url") != f"{REPOSITORY}/blob/{commit}/{name}":
            raise ValueError(f"URL does not bind the exact reviewed source: {name}")
    return lock


def compare_checkout(lock: dict[str, Any], upstream_root: Path) -> tuple[str, ...]:
    """Check Git identity and selected regular-file bytes without running Lean.

    This is a bounded static check. It neither attests the unreviewed tree nor
    guarantees a snapshot remains unchanged after this function returns.
    """
    root = upstream_root.resolve(strict=True)
    if not root.is_dir():
        raise ValueError("upstream root must be a directory")
    result = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
        timeout=10,
        env=git_environment(),
    )
    identity = result.stdout.splitlines()
    if len(identity) != 2 or Path(identity[0]).resolve() != root:
        raise ValueError("upstream root must be the Git checkout root")
    failures = []
    if identity[1] != lock["commit"]:
        failures.append("upstream HEAD differs from the reviewed commit")
    for entry in lock["reviewed_files"]:
        target = root
        for part in entry["path"].split("/"):
            target /= part
            if target.is_symlink():
                failures.append(f"symlink in reviewed path: {entry['path']}")
                break
        else:
            if not target.is_file():
                failures.append(f"missing regular reviewed file: {entry['path']}")
                continue
            with target.open("rb") as stream:
                blob = stream.read(entry["bytes"] + 1)
            git_blob = hashlib.sha1(
                b"blob " + str(len(blob)).encode("ascii") + b"\0" + blob
            ).hexdigest()
            if (
                len(blob) != entry["bytes"]
                or hashlib.sha256(blob).hexdigest() != entry["sha256"]
                or git_blob != entry["git_blob_sha1"]
            ):
                failures.append(f"reviewed source drift: {entry['path']}")
    return tuple(failures)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", required=True)
    parser.add_argument("--upstream-root", type=Path)
    args = parser.parse_args(argv)
    try:
        lock = load_lock()
        failures = (
            compare_checkout(lock, args.upstream_root)
            if args.upstream_root is not None
            else ()
        )
    except (TypeError, ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}")
        return 1
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    evidence = (
        "selected checkout bytes match"
        if args.upstream_root is not None
        else "lock structure valid; upstream bytes not rechecked"
    )
    print(f"OK: {lock['commit']}; {evidence}; no proof or execution acceptance")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
