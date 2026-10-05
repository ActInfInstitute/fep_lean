# fep_lean formalism and publication handoff

**Date:** 2026-10-03
**Repository:** `ActiveInferenceInstitute/fep_formal`
**Checkout:** this repository checkout (see the `origin` remote)
**Release line:** source candidate `v1.4.0`, dated 2026-10-02; existing tag
`v1.3.0`; latest published GitHub release `v1.2.0`. Daniel authorized the minor
release after final-source acceptance, tracked by `FEP-RELEASE-NEXT`.

## Mission and evidence boundary

This standalone repository now has an installable `fep_lean` package, a typed
168-topic semantic catalogue in 22 families, a pinned Lean kernel with warning
rejection, an authored formalism relation/capability graph, fail-closed evidence
receipts, and source-to-build manuscript rendering. Keep four claims separate:

1. catalogue generation is deterministic but verifies zero topics;
2. native Lean evidence proves that the exact selected source compiled at the
   pin without warnings or `sorry`;
3. semantic disposition records how closely a row matches its advertised
   scientific topic;
4. bounded Hermes/OpenGauss evidence applies only to the exact source and
   receipt schema it records; publication-grade live evidence requires a
   claim-ready report bound to the final source.

Two bounded one-topic OpenRouter/Hermes smokes were completed on 2026-08-20
against earlier source snapshots: `fep-001` with Kimi K2.6 and `fep-002` with
Gemini 3.7 Flash. Both selected topics passed the then-current pipeline, Gauss
session, and Lean checks. They are historical connectivity and workflow
evidence only: the source and receipt schema subsequently changed, and the
current validator correctly rejects both report directories as non-current.
The report directories for those smokes were
`output/reports/run_20260820_150225_893319` and
`output/reports/run_20260820_150523_744462`; the retained copies are no longer
present under the current `output/reports/` tree.

The later 50-topic report,
`output/reports/run_20260820_183143_709998`, superseded those one-topic smokes
for its own source snapshot. It is now historical too: the schema-2 expansion
changed the roster, body-source manifest, formal resources, and source digests.
It must not be described as current evidence for the live checkout.

No provider secret is stored in the repository. Versioned publication does not
promote the historical provider runs: only a separately authorized,
source-bound full receipt can make a current Hermes/OpenGauss claim.

## Canonical ownership

| Concept | Maintained owner | Generated projection |
| --- | --- | --- |
| Static topic metadata | `config/catalogue_metadata.yaml` | catalogue YAML/package rows |
| Semantic review | `config/theorem_maturity.yaml` | package API, audit, manuscript |
| Typed relations and capabilities | `config/formalism_relations.yaml` | coverage and atlas projections |
| Lean bodies | `src/fep_lean/catalogue/bodies/*.py`, merged by `registry.py` | YAML and aggregate Lean |
| Theorem equation signatures | `src/fep_lean/catalogue/latex.py` | Catalogue and manuscript equations |
| Expansion novelty and bridges | `config/formalism_novelty.yaml` | Novelty audit and composition checks |
| Formal resource roster | `src/fep_lean/formal/manifest.py` | Lean workspace projection |
| Cross-topic theorems | `src/fep_lean/formal/compositions/*.lean` | Import aggregate and workspace leaves |
| Catalogue join | `src/fep_lean/catalogue/generation.py` | checkout/package YAML |
| Native/full evidence policy | `src/fep_lean/output/evidence.py` | manuscript claim sentences |
| Declaration/axiom audit | `src/fep_lean/verification/formalism_audit.py` | typed audit receipt |
| Formalism atlas renderer | `src/fep_lean/output/formalism_atlas.py` | standalone SVG/HTML |
| Authored manuscript | `manuscript/*.md` | `output/manuscript/` |

Never hand-edit `config/topics.yaml`, `src/fep_lean/data/topics.yaml`,
`lean/FepSketches/fep_all.lean`, any manifested `lean/FepSketches` formal resource,
`docs/formalism-coverage.*`, `docs/formalism-atlas.*`, or generated manuscript
output. Use the owner-provided generators and their `--check` modes.

