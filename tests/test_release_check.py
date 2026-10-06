"""Release gate: version/date agreement, changelog section and hosted CI."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
from pathlib import Path
from types import ModuleType

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SOURCES = (
    "pyproject.toml",
    "src/fep_lean/__init__.py",
    "src/fep_lean/output/release_bundle/_constants.py",
    "CITATION.cff",
    "manuscript/config.yaml",
    "config/settings.yaml",
    "uv.lock",
    "CHANGELOG.md",
)


def _module() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "release_check", PROJECT_ROOT / "scripts" / "release_check.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _copy_sources(root: Path) -> Path:
    for relative in _SOURCES:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(PROJECT_ROOT / relative, target)
    return root


def test_repository_metadata_agrees_on_one_release() -> None:
    check = _module()
    release = check.read_release(PROJECT_ROOT)
    assert check.metadata_errors(PROJECT_ROOT) == ()
    assert release.version == check.read_versions(PROJECT_ROOT)["pyproject.toml"]
    assert release.date == check.read_dates(PROJECT_ROOT)["CITATION.cff"]


@pytest.mark.parametrize(
    ("relative", "old", "new", "message"),
    [
        ("pyproject.toml", 'version = "', 'version = "9.9.9" #', "pyproject.toml"),
        (
            "src/fep_lean/__init__.py",
            '__version__ = "',
            '__version__ = "0.',
            "__init__",
        ),
        ("CITATION.cff", "date-released: ", "date-released: 1999-01-01 #", "CITATION"),
        ("manuscript/config.yaml", "  version: ", "  version: 0.0.1 #", "manuscript"),
        ("config/settings.yaml", "  version: ", "  version: 0.0.1 #", "settings"),
    ],
)
def test_any_metadata_drift_is_reported(
    tmp_path: Path, relative: str, old: str, new: str, message: str
) -> None:
    check = _module()
    root = _copy_sources(tmp_path)
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new, 1), encoding="utf-8")
    errors = check.metadata_errors(root)
    assert errors and any(message in error for error in errors)


def test_missing_changelog_section_is_reported(tmp_path: Path) -> None:
    check = _module()
    root = _copy_sources(tmp_path)
    release = check.read_release(root)
    changelog = root / "CHANGELOG.md"
    changelog.write_text(
        changelog.read_text(encoding="utf-8").replace(
            f"## {release.version} — {release.date}", "## Unreleased", 1
        ),
        encoding="utf-8",
    )
    assert any("CHANGELOG" in error for error in check.metadata_errors(root))


def test_hosted_ci_requires_successful_run_on_exact_commit() -> None:
    check = _module()
    sha = "a" * 40
    ok = [{"headSha": sha, "status": "completed", "conclusion": "success"}]
    assert check.hosted_errors(sha, ok) == ()
    assert check.hosted_errors(sha, []) != ()
    pending = [{"headSha": sha, "status": "in_progress", "conclusion": ""}]
    assert any("not completed" in e for e in check.hosted_errors(sha, pending))
    failed = [{"headSha": sha, "status": "completed", "conclusion": "failure"}]
    assert any("failure" in e for e in check.hosted_errors(sha, failed))
    other = [{"headSha": "b" * 40, "status": "completed", "conclusion": "success"}]
    assert check.hosted_errors(sha, other) != ()
    # The newest run on the commit decides; an older success does not mask it.
    assert check.hosted_errors(sha, failed + ok) != ()


def test_release_notes_extract_only_the_version_section(tmp_path: Path) -> None:
    check = _module()
    root = _copy_sources(tmp_path)
    release = check.read_release(root)
    notes = check.release_notes(root, release)
    assert notes.startswith(f"## {release.version} — {release.date}")
    assert "\n## " not in notes[3:]


def test_cli_reports_json_and_exit_status(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    check = _module()
    assert check.main(["--root", str(PROJECT_ROOT), "--json"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["errors"] == [] and payload["version"]
    root = _copy_sources(tmp_path)
    (root / "CITATION.cff").write_text("version: 0\n", encoding="utf-8")
    assert check.main(["--root", str(root)]) == 1
