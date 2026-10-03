---
title: fep_lean Ideal State Assessment
status: active
phase: verifying
updated: 2026-10-02
---

# fep_lean Ideal State Assessment

## Problem

`fep_lean` combines a 168-row catalogue, generated Lean source, a pinned
Lean/Mathlib workspace, Hermes model calls, OpenGauss persistence, manuscript
projections, and strict run reports. The repository must distinguish a
deterministic offline catalogue from real theorem verification. A green local
command is only meaningful when its capability boundary and evidence are
explicit.

## Vision

A fresh checkout can reproduce the catalogue, acquire the exact declared Lean
toolchain, compile the canonical aggregate, and expose a bounded full-run
workflow whose report proves what was actually verified. Missing external
credentials or failed topics stop full mode without producing a misleading
success report.

## Scope

This assessment covers the standalone repository boundary:

- Typed authoring parity among the roster/family metadata, semantic and novelty
  review, authored relations, family-owned canonical bodies, and their
  generated YAML/Lean/documentation projections.
- Python dependency installation, tests, coverage, type checking, and local
  subprocess/file/database behavior.
- Exact Lean/Mathlib `v4.34.1` acquisition and compilation, plus a
  fail-closed audit against the newest stable release pair.
- Hermes, OpenGauss, SQLite session lifecycle, report provenance, and generated
  manuscript artifacts.
- Documentation links, cross-references, pinned dependency claims, and this
  repository's operator contracts.
- The authorized `v1.4.0` minor release after final-source acceptance, including
  intentional main publication and verified tag, release and artifact identity.

## Out of scope

- Changing the parent repository or any sibling repository.
- Treating catalogue mode, a cached response, or a generated manuscript value
  as proof that a theorem was verified.
- Printing, inventing, or storing provider credentials.
- Making mathematical claims stronger than the source theorem statements and
  the compiler evidence support.

## Ideal-state criteria

| ID | Criterion | Required evidence |
| --- | --- | --- |
| ISA-01 | The sealed topic roster and family registry are complete and parity-safe. | Registry/SSOT tests pass; the aggregate generator is deterministic and leaves no diff. |
| ISA-02 | Offline mode is deterministic and honest. | `uv run fep-lean catalogue` completes, emits reproducible artifacts, and reports `verified_topics: 0`. |
| ISA-03 | The local Python boundary is reproducible. | `uv sync --locked --extra dev`, `uv pip check`, the coverage gate, and `uv run mypy src` pass. |
| ISA-04 | The pinned Lean workspace is real, not merely configured. | Direct pinned Lean/Lake version probes, Mathlib cache/build, `lake build FepSketches`, an exact sealed-roster native compile sweep, and the declaration/axiom audit pass. |
| ISA-05 | Full mode is fail-closed. | Preflight requires Gauss, writable state, exact Lean/Lake/Mathlib, and Hermes credentials; any failure returns an error without a successful report. |
| ISA-06 | The live full path is end-to-end. | A permitted Hermes provider answers a bounded smoke run, OpenGauss persists and closes sessions, Lean verifies each selected topic, and the report/manifest agree. |
| ISA-07 | Reports are provenance-safe. | Selected-topic identities and denominators, source/config and compiled-source digests, the preserved Lean declaration contract, toolchain revision, nested artifact hashes, verification source, and completion state are internally consistent. |
| ISA-08 | Generated manuscript projections use the requested output root. | A custom output-root run cannot consume a stale report from the default `output/reports` tree. |
| ISA-09 | Operator documentation matches behavior. | Link, Markdown hygiene, pin, and cross-reference audits pass after catalogue generation; counts and setup commands are current. |
| ISA-10 | Every primary theorem proxy has a non-vacuity and assumption-strength review on record. | `config/theorem_maturity.yaml` has a `non_vacuity` field for every topic, and the generated `docs/theorem-maturity-audit.md` renders it. The `non_vacuity` entry documents whether the statement has a real witness or is structural/vacuous; topics with `non_vacuity: structural` or `non_vacuity: witnessed` are accepted; topics missing the field are flagged. |
| ISA-11 | Scientific relations and capability history are explicit. | The typed loader validates every authored edge, every gap row has a `blocked_by` edge, derivational `formal` edges are acyclic, both theorem-backed kinds resolve leaf-owned declarations that use both endpoints, `formal_pairing` does not imply dependence, capability evidence resolves, and shared imports are reported separately. |
| ISA-12 | Manuscript claims fail closed. | Theorem-reference, bibliography/citation, placeholder, receipt, and source-to-build rendering audits pass; authored Markdown is never modified by rendering. |
| ISA-13 | Formal breadth and depth are inspectable without a second semantic source. | Coverage JSON/Markdown and the offline SVG/HTML atlas are deterministic projections of the same canonical join, conserve every node/edge, and pass drift/accessibility tests; the numerical dashboard independently renders every typed family witness and preserves its non-proof evidence label. |

