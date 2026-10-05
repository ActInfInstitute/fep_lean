# fep_lean functional specification

## Scope

The project validates the schema-2 168-topic catalogue sealed in
[`config/catalogue_metadata.yaml`](config/catalogue_metadata.yaml) against its
pinned Lean and Mathlib workspace. The evidence compiler and dependency revision
are defined by [`lean/lean-toolchain`](lean/lean-toolchain),
[`lean/lakefile.lean`](lean/lakefile.lean), and
[`lean/lake-manifest.json`](lean/lake-manifest.json). Pin and lock changes require
an explicit reviewed upgrade; a newer upstream release never replaces the
evidence compiler automatically. Package version metadata lives in
[`pyproject.toml`](pyproject.toml); publication and evidence status live in
[`TODO.md`](TODO.md) and [`HANDOFF.md`](HANDOFF.md).

The pipeline can call configured Hermes, persist each session in SQLite, and
generate deterministic manuscript and report artifacts. Its operating contract
and required checks are maintained in [`AGENTS.md`](AGENTS.md).

## Execution modes

### `catalogue`

This mode performs strict YAML/schema/source-parity validation and generates
offline figures, manuscript variables, the unified appendix, and a report. It
records `verified_topics: 0` and `capabilities.verification: false`.

### `full`

This is the default for the programmatic API and requires every configured
capability: `gauss doctor`, the exact Lean/Lake pins, a complete Mathlib build,
writable configured output and persistence destinations, and Hermes credentials
as defined in [Configuration](docs/configuration.md). It executes one Hermes + Lean +
SQLite session per selected topic. A topic succeeds only when the Hermes-derived
sketch compiles without proof holes. Any failed capability or topic makes the
pipeline incomplete and prevents a successful report.

### `verify`

This command is a separate native Lean evidence path. It compiles canonical
topic bodies without Hermes or OpenGauss. With `--receipt` it writes a typed,
source-digest-bound receipt; full-catalogue claim readiness additionally
requires the exact ordered roster, zero failures, zero warnings, zero `sorry`,
and current toolchain/catalogue/source identities.

### `atlas`

This command is a deterministic offline projection of canonical coverage. It
writes a standalone SVG and self-contained interactive HTML view, or performs a
non-mutating drift check with `--check`. It carries no compilation or full-run
claim; derivational formal edges and non-implicational formal pairings display
the qualified Lean witnesses already maintained by the relation graph.

### `dashboard`

This command evaluates the typed deterministic numerical witness registry and
renders a shared immutable model as offline SVG and accessible HTML. Every
witness names theorem mirrors, parameters, typed exact checks with per-check
tolerances, and boundary behavior. The dashboard is explanatory non-proof
evidence; `--check` performs
a non-mutating freshness test.

## Public API

```python
from fep_lean.pipeline.core import FEPPipeline
from fep_lean.pipeline.orchestrator import run_pipeline, run_single_topic

result = run_pipeline(mode="catalogue")
result = run_pipeline(mode="full", topic_filter=["fep-001"])
result = run_single_topic("fep-001", mode="full")
```

`PipelineResult` exposes `mode`, `complete`, `catalogue_topics`,
`verified_topics`, `capabilities`, `failure_reason`, `stages`, and
`topic_results`. `TopicRunResult` records both the refined sketch and its
`verification_source`; no result is silently substituted or relabeled.

## Validation

Python 3.14 is the evidence-validator runtime selected by
[`.python-version`](.python-version). The `requires-python >=3.10` declaration
in [`pyproject.toml`](pyproject.toml) is the packaging floor; it does not broaden
the validator contract. The declared test gate requires at least 89% line
coverage, alongside blocking Ruff lint and formatting and the other
[required checks](AGENTS.md#required-checks). Branch coverage, hosted wheel
compatibility, native compilation, and full-mode acceptance need their own
scoped evidence.

`run_validation_checks(project_root, mode=...)` is read-only. It never downloads
Mathlib, invokes a build, creates a database, or writes a report. The explicit
`fep-lean setup` command performs dependency acquisition and `lake build` with a
bounded timeout.

The catalogue loader rejects missing fields, divergence from the maintained
roster seal, duplicate or out-of-order IDs, unsupported areas/statuses, empty
theorem bodies, mismatched equation counts, and divergence from the validated
family-body registry under `src/fep_lean/catalogue/`.
The formalism-graph loader separately rejects unknown or self targets,
unsupported edge kinds, duplicate edges, derivational-formal cycles,
unreferenced capabilities, and missing blocker edges for semantic gap rows.
Both `formal` and `formal_pairing` edges require resolvable qualified witnesses;
conceptual and blocker edges forbid witnesses. Partial/satisfied capability
nodes require resolvable declaration evidence.

`run_formalism_audit` imports the aggregate Lean library, whose manifested leaf
composition modules own the cross-topic witnesses. It resolves every primary
and semantic-evidence declaration, runs `#print axioms` for the evidence set,
and fails on stale projections, warnings, compiler errors, timeouts, or
`sorryAx`.

## Artifacts

Successful pipeline runs write a timestamped report containing Markdown, JSON,
a verification manifest, and SHA-256 hashes. Catalogue generation writes
`manuscript/manuscript_vars.yaml` and the unified appendix. Rendering writes
resolved chapters to `output/manuscript/` without changing authored Markdown.
Generated files are never evidence by themselves: native claims require a
validated native receipt, and Hermes/OpenGauss claims require an independently
validated, claim-ready full report.

The tracked coverage JSON/Markdown, formalism atlas SVG/HTML, and numerical
dashboard SVG/HTML are deterministic projections with non-mutating drift
checks. Every manifested workspace Lean module is an exact projection of its
packaged canonical resource.
