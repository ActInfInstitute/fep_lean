"""Retain the actual final-source native command and both source brackets."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import time

from fep_lean.output.evidence import validate_native_lean_receipt
from fep_lean.output.provenance import config_owner_paths, source_owner_paths

ROOT = Path.cwd().resolve()
HERE = Path(__file__).resolve().parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot() -> dict[str, str]:
    paths = (*source_owner_paths(ROOT), *config_owner_paths(ROOT))
    return {str(p.relative_to(ROOT)): digest(p) for p in sorted(paths)}


def save(name: str, value: object) -> None:
    (HERE / name).write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


before = snapshot()
save("source-before.json", before)
shutil.copyfile(ROOT / "output/native-verification.json", HERE / "prior-native-verification.json")
command = ["uv", "run", "--locked", "fep-lean", "verify", "--receipt", "output/native-verification.json", "--fail-on-warnings"]
environment = dict(os.environ)
environment.pop("FEP_LEAN_MAX_TOPICS", None)
environment["PYTHONDONTWRITEBYTECODE"] = "1"
started = time.monotonic()
with (HERE / "native.stdout.txt").open("wb") as stdout, (HERE / "native.stderr.txt").open("wb") as stderr:
    result = subprocess.run(command, env=environment, cwd=ROOT, stdout=stdout, stderr=stderr, check=False, timeout=3600)
elapsed = time.monotonic() - started
after = snapshot()
save("source-after.json", after)
shutil.copyfile(ROOT / "output/native-verification.json", HERE / "native-verification.json")
validation = validate_native_lean_receipt(ROOT / "output/native-verification.json", project_root=ROOT)
receipt = {
    "schema_version": 1,
    "kind": "actual-final-source-native-capture",
    "argv": command,
    "exit_code": result.returncode,
    "elapsed_seconds": elapsed,
    "source_count": len(before),
    "sources_unchanged": before == after,
    "validation": validation,
    "accepted": result.returncode == 0 and before == after and validation["native_claim_ready"],
    "artifacts": {p.name: digest(p) for p in sorted(HERE.iterdir()) if p.is_file() and p.name != "receipt.json"},
}
save("receipt.json", receipt)
print(json.dumps(receipt, indent=2, sort_keys=True))
raise SystemExit(0 if receipt["accepted"] else 1)
