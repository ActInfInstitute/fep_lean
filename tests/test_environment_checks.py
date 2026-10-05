"""Capability validation contract."""

from pathlib import Path

import pytest

from fep_lean.verification.environment import (
    CATALOGUE_VALIDATION_CHECK_NAMES,
    FULL_VALIDATION_CHECK_NAMES,
    run_validation_checks,
)

PROJ = Path(__file__).resolve().parent.parent


def test_catalogue_validation_is_read_only_capability_check() -> None:
    result = run_validation_checks(PROJ, mode="catalogue")
    assert result["status"] == "ok"
    assert result["mode"] == "catalogue"
    assert result["failed_count"] == 0
    assert all(check["ok"] for check in result["checks"])
    assert [check["name"] for check in result["checks"]] == list(
        CATALOGUE_VALIDATION_CHECK_NAMES
    )


def test_full_validation_reports_missing_capabilities_without_building(
    monkeypatch,
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    result = run_validation_checks(PROJ, mode="full")
    assert result["status"] == "error"
    assert any(
        check["name"] == "hermes_credentials" and not check["ok"]
        for check in result["checks"]
    )
    assert any(check["name"] == "mathlib_built" for check in result["checks"])
    assert [check["name"] for check in result["checks"]] == list(
        FULL_VALIDATION_CHECK_NAMES
    )


def test_validation_reports_the_selected_output_target(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    selected = tmp_path / "selected"
    selected.mkdir()
    monkeypatch.setattr(
        "fep_lean.verification.environment.os.access",
        lambda path, _mode: Path(path) != selected,
    )
    result = run_validation_checks(PROJ, mode="catalogue", output_root=selected)
    output = next(
        check for check in result["checks"] if check["name"] == "output_writable"
    )
    assert output["ok"] is False
    assert str(selected) in output["message"]
    assert result["status"] == "error"

    monkeypatch.setenv("FEP_LEAN_OUTPUT_ROOT", str(selected))
    implicit = run_validation_checks(PROJ, mode="catalogue")
    implicit_output = next(
        check for check in implicit["checks"] if check["name"] == "output_writable"
    )
    assert implicit_output["ok"] is False
    assert str(selected) in implicit_output["message"]