## Current formal breadth and depth

- Stable schema-2 roster: `fep-001` through `fep-168`, partitioned into 22
  families across five areas.
- The generated coverage report owns all topic/formal-resource declaration,
  import, relation, and capability totals. Do not copy those moving totals into
  this handoff.
- Semantic review contains direct formalizations together with explicit
  conditional and structural proxies. Their assumptions and non-vacuity
  boundaries remain first-class even when the bodies compile.
- Manifested foundations and leaf compositions cover finite and
  measure-theoretic probability, Bayesian inversion, variational duality,
  active inference and controlled planning, temporal inference, causal
  interventions, predictive coding, stochastic thermodynamics, geometric
  optimization, collective inference, learning/model evidence, finite-sample
  risk, policy trees, native blanket transfer, exponential-family duality, and
  exact two-state continuous time.
- `fep-036` now defines a finite binomial sampling law and outcome-indexed
  Laplace prior, proves interiority, monotonicity, exact shrinkage, and
  consistency transfer from a convergent empirical frequency, while the
  statistical-convergence foundation derives the corresponding almost-sure
  Boolean, finite-atom, simultaneous, whole-law `L¹`, and finite-observable
  expectation limits. The `fep-121`--`fep-127` family now adds finite-law
  Laplace squared-risk and Brier-risk transfer plus event containment. It still
  does not claim posterior contraction, minimax optimality, empirical calibration, or a
  marginal-likelihood optimum.
- The formalism audit is designed to resolve every primary, relation,
  capability, and manifested formal-resource declaration, reject warnings and
  `sorryAx`, and require one parsed axiom result per declaration before
  recording the standard dependencies reported by Lean.

Compilation is not a proof of the FEP as a physical theory. Read
`docs/formalism-coverage.md` and `docs/theorem-maturity-audit.md` before
summarizing scientific completeness.

## Current source and evidence state

