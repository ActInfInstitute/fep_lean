# Development guide

## Setup

```bash
uv sync --locked --extra dev
uv run python -c "from fep_lean.catalogue import FEPTopicCatalogue; print(len(FEPTopicCatalogue.default().topics))"
```

The distribution uses a single `fep_lean` namespace under `src/fep_lean/`.
Do not add `PYTHONPATH` shims or import obsolete top-level modules such as
`catalogue` or `pipeline`; the isolated-wheel test enforces this boundary.

## Canonical authoring graph

- `config/catalogue_metadata.yaml`: stable topic metadata and Mathlib hints.
- `config/theorem_maturity.yaml`: semantic review and primary theorem.
- `config/formalism_novelty.yaml`: expansion-row nearest topics, carrier delta,
  invariant, and required composition bridge.
- `config/formalism_relations.yaml`: explicit derivational formal,
  non-implicational formal-pairing, conceptual, and blocker relations plus
  retained capability status/evidence.
- `src/fep_lean/catalogue/bodies/*.py`: family-owned canonical Lean bodies;
  `registry.py` validates their sole ordered union and `latex.py` derives
  theorem signatures.
- `src/fep_lean/formal/`: reusable finite and measure-theoretic foundations plus
  exact cross-topic proofs; `manifest.py` owns foundation, leaf-composition,
  and aggregate roles.
- `config/topics.yaml`, packaged `src/fep_lean/data/topics.yaml`, aggregate
  Lean, maturity audit, and coverage files: generated projections.

Every body keeps its `namespace FEPNNN ... end FEPNNN` wrapper and may declare
the narrow Mathlib imports it needs. Generated aggregate wrappers add a second
topic namespace to prevent helper collisions.

## Change loop

```bash
uv run python scripts/_maint_build_topics_catalogue.py
uv run python scripts/_maint_build_fep_all_lean.py
uv run python scripts/_maint_build_formal_modules.py
uv run python scripts/theorem_maturity_audit.py
uv run python scripts/build_formalism_coverage.py
uv run fep-lean atlas
uv run fep-lean dashboard

uv run python scripts/_maint_build_topics_catalogue.py --check
uv run python scripts/_maint_build_fep_all_lean.py --check
uv run python scripts/_maint_build_formal_modules.py --check
uv run python scripts/theorem_maturity_audit.py --check
uv run python scripts/build_formalism_coverage.py --check
uv run python scripts/_maint_build_lean_landscape.py --check
uv run fep-lean atlas --check
uv run fep-lean dashboard --check
uv run python specs/geo-infer-notation-bridge/check_geo_notation_bridge.py --check
uv run python docs/theorem_ref_audit.py
uv run python docs/citation_audit.py
uv run fep-lean catalogue
uv run python scripts/render_manuscript.py --check

uv run ruff check src tests scripts docs
uv run ruff format --check src tests scripts docs
uv run mypy src
uv run pytest tests/ -q --cov=src --cov-fail-under=89 -m "not serial_lean"
uv run python docs/check_links.py --strict --include-root
uv run python docs/md_hygiene.py --strict
uv run python docs/pin_audit.py --check-latest
uv run python docs/xref_audit.py
```

Run native Lean acceptance separately because it is the expensive semantic
compiler boundary:

```bash
uv run fep-lean verify \
  --fail-on-warnings \
  --receipt output/native-verification.json
cd lean && lake build FepSketches
cd .. && uv run python scripts/audit_formalisms.py \
  --receipt output/formalism-audit.json
```

The native receipt establishes exact-source compilation for the stable topic
roster; the formalism audit separately covers the maintained formal modules
and reviewed declarations. A credentialed full run remains a distinct gate:

```bash
uv run fep-lean preflight
uv run fep-lean run --topic fep-001
uv run fep-lean run
```

Never inject credentials into source, tests, or generated evidence.

## Package boundaries

| Area | Path | Contract |
| --- | --- | --- |
| Catalogue | `src/fep_lean/catalogue/` | typed authoring, loading, audits, coverage |
| Formal kernel | `src/fep_lean/formal/` | reusable finite carriers, cross-topic proofs, and exact Lake projection |
| Verification | `src/fep_lean/verification/` | read-only capability probes, Lean subprocesses, declaration/axiom audit |
| Hermes | `src/fep_lean/llm/` | provider request, retry, and response validation |
| Sessions | `src/fep_lean/gauss/` | SQLite ownership and per-topic runner |
| Pipeline | `src/fep_lean/pipeline/` | strict `catalogue`/`full` orchestration |
| Output | `src/fep_lean/output/` | receipts, reports, figures, rendering, atlas, and numerical witness dashboard |

Use type hints on public APIs, immutable dataclasses for source records,
structured results at subprocess/network boundaries, and temporary paths in
tests. Preserve catalogue, native, and full-run evidence as separate types and
claims.

For theorem ownership, support conventions, the validation ladder, and the
limits of numerical witnesses, see
[formal-kernel methods](formal-kernel-methods.md).

## Roster expansion

The current schema deliberately seals a reviewed, family-partitioned roster.
Adding another topic is a policy/schema change, not a YAML append. It requires
updating the roster seal and family metadata, semantic record, canonical body,
novelty record and composition bridge, generated projections, registry and
coverage tests, and manuscript review together. A new ID is not accepted until
that scientific review and its native acceptance plan are explicit.

## Source-owner roster expansion

