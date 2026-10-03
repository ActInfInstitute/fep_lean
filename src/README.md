# fep_lean/src/

**Version**: v1.4.0 | **Status**: Active | **Last Updated**: October 2026

This directory contains the installable `fep_lean` package. Its ten domain subpackages drive the FEP Lean
pipeline. The layer runs end-to-end per-topic formalization sessions (LLM
explanation + Lean 4 compilation + SQLite session capture), and emits the
artifacts consumed by the manuscript stage (`manuscript_vars.yaml`, figures,
per-topic markdown reports).

## Subpackages

| Subpackage | Role | Key public API |
| ---------- | ---- | -------------- |
| [`fep_lean/catalogue/`](fep_lean/catalogue/) | Load the packaged sealed roster, family-owned bodies, and semantic review. | `FEPTopicCatalogue`, `TopicEntry`, `SemanticDisposition` |
| [`fep_lean/formal/`](fep_lean/formal/) | Manifested FEP/active-inference foundations, leaf composition proofs, import aggregate, and Lake projection. | `FORMAL_MODULES`, `formal_projection_drift`, `write_formal_projections` |
| [`fep_lean/verification/`](fep_lean/verification/) | Lean 4 toolchain, workspace, declaration, and axiom checks. | `LeanVerifier`, `run_validation_checks`, `run_formalism_audit` |
| [`fep_lean/llm/`](fep_lean/llm/) | Hermes LLM explainer (OpenRouter / Anthropic) with a configured fallback chain. | `HermesConfig`, `HermesExplainer`, `HermesResult`, `HermesAPIError` |
| [`fep_lean/gauss/`](fep_lean/gauss/) | SQLite-backed session store and per-topic orchestrator. | `OpenGaussClient`, `SessionRecord`, `GaussRunner`, `TopicRunResult` |
| [`fep_lean/output/`](fep_lean/output/) | Evidence receipts, source-preserving rendering, atlas, figures, and reports. | `validate_native_lean_receipt`, `build_formalism_atlas`, `Reporter` |
| [`fep_lean/pipeline/`](fep_lean/pipeline/) | 4-stage FEP pipeline DAG + entry-point wrappers. | `FEPPipeline`, `PipelineResult`, `StepResult`, `run_pipeline`, `run_single_topic` |
| [`fep_lean/bridge/`](fep_lean/bridge/) | Explicit GNN source pinning, emission and numerical comparison. | `pin_sources`, `check_sources`, `emit`, `verify_document` |
| [`fep_lean/custody/`](fep_lean/custody/) | Evidence census, strict gates, staged refresh and committed-candidate resume. | `census`, `verify`, `Census`, `Expectations` |
| [`fep_lean/prove2me/`](fep_lean/prove2me/) | Explicit authenticated remote formalization operations. | `Prove2meConfig`, `Prove2meClient`, `submit_solution`, `wait_for_verdict` |

## Package boundaries

- `catalogue/` owns typed catalogue and publication-authoring policy. Its
  coverage join resolves the `formal/` manifest and declarations; maintained
  YAML and the validated family-body registry remain the named source owners.
- `formal/` owns the reusable carriers and laws plus manifested leaf
  composition modules; its workspace copies and import aggregate are generated,
  never authored.
- `verification/` consumes catalogue/formal declarations, bridge custody and
  numerical witnesses. Environment validation checks Gauss availability;
  explicit native verification owns Lean subprocesses.
- `llm/` imports `catalogue.topics.TopicEntry` under `TYPE_CHECKING` only; at
  runtime it depends only on `urllib` and `yaml`.
- `gauss/` wires `llm/` + `verification/` + `catalogue/` into a per-topic
  orchestration loop; this is the only module that owns the SQLite file.
- `output/` consumes catalogue/formal models and upstream result dataclasses.
  Explicit browser/publication acceptance can start bounded browser and renderer
  processes; ordinary source/receipt freshness checks remain read-only.
- `pipeline/` is the top-level DAG: it composes the runtime sibling packages and
  exposes `run_pipeline()` / `run_single_topic()` for the console command and
  thin checkout scripts.
- `bridge/` validates an explicitly named sibling checkout. Numerical comparison
  and native artifact verification have separate acceptance contracts.
- `custody/` composes receipt validators and staged evidence refresh. A dependency
  re-bind preserves recorded observations; it is not new execution evidence.
- `prove2me/` owns authenticated remote proposals/submissions. Those operations
  require their own explicit authorization and never run in catalogue mode.

## Import convention

Internal modules prefer qualified subpackage paths, e.g.

```python
from fep_lean.catalogue import FEPTopicCatalogue
from fep_lean.verification import LeanVerifier
from fep_lean.gauss import GaussRunner
```

The package root (`fep_lean/__init__.py`) re-exports stable high-level symbols;
subpackages remain the preferred narrow import surface. Obsolete top-level
module names are intentionally not installed.

The installed wheel owns imports plus packaged catalogue and formal Lean
resources. Operator commands also need checkout-owned configuration, Lean, and
manuscript assets; the console validates those markers and accepts an explicit
`--project-root` instead of guessing that `site-packages` is a checkout.

See [`AGENTS.md`](AGENTS.md) for the full export list, contract notes, and
run-time wiring. The 4 recorded pipeline stages are documented in
[`fep_lean/pipeline/README.md`](fep_lean/pipeline/README.md): Load Catalogue → Environment
Validation → Gauss Sessions → Manuscript Artifacts.
