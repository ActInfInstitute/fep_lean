#!/usr/bin/env python3
"""Check the release gate: one version/date, a changelog section, green hosted CI.

The gate is deliberately short (see release.md). Research and evidence
lanes (H3 study, capture custody, installed-wheel matrix, provider runs) are
reported in release notes; they do not block a versioned release.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = "ci.yml"
#: Jobs whose success the release table in release.md promises. A dispatch
#: run may skip Lean or render and still conclude ``success``, so the run
#: conclusion alone is not enough.
REQUIRED_JOBS = ("python", "lean", "render-deps", "render")
DISTRIBUTION_PREFIX = "distribution ("


@dataclass(frozen=True)
class Release:
    version: str
    date: str

    @property
    def tag(self) -> str:
        return f"v{self.version}"


def _text(root: Path, relative: str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def _assignment(root: Path, relative: str, name: str) -> str | None:
    match = re.search(rf'(?m)^{name}\s*=\s*"([^"]+)"\s*$', _text(root, relative))
    return match.group(1) if match else None


def _yaml(root: Path, relative: str) -> dict[str, Any]:
    data = yaml.safe_load(_text(root, relative))
    return data if isinstance(data, dict) else {}


def _nested(data: dict[str, Any], *keys: str) -> str | None:
    value: Any = data
    for key in keys:
        value = value.get(key) if isinstance(value, dict) else None
    return None if value is None else str(value)


def _lock_version(root: Path) -> str | None:
    packages = tomllib.loads(_text(root, "uv.lock")).get("package", [])
    versions = [p.get("version") for p in packages if p.get("name") == "fep-lean"]
    return versions[0] if len(versions) == 1 else None


def read_versions(root: Path) -> dict[str, str | None]:
    """Every version-bearing source, keyed by the file a maintainer edits."""
    pyproject = tomllib.loads(_text(root, "pyproject.toml"))
    return {
        "pyproject.toml": pyproject.get("project", {}).get("version"),
        "src/fep_lean/__init__.py": _assignment(
            root, "src/fep_lean/__init__.py", "__version__"
        ),
        "release_bundle/_constants.py": _assignment(
            root,
            "src/fep_lean/output/release_bundle/_constants.py",
            "_CANONICAL_RELEASE_VERSION",
        ),
        "CITATION.cff": _nested(_yaml(root, "CITATION.cff"), "version"),
        "manuscript/config.yaml": _nested(
            _yaml(root, "manuscript/config.yaml"), "paper", "version"
        ),
        "config/settings.yaml": _nested(
            _yaml(root, "config/settings.yaml"), "project", "version"
        ),
        "uv.lock": _lock_version(root),
    }


def read_dates(root: Path) -> dict[str, str | None]:
    return {
        "CITATION.cff": _nested(_yaml(root, "CITATION.cff"), "date-released"),
        "manuscript/config.yaml": _nested(
            _yaml(root, "manuscript/config.yaml"), "paper", "date"
        ),
        "release_bundle/_constants.py": _assignment(
            root,
            "src/fep_lean/output/release_bundle/_constants.py",
            "_CANONICAL_RELEASE_DATE",
        ),
    }


def read_release(root: Path) -> Release:
    versions, dates = read_versions(root), read_dates(root)
    return Release(
        version=versions["pyproject.toml"] or "", date=dates["CITATION.cff"] or ""
    )


def _heading(release: Release) -> str:
    return f"## {release.version} — {release.date}"


def metadata_errors(root: Path) -> tuple[str, ...]:
    release = read_release(root)
    errors = [
        f"{source} version {value!r} != pyproject.toml {release.version!r}"
        for source, value in read_versions(root).items()
        if value != release.version
    ]
    errors += [
        f"{source} date {value!r} != CITATION.cff {release.date!r}"
        for source, value in read_dates(root).items()
        if value != release.date
    ]
    headings = re.findall(r"(?m)^## .*$", _text(root, "CHANGELOG.md"))
    if not any(h.startswith(_heading(release)) for h in headings):
        errors.append(f"CHANGELOG.md lacks a '{_heading(release)}' section")
    return tuple(errors)


def release_notes(root: Path, release: Release) -> str:
    lines = _text(root, "CHANGELOG.md").splitlines()
    start = next(
        i for i, line in enumerate(lines) if line.startswith(_heading(release))
    )
    end = next(
        (i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")),
        len(lines),
    )
    return "\n".join(lines[start:end]).strip() + "\n"


def hosted_errors(sha: str, runs: list[dict[str, Any]]) -> tuple[str, ...]:
    """The newest hosted CI run on the exact commit must have succeeded."""
    exact = [run for run in runs if run.get("headSha") == sha]
    if not exact:
        return (f"no hosted {WORKFLOW} run for {sha}",)
    newest = exact[0]
    if newest.get("status") != "completed":
        return (f"hosted {WORKFLOW} run for {sha} not completed",)
    if newest.get("conclusion") != "success":
        return (f"hosted {WORKFLOW} run for {sha}: {newest.get('conclusion')}",)
    return ()


def job_errors(jobs: list[dict[str, Any]]) -> tuple[str, ...]:
    """Every promised job must have run and succeeded, none skipped."""
    conclusions = {str(job.get("name")): job.get("conclusion") for job in jobs}
    errors = [
        f"hosted {WORKFLOW} job {name!r}: {conclusions.get(name) or 'missing'}"
        for name in REQUIRED_JOBS
        if conclusions.get(name) != "success"
    ]
    cells = {n: c for n, c in conclusions.items() if n.startswith(DISTRIBUTION_PREFIX)}
    if not cells:
        errors.append(f"hosted {WORKFLOW} run has no distribution matrix jobs")
    errors += [
        f"hosted {WORKFLOW} job {name!r}: {conclusion}"
        for name, conclusion in sorted(cells.items())
        if conclusion != "success"
    ]
    return tuple(errors)


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, capture_output=True, text=True
    ).stdout.strip()


def repository_errors(root: Path) -> tuple[str, ...]:
    errors = []
    if _git(root, "status", "--porcelain"):
        errors.append("working tree is not clean")
    _git(root, "fetch", "--quiet", "origin", "main")
    if _git(root, "rev-parse", "HEAD") != _git(root, "rev-parse", "origin/main"):
        errors.append("HEAD is not origin/main")
    return tuple(errors)


def fetch_runs(root: Path, sha: str) -> list[dict[str, Any]]:
    output = subprocess.run(
        [
            "gh", "run", "list", "--workflow", WORKFLOW, "--commit", sha,
            "--json", "headSha,status,conclusion,databaseId", "--limit", "20",
        ],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout  # fmt: skip
    runs = json.loads(output)
    return runs if isinstance(runs, list) else []


def fetch_jobs(root: Path, run_id: int) -> list[dict[str, Any]]:
    output = subprocess.run(
        ["gh", "run", "view", str(run_id), "--json", "jobs"],
        cwd=root, check=True, capture_output=True, text=True,
    ).stdout  # fmt: skip
    payload = json.loads(output)
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    return jobs if isinstance(jobs, list) else []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    parser.add_argument(
        "--hosted",
        action="store_true",
        help="also require a clean HEAD equal to origin/main with green hosted CI",
    )
    parser.add_argument("--notes", type=Path, help="write the release notes here")
    parser.add_argument("--json", action="store_true", help="print a JSON report")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    release = read_release(root)
    errors = list(metadata_errors(root))
    if args.hosted:
        errors += repository_errors(root)
        sha = _git(root, "rev-parse", "HEAD")
        runs = fetch_runs(root, sha)
        run_errors = hosted_errors(sha, runs)
        errors += run_errors
        if not run_errors:
            newest = next(run for run in runs if run.get("headSha") == sha)
            errors += job_errors(fetch_jobs(root, int(newest["databaseId"])))
    if args.notes and not errors:
        args.notes.write_text(release_notes(root, release), encoding="utf-8")
    if args.json:
        report = {"version": release.version, "date": release.date, "errors": errors}
        print(json.dumps(report, indent=2))
    else:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        if not errors:
            print(f"OK: release {release.tag} ({release.date}) gate passes")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
