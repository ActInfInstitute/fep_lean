"""Retain the actual focused metadata-copy acceptance and source brackets."""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

from fep_lean.output.provenance import config_owner_paths, source_owner_paths

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
TESTS = ("tests/test_manuscript_rendering.py", "tests/test_release_bundle.py")
GUARDED = sorted(
    {*source_owner_paths(ROOT), *config_owner_paths(ROOT), *(ROOT / p for p in TESTS)}
)


def snapshot() -> dict[str, str]:
    return {
        p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in GUARDED
    }


def write(name: str, value: object) -> None:
    (OUT / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


before = snapshot()
write("sources-before.json", before)
commands = (
    (
        "pytest",
        [
            "uv", "run", "--locked", "--no-sync", "pytest", *TESTS,
            "-q", "--no-cov", "-m", "not serial_lean",
            f"--junitxml={OUT / 'pytest.xml'}", "-o", "addopts=",
        ],
    ),
    ("ruff", ["uv", "run", "--locked", "--no-sync", "ruff", "check", "src", "tests", "scripts", "docs"]),
    ("format", ["uv", "run", "--locked", "--no-sync", "ruff", "format", "--check", "src", "tests", "scripts", "docs"]),
    ("mypy", ["uv", "run", "--locked", "--no-sync", "mypy", "src"]),
)
records = []
for name, argv in commands:
    started = time.monotonic()
    with (OUT / f"{name}.stdout.log").open("wb") as stdout, (OUT / f"{name}.stderr.log").open("wb") as stderr:
        result = subprocess.run(argv, cwd=ROOT, stdout=stdout, stderr=stderr, check=False)
    record = {"name": name, "argv": argv, "exit_code": result.returncode, "elapsed_s": time.monotonic() - started}
    records.append(record)
    write("commands.json", records)
    print(json.dumps(record), flush=True)
after = snapshot()
write("sources-after.json", after)
write("receipt.json", {
    "kind": "focused-render-metadata-copy-acceptance",
    "accepted": all(r["exit_code"] == 0 for r in records) and before == after,
    "source_stable": before == after,
    "guarded_files": len(before),
    "commands": records,
    "artifacts": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "receipt.json"},
    "scope": "Actual focused nonserial Python controls and whole-tree type/style checks; no native, provider, render worker, archive publication or scientific sampling acceptance.",
})
print((OUT / "receipt.json").read_text(), flush=True)