The report and native receipts bind a versioned owner roster
(`SOURCE_OWNER_ROSTER` in `src/fep_lean/output/provenance.py`), not a
recursive checkout snapshot. Adding a file under `src/fep_lean/**/*.py` or
`scripts/*.py` fails receipt validation fail-closed until the file is
reviewed into the roster and `OWNER_MANIFEST_VERSION` is bumped. The bump
orphans every retained receipt that pins the previous version, so roster
growth is a coordinated evidence refresh (the completed refresh is recorded
in [CHANGELOG.md](../CHANGELOG.md); a further roster change re-opens the
requirement), not a per-PR append. Per-PR alternatives: fold the new code
into an existing
rostered owner (the status verb lives in `cli.py`), or keep tooling
slice-local under `specs/`, which is not rostered.

See [authorship-guide.md](authorship-guide.md), [testing.md](testing.md), and
[troubleshooting.md](troubleshooting.md).

## Interpreter contract

`requires-python = ">=3.10"` declares the packaging floor, but the current
dev/evidence reality is narrower and pinned: `.python-version` pins CPython
3.14 for development and CI, mypy models 3.12 (`[tool.mypy] python_version`),
and the runtime test suite runs under 3.14 only. The declared 3.10/3.11 floor
is evidentially unsupported: `scaffold_digest` freezes `ast.dump` output,
which differs across CPython minor versions, so a scaffold accepted under one
interpreter cannot be re-validated under another. The Q7 module now enforces
this in code: `scaffold_digest` refuses to run before parsing under any
interpreter outside the accepted set — exactly CPython 3.14, the
`.python-version` pin — raising a `ContinuousArtifactError` naming the
accepted set and the running interpreter. The pinned `runner_ast_sha256`
digest is interpreter-contract-pinned to that set and is unchanged by the
guard. The guard does not relax the 3.14-only rule: a version-stable
serialization or an explicit multi-interpreter acceptance record still lands
as a new reviewed scaffold via `FEP-SCAFFOLD-PORTABILITY` with a coordinated
custody re-pin.

## Custody refresh orchestration

`uv run fep-lean custody <census|apply|refresh>` is the H2.7 custody machinery adapter.
`census` is a read-only drift report; `apply` performs one staged 14-phase run into
`--output-dir` (required, staged-only) with no repo-side writes; `refresh` composes
the guarded refresh loop.

`refresh` modes are mutually exclusive:

| Mode | Contract |
| --- | --- |
| default | census → strict verify gate (`GATE_EXPECTATIONS`) → one staged 14-phase `apply` into `--output-dir` (default fresh temp dir) → read-only verify set → pre-capture owner gate → optional `--native` capture. Zero repo-side writes; the staged tree and replacement directives are coordinator inputs. |
| `--plan` | Read-only planning pass. No test/audit subprocesses (no pytest, no formalism audit, no writers; read-only git probes only). Writes a plan journal and stops; state `planned`. |
| `--fixpoint` | Bounded staged fixpoint over the same 14-phase order (H3 lockstep last). Requires `--output-dir`. Terminal state `awaiting-commit`. |
| `--resume <journal-dir>` | Resumes only against a committed tip. Validates the commit is the agreed candidate, then completes evidence at that tip. Terminal state `captured` (or `awaiting-render-acceptance`). |

`--plan` refuses on: missing/empty `--reason`, dirty tree, unknown owners (`report_owner_errors`
non-empty), live-red census records, staleness outside `--authorized`, pin/toolchain mismatch,
and an authorized change path outside the reviewed source owners (no roster auto-growth).

`--fixpoint` rounds read the previous round's staged candidate (staged specs
tree plus projected directive bytes, carried into the next round). Default
bound 4 rounds (`--max-rounds`); a repeated non-terminal state hash stops as a
cycle; non-convergence at the bound stops. Convergence requires zero mutations
and zero directives in a round plus a byte-identical re-application into a
throwaway directory. The journal records per-round inputs, outputs, and state
hash, and classifies receipt re-issues as dependency re-binds, not new
execution evidence, preserving sealed historical observations. A denied census
is a stop requiring adjudication, never a rewrite.

`--resume` validates: clean tree, HEAD past the journal's pre-commit HEAD, committed bytes of
every changed path matching the journal's expected post-commit digests, clean owner snapshot,
census/gate green at the new tip, and one verification apply round with zero mutations and
zero directives (otherwise the commit is not the agreed candidate — stop). Journal paths
touching manuscript/render inputs (`manuscript/`, `src/fep_lean/output/rendering.py`,
`scripts/render_publication.py`, `scripts/render_manuscript.py`, `docs/`) stop at the
render-acceptance barrier with state `awaiting-render-acceptance` before any capture.
Otherwise the full verify set runs at the committed tip — the mode where the writer step
`scripts/audit_formalisms.py --receipt output/formalism-audit.json` legitimately runs —
then, with `--native`, exactly one sanctioned `fep-lean verify --fail-on-warnings` capture
to `output/native-verification.json`, independently validated by
`validate_native_lean_receipt` to `native_claim_ready`, with post-capture dirty/HEAD/owner
rechecks.

Journals live under `output/custody-journal/<operation-id>/journal.json` (`--journal-dir`
overrides); `--reason` is mandatory for every refresh mode. Bridge pin cycles, commits,
pushes, roster growth, and GNN-side writes are coordinator-owned, never performed here.
Native and bridge evidence is never claimed from focused tests alone; the coordinator
runs the full battery at the integrated tip.

Phase 0 correctness: a nonzero native capture exit, a missing, stale, or non-claim-ready
receipt, or post-capture drift refuses with exit 1 (the historical exit-0 `ok` behavior is
fixed). Exit codes: 0 = report composed / fixpoint converged / resume completed; 1 = any
gate or fail-closed check refused (JSON `{"status": "error", ...}`).
