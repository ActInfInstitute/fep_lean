"""Strict pipeline contract tests."""

from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest
import yaml

from fep_lean.catalogue.topics import CatalogueValidationError, FEPTopicCatalogue
from fep_lean.output.manuscript import _verify_block_from_manifest
from fep_lean.output.provenance import report_owner_errors, report_source_digest
from fep_lean.pipeline.core import (
    FEPPipeline,
    PipelineResult,
    StepResult,
    _max_topics_from_env,
)
from tests._support.catalogue_project import manuscript_owner_state

PROJ = Path(__file__).resolve().parent.parent
pytest_plugins = ["tests._support.catalogue_project"]


def test_pipeline_instantiates() -> None:
    assert FEPPipeline(PROJ) is not None


def test_catalogue_mode_is_complete_but_unverified(
    tmp_path: Path, catalogue_project: Path
) -> None:
    result = FEPPipeline(catalogue_project, output_root=tmp_path / "output").run(
        mode="catalogue", topic_filter=["fep-001", "fep-002"]
    )
    assert isinstance(result, PipelineResult)
    assert result.mode == "catalogue"
    assert result.complete is True
    assert result.catalogue_topics == 2
    assert result.verified_topics == 0
    assert result.capabilities["verification"] is False
    assert (
        next(stage for stage in result.stages if stage.name == "Gauss Sessions").status
        == "not_run"
    )


def test_real_catalogue_writes_only_the_private_project(
    tmp_path: Path, catalogue_project: Path
) -> None:
    live_before = manuscript_owner_state(PROJ)
    assert report_owner_errors(catalogue_project) == ()
    assert report_source_digest(catalogue_project) == report_source_digest(PROJ)
    assert not (catalogue_project / ".git").exists()
    assert not (catalogue_project / "lean/.lake").exists()
    assert {
        path.relative_to(catalogue_project).as_posix()
        for path in (catalogue_project / "specs").rglob("*")
        if path.is_file()
    } == {
        "specs/geo-infer-notation-bridge/check_geo_notation_bridge.py",
        "specs/gnn-bridge-q6-activeinference-artifact/skeleton/canonical_bool_runner.jl.in",
    }
    variables = catalogue_project / "manuscript/manuscript_vars.yaml"
    appendix = catalogue_project / "manuscript/09z_unified_formalism_catalogue.md"
    assert not variables.exists()
    assert not appendix.exists()
    pipeline = FEPPipeline(catalogue_project, output_root=tmp_path / "products")

    result = pipeline.run(mode="catalogue")

    assert result.status == "ok"
    assert result.complete is True
    assert result.catalogue_topics == 168
    assert result.verified_topics == 0
    projected = yaml.safe_load(variables.read_bytes())
    assert projected["total_topics"] == 168
    assert projected["verify"]["manifest_present"] is False
    assert projected["verify"]["claim_ready"] is False
    assert "fep-168" in appendix.read_text()
    assert len(list((tmp_path / "products/figures").glob("*.png"))) == 9
    assert manuscript_owner_state(PROJ) == live_before

    # A genuine source error stays a failed catalogue attempt in that private
    # project and cannot rewrite either the prior projection or live inputs.
    private_before = manuscript_owner_state(catalogue_project)
    (catalogue_project / "config/topics.yaml").write_text("topics: []\n")
    failed = pipeline.run(mode="catalogue")
    assert failed.status == "error"
    assert failed.complete is False
    assert manuscript_owner_state(catalogue_project) == private_before
    assert manuscript_owner_state(PROJ) == live_before


def test_full_mode_fails_without_capabilities(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue_project: Path
) -> None:
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    # Actual absent capabilities, with no access to host tools or elan state.
    monkeypatch.setenv("PATH", "")
    monkeypatch.setenv("ELAN_HOME", str(tmp_path / "empty-elan"))
    monkeypatch.delenv("FEP_LEAN_LEAN_EXE", raising=False)
    monkeypatch.delenv("FEP_LEAN_LAKE_EXE", raising=False)
    result = FEPPipeline(catalogue_project, output_root=tmp_path / "output").run(
        mode="full", topic_filter=["fep-001"]
    )
    assert result.complete is False
    assert result.status == "error"
    assert result.run_dir == ""
    assert result.failure_reason
    assert not (tmp_path / "output" / "reports").exists()


def test_result_fields_are_explicit(tmp_path: Path, catalogue_project: Path) -> None:
    result = FEPPipeline(catalogue_project, output_root=tmp_path / "output").run(
        mode="catalogue"
    )
    assert result.duration_s > 0
    assert isinstance(result.topic_results, list)
    assert isinstance(result.capabilities, dict)
    assert "mode" in result.as_dict()
    assert "complete" in result.as_dict()
    assert "failure_reason" in result.as_dict()
    assert not hasattr(result, "steps")