The reviewed v1.4.0 candidate changes were subsequently published to `main` at
[9aaa30e](https://github.com/ActiveInferenceInstitute/fep_formal/commit/9aaa30e94d9e31082665746dfb8715177ec84c8b)
on 2026-10-03, with equal local, tracking and direct-remote commit IDs and a
clean Git worktree at publication. No v1.4.0 tag or release has been issued.

All 15 distribution cells in its
[same-SHA hosted run](https://github.com/ActiveInferenceInstitute/fep_formal/actions/runs/37147070367)
passed across Ubuntu, macOS and Windows on Python 3.10–3.14. The Python job
failed with 34 failed, 2,337 passed and 15 skipped tests; coverage reached
90.86% against the unchanged 89% gate. The failures identify stale synthetic
custody-fixture bindings and inconsistent candidate dates. These are follow-up
repairs; this run does not establish whole-package or release acceptance.
Lean and render acceptance must be checked separately at the final source SHA.

Current local wheel acceptance retains its 15 GiB free-space requirement.
Insufficient scratch space blocks that matrix; neither a hosted distribution
pass nor a private source-only wrapper review waives the local gate. Full
production capture, H3 outcomes, study reproduction and versioned publication
remain open under the locked protocol.

The earlier source epoch retains its own evidence:

`main` was published at
[409ee71f82b3353303e6306e87c1b1fedc949088](https://github.com/ActiveInferenceInstitute/fep_formal/commit/409ee71f82b3353303e6306e87c1b1fedc949088)
on 2026-10-02, with the local and direct remote commit IDs equal. This is an
ordinary main-branch publication; no versioned release or DOI was issued.

At that source epoch, complete guarded Python acceptance passed 2,308 tests,
with 12 policy skips and 90.65% coverage above the unchanged 89% gate.
All 25 declared static checks and strict six-stage real-template render
preparation passed. Separate Q7 static/native observations, catalogue native
and H3 export checkpoints retain their exact owner and artifact bindings.

The [same-SHA hosted run](https://github.com/ActiveInferenceInstitute/fep_formal/actions/runs/37035715408)
finished with failures. Ten Ubuntu/macOS distribution cells passed; all five
Windows cells rejected newline-sensitive metadata assertions and POSIX-only
staging expectations. The Python lane rejected a retention fixture against a
different Python microversion. Two Lean-lane H2 custody checks omitted the
new H3 manifest additions from their historical reconstruction. Native and
accepted-render artifacts were not produced because that Lean job failed.

The follow-up repairs preserve strict metadata values, the actual Windows
custody refusal, the frozen primary runtime and the immutable historical H2
receipts. Template staging also requires tracked symlink targets and referents
to remain bound to its pinned Git tree through retention. Fresh independent
review and actual final-source checks are required; historical passing tests
are never relabeled as acceptance for repaired source bytes.

The [remaining acceptance](specs/comprehensive-science-improvement/NEXT.md)
owns the current execution order: settle source and guidance, retain the
accepted isolated Q7 source pair, refresh catalogue native/export custody,
and run installed-wheel and hosted acceptance,
complete real production capture and two identical independently validated
package archives, then execute the frozen H3 study once and complete claims
and reproduction. The [locked protocol](specs/comprehensive-science-improvement/PROTOCOL.md)
retains all nine criteria. Private operator journals and active GNN registry
work are preserved; only explicitly reviewed public evidence is published.

H1.0--H1.8 are accepted, including the optional H1.5 lane. The archived
[Horizon 1 acceptance record](specs/done/horizon-1-finite-synthesis/README.md)
owns the implementation and review evidence. Its terminal theorem repairs the
first recorded H1.8 carrier-merge no-go with one finite, synthetic, one-step
posterior--decision--action certificate on a shared 16-state Boolean carrier.
The posterior update, emitted action, selected sampled kernel, genuine
sensory--active blanket factorization, and strict real/native KL decrease use
that same carrier and kernel. This is not transition-aware planning,
EFE-optimal control, physical thermodynamics, causal identification, empirical
validation, or a universal FEP theorem.

The archived [Horizon 2 spec](specs/done/horizon-2-smooth-stochastic/README.md) has
separately accepted H2.0--H2.3b, H2.4a/b, H2.5a/b/c/d, H2.5b-R0,
H2.5d-R0, H2.6a/b/c, and H2.6a-R0. The maintained surface now includes scalar
Gaussian/native-KL and coordinate owners, a same-joint native posterior
martingale and limiting-observation endpoint, selected-model identification,
joint-law and fixed-truth consistency, weak Dirac and bounded-risk
consequences, the native semigroup/H1 lift, exact scalar and finite-axis
symmetric-precision transition families, the
exact four-axis specialization, an evidence-a.e. native scalar filter with
chronological finite recursion, one-step transition-consuming quadratic
decision risk, and monotone finite-grid path laws with coordinate reversal
plus explicit absolute-continuity/integrability failure boundaries. The
accepted generic H2.5b-R0 transition-covariance and H2.6a-R0 native-posterior
repairs remain append-only evidence alongside their accepted maintained owners.
The accepted H2.5d-R0 repair proves the centered native stationary-joint
factorization. Maintained H2.5d now proves the arbitrary-center native joint,
blanket-a.e. pair/scalar Gaussian conditionals, endpoint `CondIndepFun`, actual
stationary covariance `1 / 24`, and a bounded bivariate precision perturbation
with actual covariance `-1 / 15` and native non-independence. H2.7-R0 accepted
the density-relative VFE and local natural-gradient proof gate. The baseline
terminal certificate validated 328 mandatory cases, the enabled Fin4 supplement
and three source-bound reviews.
Fresh H2 custody passed 329 mandatory cases and three independent source-bound
reviews before continuous G0 acceptance and the immutable
[H3.0 freeze](specs/h3-reference-study/freeze.json). That prerequisite packet
remains historical evidence after H3 opens its new source epoch. The
[reference study](specs/h3-reference-study/README.md) has native model and
cross-domain proofs at its retained source epochs. Current package repairs
require a fresh native export and three independent proof-role reviews before
scientific execution. Frozen primary seeds remain unopened pending package
acceptance; recovery, controls, final claims and bundle reproduction are open.
The empirical branch remains governed no-go without a licensed
named dataset.

Earlier coordinated projection and receipt refreshes, including the
2026-09-12 snapshot, remain recorded in [CHANGELOG.md](CHANGELOG.md).
Their historical completion does not determine today's receipt currency.
Keep native, declaration, Python, browser, numerical, manuscript, and provider
evidence planes separate.
The 2026-08-20 Hermes/OpenGauss report likewise remains historical for its
exact 50-topic source digest; current provider claims require a new,
independently validated source-bound full report.

The earlier evidence layer — Q5/Q6/Q7 artifact proofs, W2 source custody, the
v0.6 bridge contract (the W2 report records the v0.4 snapshot; contracts v0.5
and v0.6 added verify-document and the extraction-package render route), and
schema-2 receipts — is summarized in
[specs/gnn-bridge-w2-source-custody/WAVE2-REPORT.md](specs/gnn-bridge-w2-source-custody/WAVE2-REPORT.md).

## Reproduction commands

Run from the repository root:

```bash
uv sync --locked --extra dev
uv lock --check
uv pip check
uv run python scripts/_maint_build_topics_catalogue.py --check
uv run python scripts/_maint_build_fep_all_lean.py --check
uv run python scripts/_maint_build_formal_modules.py --check
uv run python scripts/theorem_maturity_audit.py --check
uv run python scripts/build_formalism_coverage.py --check
uv run python scripts/_maint_build_lean_landscape.py --check
uv run python scripts/build_formalism_atlas.py --check
uv run python scripts/build_formal_kernel_dashboard.py --check
uv run python docs/pin_audit.py --check-latest
uv run mypy src
uv run ruff check src tests scripts docs
uv run ruff format --check src tests scripts docs
(cd lean && lake build FepSketches)
uv run fep-lean verify --fail-on-warnings \
  --receipt output/native-verification.json
uv run python scripts/audit_formalisms.py \
  --receipt output/formalism-audit.json
uv run fep-lean catalogue
uv run python scripts/build_render_fonts.py --check
uv run python scripts/render_manuscript.py --check
uv run python docs/theorem_ref_audit.py
uv run python docs/citation_audit.py
uv run python docs/check_links.py --strict --include-root
uv run python docs/md_hygiene.py --strict
uv run python docs/xref_audit.py
uv run python scripts/capture_browser_acceptance.py
FEP_LEAN_TEMPLATE_DIR=<template checkout> \
  uv run python scripts/render_publication.py
uv run python scripts/check_render_log.py --verify-receipt
uv run python scripts/build_release_bundle.py --run-python-acceptance
uv run fep-lean preflight
git diff --check

release_a_dir="$(mktemp -d)"
release_b_dir="$(mktemp -d)"
archive_a="$release_a_dir/fep-lean-candidate-168.tar.gz"
archive_b="$release_b_dir/fep-lean-candidate-168.tar.gz"
SOURCE_DATE_EPOCH=0 uv run python scripts/build_release_bundle.py \
  --output "$archive_a"
SOURCE_DATE_EPOCH=0 uv run python scripts/build_release_bundle.py \
  --output "$archive_b"
cmp "$archive_a" "$archive_b"
sha256sum "$archive_a" "$archive_b"
SOURCE_DATE_EPOCH=0 uv run python scripts/build_release_bundle.py \
  --check --output "$archive_a"
SOURCE_DATE_EPOCH=0 uv run python scripts/build_release_bundle.py \
  --check --output "$archive_b"
```

The canonical Python-acceptance command runs the exact collected suite and
atomically writes `output/pytest.xml`, `output/coverage.xml`, and
`output/python-acceptance.json`; a raw `pytest` run is a useful development
gate but is not a release receipt. Catalogue/manuscript generation precedes
that receipt because `manuscript/manuscript_vars.yaml` owns the canonical test
count. Browser capture follows the final renderer sources and atlas/dashboard
bytes. The two archive builds must remain byte-identical and independently
validate against the live checkout before publication.

Independently validate the native receipt against the live source tree before
using its prose projection. The CI workflow contains the exact validation
snippet.

`render_publication.py` belongs in that sequence rather than beside it: it is
the only command that runs the fail-closed acceptance over a real render, and
the only one that writes `docs/render-acceptance.json`. CI's render lane
(`.github/workflows/ci.yml`, FEP-CI-RENDER) renders end-to-end -- the shared
template checkout, XeLaTeX, pandoc, `rsvg-convert`, the mermaid CLI, the two
preamble faces, the catalogue, then `render_publication.py` -- and validates
the fresh receipt against the same sources in the same run, but it cannot
commit a refreshed receipt back: only a local acceptance run can rewrite the
committed `docs/render-acceptance.json`. The fast lane verifies that
committed receipt (`ci.yml` `check_render_log.py --verify-receipt`), so a
chapter edited without a fresh local render leaves CI red there.

### Reading `render_receipt_freshness: stale` from `uv run fep-lean status`

One residue case is expected local behavior, not a defect. The committed
receipt `docs/render-acceptance.json` binds the generated
`manuscript/09z_unified_formalism_catalogue.md` (`.gitignore:58`). CI's
render lane validates a fresh receipt in-run but cannot commit it back, so
the committed receipt ages against local state. A status run that reports
`render_receipt_freshness: stale` naming ONLY
`09z_unified_formalism_catalogue.md` means the local generated appendix -- the
gitignored build product, not the maintained manuscript -- is absent or
differs from the bytes the shipped render accepted. A new worktree always
starts in the absent state. Run `uv run fep-lean catalogue` first: when the
catalogue inputs are unchanged since the accepted render, regeneration
reproduces the accepted bytes and clears the residue without a render. Only
when it persists after regeneration has the catalogue itself moved, and a full
render acceptance run is required before publication; while the residue is
local-only it blocks nothing else. The
[local render runbook](scripts/README.md#local-render-runbook) gives the
preparation, both checker diagnoses, and the render prerequisites.

A REAL defect looks different: stale findings naming committed manuscript
sources (chapters, the preamble, or other tracked `manuscript/*.md` files)
mean the shipped render predates maintained text and must not be treated as
current until `scripts/render_publication.py` re-runs over a real render and
rewrites the receipt.

## Historical external stage

`FEP-FULL-002` and `FEP-PROV-003` were closed for the earlier 50-topic snapshot
by its full report and artifact validation. That dated task closure is not a
current-roster acceptance receipt. The two earlier one-topic smokes remain
historical as well.

Never print, persist, or infer credentials from a successful run. A retained
receipt supports only the exact source digest and roster it records; it does not
authorize publication or establish the FEP as a physical theory.

## Next-review protocol

1. Read the nearest `AGENTS.md`, inspect `git status --short --branch`, and
   preserve unrelated or concurrent changes.
2. Edit maintained owners only; regenerate and inspect every projection.
3. Treat semantic-disposition changes as mathematical review, not as an
   automatic consequence of compilation.
4. Use direct import/declaration searches and relevant consumer tests for
   impact analysis; use an available repository index when useful. This review
   used focused tests, local orphan compile probes and independently validated
   hosted receipts; it did not perform a new native build.
5. Before any separately authorized publication, inspect the exact diff, run
   all applicable gates, commit intentionally, push, and verify remote parity.

The 2026-10-02 [Q7 post-guidance observation](specs/comprehensive-science-improvement/evidence/public-q7-current-doc-20261002-r1/summary.json)
passes all three read-only checks after independent prose review with unchanged
custody and native JSON, closing the portability probe. Later acceptance and
publication progress is recorded in the program's execution ledger; the dated
checkpoints above retain their original source epochs. Daniel has authorized
committing and pushing reviewed changes to `main` and publishing the next minor
release, `v1.4.0`, after its acceptance gates. The
[upcoming scopes](docs/design/fep-research-program/next-improvements.md) define
future minor, medium and major package/formal work separately from current
release obligations. Licensed-data access, paid provider fallback and account
settings still require their own authorized boundaries.
