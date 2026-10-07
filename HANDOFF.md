# fep_lean formalism and publication handoff

**Date:** 2026-10-07
**Repository:** `ActiveInferenceInstitute/fep_formal`
**Checkout:** this repository checkout (see the `origin` remote)
**Release line:** `v1.6.0` (2026-10-07); the previous published release is
`v1.5.0` (2026-10-06), which ships the untagged `1.4.0` candidate. Releases follow the short
[release procedure](docs/release.md); research lanes below do not block them.

## Mathematical methods release line

The `1.6.0` release line adds a portable `fep_lean.methods` API and CLI,
a greatly extended mathematical supplement, and an offline explorer with
publication panels. [Integration ownership and acceptance](specs/openai-math-methods/INTEGRATION.md)
define this scope; [the guide](docs/mathematical-methods.md) explains its use.
The authored positioning policy is interpretive family context. Exact topic
contracts and typed theorem relations retain their canonical owners. The
OpenAI mathematics corpus is a pinned comparison source; none of its research
code is executed by this integration. The model retains 1,946 lexical Lean
declarations and twelve upstream statement passports against 82 locked file
identities. Its common comparison has 34 rows in 30 authored coordinates;
family context unions and individual upstream results retain distinct scope.
The 17-product export includes thirteen SVGs. Focused mathematical
tests passed 112 cases, and isolated installed methods checks passed on local
macOS Python 3.10.20, 3.11.15, 3.12.13, 3.13.16 and 3.14.4 with identical MDS
projection hashes. The original candidate, before integration with newer GitHub main, has
independently validated 168-topic native evidence. The final 385-page PDF passed the version-2 receipt and
independent publication reviews, with twelve Supplement A figures, six tables
and 55 numbered supplement equations. The complete non-serial Python suite
passed 2,707 tests with nine skips in 777.82 seconds and 91.50% coverage.
The first full Python run failed with 78 failures, 2,626 passes and nine skips;
its fixture repairs passed focused controls before the successful final run.
That candidate wheel's 193 package resources match its source; its source
archive has 338 checked regular members. That exact wheel passed isolated
Python 3.14.4 installation, all 17 API/CLI exports, nonmutating checks and the
reference MDS digest. The original 80-case distribution matrix and security
assertions remain; its shared fixture producers were migrated to receipt
version 2. Prior accepted artifacts remain historical.
[The validation record](specs/openai-math-methods/VALIDATION.md)
binds those local lanes. Reacquire evidence after source changes, and apply
the separate hosted release gate to the final committed source. Historical
custody and scientific-study records retain their scope.

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

Provider credentials must stay out of versioned and public artifacts. Versioned publication does not
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

Daniel resumed implementation on 2026-10-05 and authorized updating the scoped
work and pushing verified versioned changes to main. The [30-item open
backlog](TODO.md) records current release blockers, separately governed lanes
and minor/medium/major future improvements. Each item retains its dependencies,
acceptance criteria and claim boundary; resumption supplies no new acceptance.