def test_step_result_dataclass() -> None:
    step = StepResult("test_step", "ok", "all fine", 0.5)
    assert step.name == "test_step"
    assert step.status == "ok"
    assert step.message == "all fine"
    assert step.duration_s == 0.5
    assert step.error is None


def test_step_result_records_error() -> None:
    step = StepResult("test_step", "error", "boom", 0.0, error="boom")
    assert step.error == "boom"
    assert step.status == "error"


def test_filters_and_topic_cap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue_project: Path
) -> None:
    monkeypatch.setenv("FEP_LEAN_MAX_TOPICS", "2")
    result = FEPPipeline(catalogue_project, output_root=tmp_path / "output").run(
        mode="catalogue", area_filter="FEP"
    )
    load = next(stage for stage in result.stages if stage.name == "Load Catalogue")
    assert len(load.payload["topics"]) == 2


def test_unknown_topic_is_an_error(tmp_path: Path, catalogue_project: Path) -> None:
    result = FEPPipeline(catalogue_project, output_root=tmp_path / "output").run(
        mode="catalogue", topic_filter=["fep-999"]
    )
    assert result.status == "error"
    assert "unknown topic" in result.failure_reason


def test_max_topics_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("FEP_LEAN_MAX_TOPICS", raising=False)
    assert _max_topics_from_env() is None
    monkeypatch.setenv("FEP_LEAN_MAX_TOPICS", "3")
    assert _max_topics_from_env() == 3
    monkeypatch.setenv("FEP_LEAN_MAX_TOPICS", "0")
    with pytest.raises(ValueError):
        _max_topics_from_env()


def test_stats_never_counts_catalogue_as_verified() -> None:
    result = PipelineResult(
        status="ok", mode="catalogue", complete=True, catalogue_topics=50
    )
    assert result.stats["topics_total"] == 50
    assert result.stats["topics_verified"] == 0
    assert result.stats["stages_ok"] == 0
    assert result.lean_compile_ok == 0


def test_topic_metrics_use_clean_compilation() -> None:
    result = PipelineResult(status="ok", mode="full", catalogue_topics=2)
    result.topic_results = [
        SimpleNamespace(hermes_success=True, lean_compiles=True, lean_has_sorry=False),
        SimpleNamespace(hermes_success=True, lean_compiles=True, lean_has_sorry=True),
    ]
    assert result.hermes_count == 2
    assert result.lean_verified_count == 2
    assert result.lean_compile_ok == 1


def test_full_pipeline_rejects_compiling_topic_with_warnings(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, catalogue_project: Path
) -> None:
    pipeline = FEPPipeline(catalogue_project, output_root=tmp_path / "output")
    warning = SimpleNamespace(
        topic_id="fep-001",
        success=False,
        hermes_success=True,
        lean_compiles=True,
        lean_has_sorry=False,
        lean_warnings=["fixture warning"],
        error="fixture warning",
    )
    warning.as_dict = lambda: vars(warning).copy()
    monkeypatch.setattr(
        "fep_lean.pipeline.core.run_validation_checks",
        lambda *_args, **_kwargs: {
            "status": "ok",
            "failed_count": 0,
            "checks": [],
        },
    )
    monkeypatch.setattr(
        pipeline, "_run_gauss", lambda _workflow: {"results": [warning]}
    )
    monkeypatch.setattr(pipeline, "_write_artifacts", dict)

    result = pipeline.run(mode="full", topic_filter=["fep-001"])

    assert result.complete is False
    assert result.verified_topics == 0
    assert result.lean_stats["warning_count"] == 1
    assert result.lean_stats["warning_logs"] == ["fep-001: fixture warning"]


def test_invalid_mode_rejected() -> None:
    with pytest.raises(ValueError):
        FEPPipeline(PROJ).run(mode="invalid")  # type: ignore[arg-type]


def test_empty_catalogue_is_rejected(tmp_path: Path) -> None:
    yaml_path = tmp_path / "topics.yaml"
    yaml_path.write_text("topics: []\n", encoding="utf-8")
    with pytest.raises(CatalogueValidationError):
        FEPTopicCatalogue.from_yaml(yaml_path)


def test_verify_block_defaults_without_topics_keys(tmp_path: Path) -> None:
    p = tmp_path / "verification_manifest.json"
    p.write_text(json.dumps({"random_key": 42}), encoding="utf-8")
    b = _verify_block_from_manifest(p)
    assert b["manifest_present"] is True
    assert b["verify_lean_ran"] is False
    assert b["topics_with_result"] == 0


def test_verify_block_non_integer_topics_falls_back_to_results_count(
    tmp_path: Path,
) -> None:
    p = tmp_path / "verification_manifest.json"
    p.write_text(
        json.dumps({"topics_with_result": "fifty", "results": [{"compiles": True}]}),
        encoding="utf-8",
    )
    b = _verify_block_from_manifest(p)
    assert b["manifest_present"] is True
    assert b["topics_with_result"] == 1