## Anti-criteria

The repository is not in the ideal state if any of these occurs:

- catalogue mode reports a verified topic or full mode reports success after a
  failed capability check;
- a generated aggregate, report, or manuscript projection is treated as an
  authoring source of truth;
- setup silently accepts the wrong Lean version, a partial Mathlib checkout, or
  a failed build;
- a report calls failed Hermes rows `hermes_refined`, uses the full catalogue
  as a filtered-run denominator, or records stale artifact hashes;
- an unexpected runner failure leaves an open SQLite session or a live worker;
- validation acquires dependencies, prints credentials, or makes unbounded
  network calls;
- external credentials are committed, copied into tracked files, or inferred
  from a successful local fixture;
- stale test counts, version claims, or links make the documented operator path
  disagree with the checked-out tree.

## Verification strategy

Run these probes from the repository root, in order when a full local audit is
needed:

```bash
uv sync --locked --extra dev
uv run python scripts/_maint_build_topics_catalogue.py --check
uv run python scripts/_maint_build_fep_all_lean.py --check
uv run python scripts/_maint_build_formal_modules.py --check
uv run python scripts/theorem_maturity_audit.py --check
uv run python scripts/build_formalism_coverage.py --check
uv run python scripts/_maint_build_lean_landscape.py --check
uv run fep-lean atlas --check
uv run fep-lean dashboard --check
uv run python docs/pin_audit.py --check-latest
uv run mypy src
uv run fep-lean setup
cd lean
lake build FepSketches
cd ..
uv run fep-lean verify --fail-on-warnings --receipt output/native-verification.json
uv run python scripts/audit_formalisms.py --receipt output/formalism-audit.json
uv run fep-lean catalogue
uv run python docs/theorem_ref_audit.py
uv run python docs/citation_audit.py
uv run python scripts/render_manuscript.py --check
uv run python docs/check_links.py --strict --include-root
uv run python docs/md_hygiene.py --strict
uv run python docs/xref_audit.py
uv run python scripts/capture_browser_acceptance.py
uv run python scripts/build_release_bundle.py --run-python-acceptance
release_dir="$(mktemp -d)"
SOURCE_DATE_EPOCH=0 uv run python scripts/build_release_bundle.py \
  --output "$release_dir/fep-lean-candidate-168.tar.gz"
SOURCE_DATE_EPOCH=0 uv run python scripts/build_release_bundle.py \
  --check --output "$release_dir/fep-lean-candidate-168.tar.gz"
uv run fep-lean preflight
```

`preflight` reports the external full-mode capability boundary. A complete
local assessment must also run the direct Lean gate and the bounded full
workflow after credentials are supplied through the operator's existing secret
mechanism:

```bash
FEP_LEAN_CATALOGUE_COMPILE_TEST=1 uv run pytest tests/test_catalogue_bodies_compile.py -q --no-cov
uv run fep-lean run --topic fep-001
uv run fep-lean run
```