Source main was `14fe6bab8fdcf27b0d7d457e1fdb923afffba83b`, independently
matching remote before these scoping documents. Its
[hosted run](https://github.com/ActiveInferenceInstitute/fep_formal/actions/runs/37376897900)
completed with 19 successful jobs, one failed Python job and one skipped docs
job. All 15 distribution cells passed 80 cases each. Hosted Python recorded
2,483 passed, two failed, 15 skipped and 90.87% coverage; the two failures were
Chrome startup without a usable CDP port within 15 seconds. Cause is unproved.
Hosted Lean serial recorded 557 passed and five skipped. Native/audit/render
passed in that run, but the whole run failed. Historical green `c99e933` and
later focused results remain their original source epochs.

The actual local r6 production capture closed naturally on
2026-10-05 at 23:46:49 UTC, integer exit 1, no timeout, after 7,275.3362 seconds.
Native, formalism audit, render, Python and numerical stages were accepted by
its controller. Browser failed with `live Chrome DOM observations are not
canonical`; bundle was unattempted. Python recorded 2,488 passed, 12 skipped,
90.84% coverage and 1,745.78 seconds. Whole acceptance is false. The seven
browser output hashes were unchanged from earlier artifacts and are not fresh
failed-run browser evidence. Failed journals/raw streams and closed operator
packets are preserved privately. No cancellation or accepted-prefix promotion
occurred. [Hosted startup](https://github.com/ActiveInferenceInstitute/fep_formal/issues/46) and
[local DOM rejection](https://github.com/ActiveInferenceInstitute/fep_formal/issues/51) have separate scopes.

The independently reviewed
[2026-10-05 Q7 observation](specs/comprehensive-science-improvement/evidence/public-q7-current-source-20261005-r1/summary.json)
passed twelve stages and four closing checks in 1,199.3769 seconds, binding its
recorded 291-input native roster. The public observation is not itself a native
receipt or validation of this checkout; later source-owner changes require fresh
source-pair acceptance. Historical Q5/Q6/Q7 receipts remain unchanged;
generated-runner execution remains unverified. The future
[isolated runner lane](https://github.com/ActiveInferenceInstitute/fep_formal/issues/61) cannot relabel this static evidence.
Preserve concurrent active GNN work and use only a specifically named isolated
pair if that lane is activated.

The retained r7-r1 materializer review is **REVISE**; its compatible observer
has source-only approval. That checkpoint established no r7-r2 execution. The
exact known
[roster gap](https://github.com/ActiveInferenceInstitute/fep_formal/issues/52) is
`tests/fixtures/formalism_catalogue_155_reviewed_deltas.json`: actual native
planning bound 141 test members while the outer frozen set included 140.
Review this tracked fixture and any new tests explicitly before enforcing
complete membership around imports, planning, dispatch and closure. Preserve
all 560 existing frozen inputs plus approved additions, all reviewed public
paths, native 291/scientific 293 distinctions, caps and no-resume policy.

The bounded PR45 adaptation passed all nine separate cases after independent
source review, preserving the byte-identical original 80-case distribution
matrix. Its pinned test-only validator rejects tampering, and concurrent real
PDF renders produced byte-identical PDF and provenance. The guidance corrections
passed independent source review and strict links, hygiene and xrefs. CUR-02
and CUR-04 leave the open backlog; their delivery is recorded in CHANGELOG.md.
The browser repairs passed 82 local cases without skips and independent source
review, but fresh production browser capture and hosted startup acceptance
remain open. Do not blindly merge substantive PR44/45.

Release `v1.5.0` publishes the 168-topic tree. H3 primary output
has not been opened and its seeds remain unused. The
[immutable protocol](specs/h3-reference-study/preregistration.yaml) and
[implementation gates](specs/h3-reference-study/IMPLEMENTATION.md) require
actual accepted package evidence, current native export and three independent
proof-role reviews before the sole primary invocation. Outcome reviews,
42-array replay, two study archives and clean installed reproduction follow.
Governed empirical no-go remains valid without licensed data. Optional current
Hermes/OpenGauss execution has separate bounded spend authorization; secure
credential/model routing, preflight and enforceable spend controls remain
prerequisites. No current provider acceptance is established here.

These guidance and implementation edits create a new source epoch for future
capture.
Later truthful outcome-prose edits also require honest final-source acceptance;
they never authorize repeating or relabeling the primary. The original
[nine criteria](specs/comprehensive-science-improvement/PROTOCOL.md) and
[final audit](https://github.com/ActiveInferenceInstitute/fep_formal/issues/59) keep all required evidence planes explicit.

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
   impact analysis; use an available repository index when useful. Retained
   reviews record their own focused tests, local orphan compiles and hosted
   receipt validation; a guidance refresh does not imply a new native build.
5. Before any separately authorized publication, inspect the exact diff, run
   all applicable gates, commit intentionally, push, and verify remote parity.

The 2026-10-02 [Q7 post-guidance observation](specs/comprehensive-science-improvement/evidence/public-q7-current-doc-20261002-r1/summary.json)
passed all three read-only checks after independent prose review with unchanged
custody and native JSON, closing portability for those recorded inputs. That
observation remains historical. The 2026-10-05 source-pair capture closed the
later Q7 currency requirement for its recorded inputs without promoting earlier
receipts; later owner changes require fresh validation.
Later acceptance and publication progress is recorded in the program's
execution ledger; the dated
checkpoints above retain their original source epochs. Daniel has authorized
committing and pushing reviewed changes to `main`; versioned releases follow
the [release procedure](docs/release.md). The
[upcoming scopes](docs/design/fep-research-program/next-improvements.md) define
future minor, medium and major package/formal work separately from current
release obligations. Licensed-data access, provider routing/spend enforcement
and account settings retain their separate boundaries.

## Copyable continuation prompt

> Continue FEP Formal from this handoff. Daniel resumed implementation and
> authorized verified versioned changes to be pushed to main on 2026-10-05.
> Read AGENTS.md, TODO.md, this handoff, the original nine-criterion protocol,
> NEXT.md and the immutable H3 preregistration/freeze. Inspect actual main and
> remote state, preserve concurrent edits and use native subagents with disjoint
> ownership. The local operator handoff contains private closed packet copies;
> keep them out of public Issues, commits and generated artifacts.
>
> Settle both browser failures independently, then finish the bounded test and
> guidance edits against the reviewed source candidates and actual diffs.
> Preserve the fixed original 80-case matrix and separate nine-case additions.
> Correct the complete tests-roster guard and obtain fresh independent review
> before imports/planning/dispatch. Execute all seven real production stages
> within original caps and independently validate two identical package archives.
> Complete five local installed-wheel runtimes, 184-resource parity and installed
> read-only status, preserving 15 GiB before launch and every cell. Run every
> applicable AGENTS check and final-SHA hosted 15-cell/Python/Lean/docs/render
> acceptance. Canonical validation remains CPython 3.14; no pin upgrade or
> dependency acquisition belongs to read-only checks.
>
> Bind accepted package/native/axiom/Q7 evidence to current H3 export and three
> independent Lean/domain/statistical proof-role reviews. Only then execute the
> unchanged frozen primary once: same continuous branch, seeds, counts, gates,
> controls, budgets and 42-array roster. Retain complete acceptance or scientific
> rejection, pure replay, three outcome reviews, two identical valid study
> archives and clean installed reproduction. No rerun, reseed, threshold change,
> carrier substitution or unsupported physical/empirical claim is allowed.
> Outcome-prose changes need honest final-source capture without relabeling the
> primary's actual package or repeating it. Empirical no-go is valid without
> licensed data; optional provider execution retains its separate spend boundary.
>
> Have an independent nonauthor map all nine criteria to exact final-source
> receipts, including truthful static status and FORM-1–FORM-3 boundary/semantic
> acceptance. Cut later versioned releases through docs/release.md
> (`docs/release_check.py --hosted`); report unrun lanes as unrun. Do not change
> account settings, force-push, erase history or touch active GNN work.
>
> Activate future minor/medium/major Issues only after their stated predecessors
> and concrete stop/go probes. Keep canonical owners, thin orchestration,
> configurability, manuscript and accessible visuals unified; never infer
> scientific disposition from compilation or numerical agreement. Report exact
> changes, commands, results and deferred gates. Remove completed TODO rows only
> after their own acceptance and record delivery facts in changelog/history.
