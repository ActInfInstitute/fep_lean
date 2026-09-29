#!/usr/bin/env python3
"""Content-keyed reuse of the worktree-local ``lean/.lake`` state for repeat verifies.

Slice-local tooling (roster-excluded by design): validates the
toolchain/Mathlib/manifest pin triple before any Lake invocation, mirroring the
t-0058 guarded setup, then restores, exercises, and refreshes a content-keyed
snapshot of ``lean/.lake``. The store holds only derived Lake build outputs;
custody receipts are never cached.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

KEY_PREFIX = "leanlake-v1-"
PIN_FILENAMES = ("lean-toolchain", "lakefile.lean", "lake-manifest.json")
DEFAULT_STORE = Path("~/.cache/fep-lean/lean-build")
# The pinned Mathlib cache CLI returns zero for HTTP 404 misses. Upstream
# setup (src/fep_lean/cli.py) fails closed on its explicit terminal warning
# only -- not on incidental "404" tokens in retried-and-recovered attempt
# logs, which would hard-fail healthy runs.
CACHE_MISS_VERDICT = "some files were not found in the cache"
TOOLCHAIN_PIN_RE = re.compile(r"^leanprover/lean4:v(?P<version>\d+\.\d+\.\d+)$")
MATHLIB_TAG_RE = re.compile(r"^v(?P<version>\d+\.\d+\.\d+)$")
MATHLIB_REQUIRE_RE = re.compile(
    r'mathlib4\.git"\s*@\s*"(?P<tag>v\d+\.\d+\.\d+)"'
)
REPAIR = (
    "Inspect git diff -- lean/lean-toolchain lean/lakefile.lean "
    "lean/lake-manifest.json uv.lock; preserve intentional edits, then restore "
    "these files together from the intended reviewed commit and rerun. "
    "Do not run lake update to repair ordinary setup."
)
USAGE = (
    "usage: lean_cache.py [--no-cache] [--skip-build] [--store DIR] "
    "[--key-print] -- COMMAND [ARGS...]"
)


class PinError(Exception):
    """Raised when the pin triple or snapshot validation fails."""


class Store:
    """Directory holding one content-keyed ``lean/.lake`` snapshot per key."""

    def __init__(self, root: Path) -> None:
        self.root = root

    def snapshot(self, key: str) -> Path:
        return self.root / key / "lean-lake"

    def staging(self, key: str) -> Path:
        return self.root / key / ".tmp-lean-lake"


@dataclass
class ParsedArgs:
    no_cache: bool
    key_print: bool
    skip_build: bool
    store: str | None
    command: list[str]


class UsageError(Exception):
    """Raised for malformed arguments; exits with usage, status 2."""


def parse_args(argv: list[str]) -> ParsedArgs:
    """Parse CLI flags; the ``--`` separator is mandatory before the command."""
    no_cache = False
    key_print = False
    skip_build = False
    store: str | None = None
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--no-cache":
            no_cache = True
        elif arg == "--key-print":
            key_print = True
        elif arg == "--skip-build":
            skip_build = True
        elif arg == "--store":
            if index + 1 >= len(argv):
                raise UsageError("--store requires a directory argument")
            store = argv[index + 1]
            index += 1
        elif arg == "--":
            command = argv[index + 1 :]
            if not key_print and not command:
                raise UsageError("no command after --")
            return ParsedArgs(
                no_cache=no_cache,
                key_print=key_print,
                skip_build=skip_build,
                store=store,
                command=command,
            )
        else:
            raise UsageError(f"unknown argument: {arg}")
        index += 1
    if not key_print:
        raise UsageError("missing mandatory -- separator before COMMAND")
    return ParsedArgs(
        no_cache=no_cache,
        key_print=key_print,
        skip_build=skip_build,
        store=store,
        command=[],
    )


def read_pin_files(lean_dir: Path, root: Path) -> dict[Path, bytes]:
    """Read the three Lean pin files plus uv.lock, raising on any absence."""
    paths = [lean_dir / name for name in PIN_FILENAMES] + [root / "uv.lock"]
    snapshot: dict[Path, bytes] = {}
    for path in paths:
        if not path.is_file():
            raise PinError(f"missing pin file: {path}")
        snapshot[path] = path.read_bytes()
    return snapshot


def validate_pins(snapshot: dict[Path, bytes]) -> str:
    """Validate the toolchain/Mathlib/manifest pins and derive the cache key.

    Mirrors t-0058's guarded setup: toolchain semver, lakefile Mathlib tag, and
    manifest package list must agree before any Lake invocation.
    """
    lean_dir = next(iter(snapshot)).parent
    toolchain_path = lean_dir / "lean-toolchain"
    toolchain = snapshot[toolchain_path].decode("utf-8").strip()
    if "\n" in toolchain or TOOLCHAIN_PIN_RE.fullmatch(toolchain) is None:
        raise PinError(f"lean-toolchain is not a single canonical pin: {toolchain!r}")
    match = TOOLCHAIN_PIN_RE.fullmatch(toolchain)
    assert match is not None  # guarded above
    pinned_semver = match.group("version")
    lakefile = snapshot[lean_dir / "lakefile.lean"].decode("utf-8")
    tags = [match.group("tag") for match in MATHLIB_REQUIRE_RE.finditer(lakefile)]
    if len(tags) != 1 or MATHLIB_TAG_RE.fullmatch(tags[0]) is None:
        raise PinError("lakefile.lean does not pin exactly one Mathlib release tag")
    tag = tags[0]
    if tag != "v" + pinned_semver:
        raise PinError(f"toolchain pin {pinned_semver} does not match Mathlib tag {tag}")
    try:
        manifest = json.loads(snapshot[lean_dir / "lake-manifest.json"].decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise PinError(f"lake-manifest.json is not valid JSON: {exc}") from exc
    packages = manifest.get("packages") if isinstance(manifest, dict) else None
    if not isinstance(packages, list) or not packages:
        raise PinError("manifest packages is not a nonempty list")
    if manifest.get("packagesDir") != ".lake/packages":
        raise PinError("manifest packagesDir is not .lake/packages")
    for package in packages:
        if (
            not isinstance(package, dict)
            or package.get("type") != "git"
            or not re.fullmatch(r"[0-9a-f]{40}", str(package.get("rev", "")))
        ):
            raise PinError(f"manifest package is not a pinned git revision: {package!r}")
    mathlib = [package for package in packages if package.get("name") == "mathlib"]
    if len(mathlib) != 1 or mathlib[0].get("inputRev") != tag:
        raise PinError(
            f"manifest Mathlib inputRev does not match lakefile/toolchain tag {tag}"
        )
    digest = hashlib.sha256()
    for name in PIN_FILENAMES:
        digest.update(snapshot[lean_dir / name])
    return KEY_PREFIX + digest.hexdigest()


def check_snapshots(snapshot: dict[Path, bytes]) -> None:
    """Re-validate pin-file bytes; any drift fails closed (lock preservation)."""
    for path, original in snapshot.items():
        if not path.is_file() or path.read_bytes() != original:
            raise PinError(f"pin drift: {path}. {REPAIR}")


def clone_tree(src: Path, dst: Path) -> None:
    """Copy a tree, preferring cheap APFS clones on darwin; never clobbering."""
    command = (
        ["cp", "-cR", str(src), str(dst)]
        if sys.platform == "darwin"
        else ["cp", "-aR", str(src), str(dst)]
    )
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode == 0:
        return
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, symlinks=True)


def restore(snapshot_dir: Path, lean_dir: Path) -> None:
    """Restore lean/.lake from the store snapshot only when it is absent."""
    target = lean_dir / ".lake"
    if target.exists():
        print(f"cache: {target} already present; kept existing (no clobber)")
        return
    clone_tree(snapshot_dir, target)
    print(f"cache: restored {target} from {snapshot_dir}")


def lake_env(elan_home: Path) -> dict[str, str]:
    env = dict(os.environ)
    env["ELAN_HOME"] = str(elan_home)
    env["PATH"] = str(elan_home / "bin") + os.pathsep + env.get("PATH", "")
    return env


def run_lake(
    command: list[str], lean_dir: Path, env: dict[str, str], snapshot: dict[Path, bytes]
) -> subprocess.CompletedProcess[str]:
    """Run one guarded Lake invocation in lean/, checking pins before and after."""
    check_snapshots(snapshot)
    result = subprocess.run(
        command, cwd=lean_dir, env=env, capture_output=True, text=True, check=False
    )
    check_snapshots(snapshot)
    return result


def require_lean_version(
    result: subprocess.CompletedProcess[str], pinned_semver: str
) -> None:
    output = (result.stdout + result.stderr) if result.returncode else result.stdout
    if result.returncode != 0 or pinned_semver not in output:
        tail = (result.stdout + result.stderr).strip()[-400:]
        raise PinError(
            f"lake --wfail env lean --version did not report the pinned Lean "
            f"{pinned_semver}; output tail: {tail}"
        )


def run_cache_get(
    result: subprocess.CompletedProcess[str],
) -> None:
    """Fail closed on a nonzero exit or the terminal incomplete-cache verdict."""
    combined = (result.stdout + result.stderr).strip()
    if result.returncode != 0 or CACHE_MISS_VERDICT in combined:
        print(combined[-2000:], file=sys.stderr)
        verdict = (
            "failed" if result.returncode else "reported an incomplete Mathlib cache"
        )
        raise PinError(
            f"`lake --wfail exe cache get` {verdict}; fail closed rather than "
            "starting a from-source rebuild"
        )


def _process_command(pid: str) -> str:
    """Full command line of a pid, empty when it cannot be read."""
    listed = subprocess.run(
        ["/bin/ps", "-ww", "-o", "command=", "-p", pid],
        capture_output=True,
        check=False,
    )
    return listed.stdout.decode("utf-8", "replace").strip()


def _process_cwd(pid: str) -> str | None:
    """Current working directory of a pid, None when it cannot be resolved."""
    listed = subprocess.run(
        ["/usr/sbin/lsof", "-a", "-w", "-p", pid, "-d", "cwd", "-Fn"],
        capture_output=True,
        check=False,
    )
    for line in listed.stdout.decode("utf-8", "replace").splitlines():
        if line.startswith("n/"):
            return line[1:]
    return None


def check_no_running_lake(lean_dir: Path) -> None:
    """Refuse to mutate this worktree's .lake while its own Lake processes run.

    Concurrent Lake invocations in ONE worktree race the same build state;
    sibling worktrees are independent and must not block this one — even
    though their ``lake`` argv[0] is the same elan binary. A process counts
    as this worktree's when its command line references this lean/ directory
    (``lake env lean <here>/lean/FepSketches/...``) or, for bare invocations
    with no path argument, when its cwd is this lean/ directory.
    """
    prefix = str(lean_dir)
    for name in ("lake", "lean"):
        result = subprocess.run(
            ["/usr/bin/pgrep", "-x", name], capture_output=True, check=False
        )
        if result.returncode != 0:
            continue
        pids = result.stdout.decode().split()
        mine: list[str] = []
        for pid in pids:
            if prefix in _process_command(pid):
                mine.append(pid)
                continue
            cwd = _process_cwd(pid)
            if cwd is not None and cwd == str(lean_dir):
                mine.append(pid)
        if mine:
            raise PinError(
                f"another {name} process for THIS worktree is running "
                f"(pid(s) {' '.join(mine)}); concurrent Lake invocations in "
                "one worktree race .lake state — wait for it to finish, "
                "then rerun"
            )


def run_build_aggregate(
    lean_dir: Path, env: dict[str, str], snapshot: dict[Path, bytes]
) -> None:
    """Build the FepSketches aggregate before the wrapped command (CI mirror).

    CI's lean lane always runs 'Compile warning-free aggregate' before the
    receipt verify; ``lake env lean`` resolves ``FepSketches.*`` imports only
    through the built library, so a verify-class command without this step
    fails closed on every topic that imports the aggregate. Incremental:
    near-zero when the restored snapshot is already current.
    """
    result = run_lake(
        ["lake", "--wfail", "build", "FepSketches"], lean_dir, env, snapshot
    )
    if result.returncode != 0:
        combined = ((result.stdout or "") + (result.stderr or "")).strip()
        print(combined[-2000:], file=sys.stderr)
        raise PinError("`lake --wfail build FepSketches` failed; not starting the wrapped command")


def fail(message: str) -> int:
    print(f"lean_cache failed: {message}. {REPAIR}", file=sys.stderr)
    return 1


def main(argv: list[str]) -> int:
    root = Path(__file__).resolve().parents[2]
    lean_dir = root / "lean"
    try:
        args = parse_args(argv)
    except UsageError as exc:
        print(f"error: {exc}\n{USAGE}", file=sys.stderr)
        return 2
    try:
        snapshot = read_pin_files(lean_dir, root)
        key = validate_pins(snapshot)
    except (OSError, PinError) as exc:
        return fail(str(exc))
    if args.key_print:
        print(key)
        return 0
    no_cache = args.no_cache
    store_root = os.environ.get("FEP_LEAN_CACHE_DIR")
    store = Path(args.store or store_root or str(DEFAULT_STORE)).expanduser()
    store_snapshot = Store(store).snapshot(key)
    env = lake_env(Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan"))))
    try:
        check_no_running_lake(lean_dir)
        if not no_cache:
            if store_snapshot.exists():
                restore(store_snapshot, lean_dir)
            else:
                print(f"cache: miss (no snapshot at {store_snapshot}); continuing")
        pinned_semver = TOOLCHAIN_PIN_RE.fullmatch(
            snapshot[lean_dir / "lean-toolchain"].decode("utf-8").strip()
        ).group("version")  # type: ignore[union-attr]
        require_lean_version(
            run_lake(
                ["lake", "--wfail", "env", "lean", "--version"],
                lean_dir,
                env,
                snapshot,
            ),
            pinned_semver,
        )
        run_cache_get(
            run_lake(["lake", "--wfail", "exe", "cache", "get"], lean_dir, env, snapshot)
        )
        if not args.skip_build:
            run_build_aggregate(lean_dir, env, snapshot)
        command = list(args.command)
        if not command:
            return 0
        check_snapshots(snapshot)
        exit_code = subprocess.run(command, cwd=root, check=False).returncode
        check_snapshots(snapshot)
        if exit_code != 0:
            return exit_code
        if no_cache:
            print("cache: --no-cache; store not refreshed")
            return 0
        staging = Store(store).staging(key)
        staging.parent.mkdir(parents=True, exist_ok=True)
        if staging.exists():
            shutil.rmtree(staging)
        clone_tree(lean_dir / ".lake", staging)
        if store_snapshot.exists():
            shutil.rmtree(store_snapshot)
        staging.rename(store_snapshot)
        print(f"cache: refreshed store snapshot {store_snapshot}")
        return 0
    except (OSError, subprocess.SubprocessError, PinError) as exc:
        return fail(str(exc))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