The smoke run is accepted only when its result is `complete: true`; the full
run is accepted only when all selected topics are cleanly verified and the
report's verification manifest agrees with the result. If credentials are not
available, record the exact preflight failure and leave the full-run criterion
open in [TODO.md](TODO.md).

## Current assessment

The maintained schema-2 roster spans `fep-001` through `fep-168` in 22
families. Canonical bodies are family-owned and formal resources are manifested
foundations/composition leaves behind an import-only aggregate. The generated
coverage and theorem-maturity projections own the live declaration, relation,
capability, import, and semantic-disposition totals. The current reviewed
maturity split is 149 formalized, 13 conditional proxies, and six structural
proxies. Satisfied capability nodes refer to their narrowed statements;
compilation cannot erase those boundaries.

The 2026-09-30 baseline at `cd4a84c` has independently validated hosted
native and declaration/axiom evidence at the v4.34.1 pin. Expanded local
native and H3 export checkpoints retain their exact source epochs. Receipt
currency must be checked against the live source; none of these observations
substitutes for final package or scientific acceptance.

The 2026-10-02 publication at `409ee71` has local guarded Python acceptance
(2,308 passes, 90.65% coverage) and strict render preparation. Its exact-SHA
hosted run passed ten Ubuntu/macOS distribution cells but failed all five
Windows cells, one Python runtime-fixture test and two H2 custody checks.
No native or accepted-render artifact was produced by that run. Follow-up
source repairs reopen dependent source-currency gates; the
[remaining acceptance](specs/comprehensive-science-improvement/NEXT.md)
contains only open steps. Earlier failed probes remain retained history.

The [fresh Q7 source-pair capture](specs/comprehensive-science-improvement/evidence/public-q7-final-source-20261002-r1/summary.json)
passes all 12 fresh stages and four closing checks, five-runtime scaffold parity
and 124 pure controls. Its exact new native receipt is separately validated;
runner execution remains unverified. Native-input changes require a new source
pin and receipt validation. Capture-time guidance bytes remain recorded, and
postcapture prose changes carry their own reviewed delta. Q5/Q6 remain
historical and active GNN work is preserved. Catalogue-native and package
publication acceptance remain separate.

Fresh H2 custody and continuous G0 acceptance preceded the immutable H3.0
freeze. H3 model/composition proofs, exports and independent proof-role reviews
retain their recorded epochs. The frozen primary remains unopened until
current package and source-bound proof/export gates pass. Complete recovery,
negative controls, independent final claim review and clean-environment study
reproduction are mandatory; the empirical branch is governed no-go without
licensed data. The original nine program criteria remain binding.

The 2026-08-20 provider reports remain historical for their earlier source
snapshots. They cannot close ISA-06 or the provider-backed portion of ISA-07
for today's roster. A new full Hermes/OpenGauss receipt requires explicit
credential/spend authorization and independent live-source validation.

## Release boundary

Source metadata is the 1.4.0 candidate dated 2026-10-02; the existing v1.3.0
tag records the earlier 159-topic cut. As checked on 2026-10-02, the latest
published GitHub release is v1.2.0. Daniel authorized the next minor release
after final-source acceptance.
The current 168-topic tree is not a published GitHub release. Publication
readiness requires all applicable final-source receipts, deterministic bundle
parity, version/DOI agreement, and publication with remote
commit and artifact-hash verification. Historical receipts do not cross this
boundary. Neither compilation nor provider execution establishes the FEP as a
physical theory.

Prior delivery checkpoints remain in the [W2 operations record](specs/gnn-bridge-w2-source-custody/REPORT.md), [wave-2 report](specs/gnn-bridge-w2-source-custody/WAVE2-REPORT.md), [Q5 proof record](specs/gnn-bridge-q5-artifact-proof/REPORT.md), [H2 audit](specs/done/horizon-2-smooth-stochastic/readiness/07-terminal-audit-20260904.md), and repository history. They retain their original source and verification boundaries. Completed delivery checklists do not belong in this active assessment.
