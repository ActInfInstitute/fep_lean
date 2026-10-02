"""Latest-stable Lean/Mathlib policy checks."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _audit_module():
    spec = importlib.util.spec_from_file_location(
        "pin_audit_latest", PROJECT_ROOT / "docs" / "pin_audit.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pin_audit_keeps_history_journals_out_of_current_guidance(
    tmp_path: Path,
) -> None:
    audit = _audit_module()
    names = (
        "specs/comprehensive-science-improvement/evidence/retained/REPORT.md",
        "specs/comprehensive-science-improvement/NEXT.md",
        "docs/evidence/README.md",
    )
    paths = [tmp_path / name for name in names]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("Historical Lean v4.33.1; current instructions use this pin.\n")
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.34.1",
        lean_version="4.34.1",
        mathlib_tag="v4.34.1",
        primary_model="fixture/model",
        mathlib_revision="d" * 40,
    )

    current = audit._gather_files(tmp_path)

    assert set(current) == set(paths[1:])
    assert all(audit._scan_file(path, pins) for path in current)


def test_latest_release_audit_accepts_matching_stable_pair() -> None:
    audit = _audit_module()
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.33.1",
        lean_version="4.33.1",
        mathlib_tag="v4.33.1",
        primary_model="fixture/model",
        mathlib_revision="d" * 40,
    )
    requested: list[str] = []

    def fetch_json(url: str):
        requested.append(url)
        if url == audit.LEAN_RELEASES_API:
            return [
                {
                    "tag_name": "v4.33.1",
                    "draft": False,
                    "prerelease": False,
                }
            ]
        return {"ref": "refs/tags/v4.33.1", "object": {"sha": "d" * 40}}

    result = audit.audit_latest_stable(pins, fetch_json=fetch_json)

    assert result.current
    assert result.latest_lean_tag == "v4.33.1"
    assert result.latest_compatible_tag == "v4.33.1"
    assert result.newer_lean_without_mathlib == ()
    assert result.mathlib_tag_available
    assert result.errors == ()
    assert requested == [
        audit.LEAN_RELEASES_API,
        audit.MATHLIB_TAG_API.format(tag="v4.33.1"),
    ]


def test_latest_release_audit_rejects_stale_local_pins() -> None:
    audit = _audit_module()
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.32.2",
        lean_version="4.32.2",
        mathlib_tag="v4.32.2",
        primary_model="fixture/model",
        mathlib_revision="d" * 40,
    )

    def fetch_json(url: str):
        if url == audit.LEAN_RELEASES_API:
            return [
                {
                    "tag_name": "v4.33.1",
                    "draft": False,
                    "prerelease": False,
                }
            ]
        return {"ref": "refs/tags/v4.33.1", "object": {"sha": "d" * 40}}

    result = audit.audit_latest_stable(pins, fetch_json=fetch_json)

    assert not result.current
    assert any("Lean pin" in error and "stale" in error for error in result.errors)
    assert any("Mathlib pin" in error for error in result.errors)


def test_latest_release_audit_rejects_a_stale_locked_mathlib_revision() -> None:
    audit = _audit_module()
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.33.1",
        lean_version="4.33.1",
        mathlib_tag="v4.33.1",
        primary_model="fixture/model",
        mathlib_revision="c" * 40,
    )

    def fetch_json(url: str):
        if url == audit.LEAN_RELEASES_API:
            return [
                {
                    "tag_name": "v4.33.1",
                    "draft": False,
                    "prerelease": False,
                }
            ]
        return {"ref": "refs/tags/v4.33.1", "object": {"sha": "d" * 40}}

    result = audit.audit_latest_stable(pins, fetch_json=fetch_json)

    assert not result.current
    assert "locked Mathlib revision " + "c" * 40 in "\n".join(result.errors)


def test_latest_release_audit_rejects_prerelease_or_missing_mathlib_tag() -> None:
    audit = _audit_module()
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.33.1",
        lean_version="4.33.1",
        mathlib_tag="v4.33.1",
        primary_model="fixture/model",
        mathlib_revision="d" * 40,
    )

    prerelease = audit.audit_latest_stable(
        pins,
        fetch_json=lambda _url: [
            {
                "tag_name": "v4.34.0",
                "draft": False,
                "prerelease": True,
            }
        ],
    )
    assert not prerelease.current
    assert any("no stable" in error for error in prerelease.errors)

    def missing_mathlib(url: str):
        if url == audit.LEAN_RELEASES_API:
            return [
                {
                    "tag_name": "v4.33.1",
                    "draft": False,
                    "prerelease": False,
                }
            ]
        return {"message": "Not Found"}

    missing = audit.audit_latest_stable(pins, fetch_json=missing_mathlib)
    assert not missing.current
    assert any("No recent stable Lean release" in error for error in missing.errors)


def test_latest_release_audit_waits_for_matching_mathlib_release() -> None:
    audit = _audit_module()
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.33.0",
        lean_version="4.33.0",
        mathlib_tag="v4.33.0",
        primary_model="fixture/model",
        mathlib_revision="d" * 40,
    )

    def fetch_json(url: str):
        if url == audit.LEAN_RELEASES_API:
            return [
                {
                    "tag_name": "v4.33.0",
                    "draft": False,
                    "prerelease": False,
                },
                {
                    "tag_name": "v4.33.1",
                    "draft": False,
                    "prerelease": False,
                },
            ]
        if url == audit.MATHLIB_TAG_API.format(tag="v4.33.1"):
            return {"message": "Not Found"}
        return {"ref": "refs/tags/v4.33.0", "object": {"sha": "d" * 40}}

    result = audit.audit_latest_stable(pins, fetch_json=fetch_json)

    assert result.current
    assert result.latest_lean_tag == "v4.33.1"
    assert result.latest_compatible_tag == "v4.33.0"
    assert result.newer_lean_without_mathlib == ("v4.33.1",)
    assert result.mathlib_revision == "d" * 40


def test_local_audit_catches_plain_lean_version_but_preserves_changelog_history(
    tmp_path: Path,
) -> None:
    audit = _audit_module()
    pins = audit.CanonicalPins(
        lean_toolchain="leanprover/lean4:v4.33.1",
        lean_version="4.33.1",
        mathlib_tag="v4.33.1",
        primary_model="fixture/model",
        mathlib_revision="d" * 40,
    )
    current = tmp_path / "README.md"
    current.write_text("Pinned Lean 4.32.0.\n", encoding="utf-8")
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "## Unreleased\n\nLean 4.33.1.\n\n## 1.0.0\n\nHistorical Lean 4.29.0.\n",
        encoding="utf-8",
    )

    drift = audit._scan_file(current, pins)

    assert [(item.pin_kind, item.found) for item in drift] == [
        ("lean_prose", "Lean 4.32.0")
    ]
    assert audit._scan_file(changelog, pins) == []


@pytest.mark.parametrize(
    "pin",
    (
        "leanprover/lean4:v4.34.0-rc1",
        "leanprover/lean4:nightly-2026-08-21",
        "leanprover/lean4:master",
        "leanprover/lean4:stable",
    ),
)
def test_local_toolchain_owner_rejects_nonstable_or_floating_pins(
    tmp_path: Path,
    pin: str,
) -> None:
    audit = _audit_module()
    lean_dir = tmp_path / "lean"
    lean_dir.mkdir()
    (lean_dir / "lean-toolchain").write_text(pin + "\n", encoding="utf-8")

    with pytest.raises(SystemExit, match="unexpected format"):
        audit._read_lean_toolchain(tmp_path)


@pytest.mark.parametrize(
    "mathlib_ref",
    ("v4.34.0-rc1", "master", "nightly-2026-08-21"),
)
def test_local_mathlib_owner_rejects_nonstable_or_floating_refs(
    tmp_path: Path,
    mathlib_ref: str,
) -> None:
    audit = _audit_module()
    lean_dir = tmp_path / "lean"
    lean_dir.mkdir()
    (lean_dir / "lakefile.lean").write_text(
        "require mathlib from git\n"
        '  "https://github.com/leanprover-community/mathlib4.git" '
        f'@ "{mathlib_ref}"\n',
        encoding="utf-8",
    )

    with pytest.raises(SystemExit, match="could not find"):
        audit._read_mathlib_tag(tmp_path)


def test_local_mathlib_revision_owner_is_bound_to_the_pinned_tag(
    tmp_path: Path,
) -> None:
    audit = _audit_module()
    lean_dir = tmp_path / "lean"
    lean_dir.mkdir()
    manifest = lean_dir / "lake-manifest.json"
    manifest.write_text(
        '{"packages":[{"name":"mathlib","inputRev":"v4.33.1",'
        '"rev":"' + "d" * 40 + '"}]}\n',
        encoding="utf-8",
    )

    assert audit._read_mathlib_revision(tmp_path, "v4.33.1") == "d" * 40

    with pytest.raises(SystemExit, match="inputRev does not match"):
        audit._read_mathlib_revision(tmp_path, "v4.33.0")
