# fep_lean

`fep_lean` is a standalone catalogue of 168 Free Energy Principle, Active
Inference, Bayesian Mechanics, Information Geometry, and Thermodynamics topics.
Each row contains a reviewed invariant, explicit assumptions, a Lean 4 theorem
body, and typeset signatures. The pinned Lean workspace is the compilation
authority; the semantic review separately records how far each theorem reaches
toward its topic label. The schema-2 roster spans 22 reviewed families in five
areas and is a versioned interface, not an exhaustive census of the FEP
literature. The families include five second-expansion families for
finite-sample risk, closed-loop policy trees, native blanket transfer, finite
exponential-family dual geometry, and exact two-state continuous time, plus
standalone EFE and geometric-mechanics families.

## Release

Source metadata is `1.3.0`, and the [existing `v1.3.0` tag](https://github.com/ActiveInferenceInstitute/fep_formal/tree/v1.3.0)
records the earlier 159-topic cut. As checked on 2026-09-30, the latest
published GitHub release is [v1.2.0](https://github.com/ActiveInferenceInstitute/fep_formal/releases/tag/v1.2.0);
the current 168-topic `main` tree has not been published as a GitHub release.
The evolving scholarly record is identified by the
[Zenodo concept DOI](https://doi.org/10.5281/zenodo.19699233). The GitHub
release process must cross-reference the immutable Zenodo version DOI and
publish the release-bundle checksum; the bundle manifest owns per-file hashes.
Neither publication surface changes the evidence boundaries below.

## Contract

`full` execution is strict. It requires the pinned Lean/Lake/Mathlib workspace,
the `gauss` executable, configured Hermes credentials, and writable SQLite
state. Every selected row must compile without `sorry` or Lean warnings, and a
requested review workflow must complete its post-compile review turn.
**Missing capability or incomplete stage → `complete: false`, no report
directory.**

`catalogue` execution is deterministic and offline. It validates the complete
YAML source and writes figures, manuscript variables, the unified appendix, and
a report explicitly marked `catalogue`; it does not count topics as verified.

`verify` execution is Lean-only. It runs the sealed-roster native compile sweep
without Hermes or OpenGauss. Add `--receipt output/native-verification.json
--fail-on-warnings` to persist independently revalidatable native evidence.

`atlas` execution is deterministic and offline. It projects the canonical
coverage join into a standalone SVG and an interactive, keyboard-accessible
HTML graph; `--check` fails on missing or stale bytes. The graph distinguishes
derivational formal edges from checked formal pairings that place two endpoint
laws side by side without asserting implication. Both name qualified Lean
witnesses; conceptual and blocker edges remain visibly non-proof evidence.

`dashboard` execution is also deterministic and offline. It renders static
and interactive numerical witnesses for the expansion families. The
first ten cover Bayesian inversion, variational duality, control, temporal
inference, causal intervention, predictive coding, path thermodynamics,
categorical Fisher geometry, consensus, and finite concentration; the next
five cover Laplace/Brier risk transfer, policy-tree feedback, native blanket
conditional independence, exponential-family duality, and a two-state master
equation. Later witnesses cover standalone EFE and geometric mechanics.
These witnesses expose computational behavior and boundary cases but
never replace native Lean or axiom-audit evidence.

## Formal depth

The live formalism is organized into theorem-connected strands rather than a
headline theorem count: normalized finite probability and information
algebras, including support-free separation for the explicitly totalized finite
KL; posterior-form variational free energy and a uniquely attained evidence
lower bound; both expected-free-energy decompositions; a transition-consistent
infer--select--act joint and prior-sensitive Boolean policy witness;
stage-dependent cumulative finite-horizon EFE; finite Bayesian inversion,
variational duality, controlled and temporal inference, causal interventions,
and generalized predictive coding; path-space fluctuation identities and
reversible KL dissipation; categorical Fisher geometry, Cramér--Rao,
natural-gradient, mirror-descent, and replicator laws; collective inference;
finite concentration and model-evidence results; finite Laplace/Brier risk
transfer; observation-contingent policy-tree recursion and dominance; native
`CondIndepFun` blanket transfer; scalar exponential-family KL/Bregman duality;
and an exact two-state continuous-time semigroup, master equation, detailed
balance, relaxation, and Lyapunov law. The generated
[coverage report](docs/formalism-coverage.md) owns all current counts, and the
[atlas](docs/formalism-atlas.html) shows exactly which relations have Lean
witnesses. The semantic firewall requires every non-formalized row to expose
an explicit scope or assumption boundary. The reusable kernel is an explicit
manifest of foundations and leaf composition modules; `composed.lean` is only
their import aggregate. The maturity audit, rather than compilation alone,
records which rows are direct formalizations and which remain conditional or
structural proxies.

**Current evidence boundary.** The maintained catalogue spans 168 topics.
H1.0--H1.8 have exited through their accepted gates, with optional H1.5
accepted separately; the archived
[Horizon 1 record](specs/done/horizon-1-finite-synthesis/README.md) owns the
detailed evidence. Its terminal theorem is one finite, synthetic, one-step
posterior--decision--action certificate on a shared 16-state Boolean carrier.
The learned posterior, emitted action, sampled kernel, genuine sensory--active
blanket factorization, and strict real/native KL decrease remain connected on
that same carrier and kernel. The record also preserves the first H1.8
carrier-merge no-go. It does not establish transition-aware planning,
EFE-optimal control, physical or causal adequacy, empirical validation, or a
universal FEP claim.

The archived [Horizon 2 spec](specs/done/horizon-2-smooth-stochastic/README.md) has
accepted H2.0--H2.3b, H2.4a/b, H2.5a/b/c/d, H2.5b-R0, H2.5d-R0,
H2.6a/b/c, and H2.6a-R0. The current smooth surface includes fixed-variance scalar Gaussian
KL/information geometry, local coordinate duality, a same-joint native
posterior martingale with its limiting-observation conditional-expectation
endpoint, selected-model identification, joint-law and fixed-truth posterior
consistency, weak convergence to the sampled-parameter Dirac law,
bounded-continuous transfer, bounded zero-one risk convergence, native
kernel/action semigroups, exact scalar and finite-axis linear-Gaussian
transition families, the exact four-axis symmetric-precision specialization,
an evidence-a.e. native Gaussian filter with chronological finite recursion,
one-step transition-consuming quadratic decision risk, and monotone finite-grid
path laws with explicit support and log-ratio boundaries. The accepted R0
repairs preserve the historical H2.0 no-go rows while their maintained owners
derive the replacement mathematics. H2.5d-R0 reconstructs the centered Fin4
stationary joint. Maintained H2.5d extends that native conditional product to
every stationary center, proves blanket-a.e. pair and scalar conditional laws
plus endpoint `CondIndepFun`, and derives a fixed bivariate precision
perturbation with actual covariance `-1 / 15` and native non-independence.
H2.7-R0 has accepted the continuous density-relative exact-posterior VFE and
derived local natural-gradient seam. The [H2.7 terminal record](specs/done/horizon-2-smooth-stochastic/readiness/terminal-acceptance.json)
validates the mandatory cases, enabled Fin4 supplement, source hashes,
independent diagnostics, and source-bound reviews. Fresh H2 custody and
continuous H3.G0 acceptance preceded the immutable
[H3.0 protocol freeze](specs/h3-reference-study/freeze.json). The selected
[reference study](specs/h3-reference-study/README.md) now has compiled native
model and cross-domain proofs, a retained native export and three independent
proof-role reviews. Package repairs require a fresh final-source export and
review before opening the frozen synthetic seeds. Final claim review and
bundle reproduction remain open; empirical execution is governed no-go without
a licensed named dataset.

The 2026-09-30 [status review](SCOPE-2026-09-30.md) independently validated
the baseline CI native receipt at `cd4a84c` (168/168 topics, zero warnings or
`sorry`) and its 1,411-declaration axiom receipt against that source epoch.
The expanded local native r3 checkpoint separately verifies 168 topics against
291 unchanged owners; its audit covers 1,596 declarations with 1,465 evidence
records. These are distinct from hosted acceptance for the changed source and
from publication evidence. The local
full-report
path `output/reports/run_20260820_183143_709998/` was historical evidence
for the earlier 50-topic source snapshot and does not bind the current
source; that retained copy is no longer present under `output/reports/`, and
ignored provider reports are deliberately not shipped in a release.
The earlier Kimi and Gemini one-topic runs are historical smoke evidence as
well. No provider secret is stored in the
repository, and no execution receipt authorizes publication or proves the FEP
as a physical theory.

The isolated Q7 recapture now has accepted native coefficient evidence and
five-runtime scaffold parity; the [Q7 report](specs/gnn-bridge-q7-continuous-ou-proof/REPORT.md)
identifies the new retained receipt and actual positive/wrong-F/wrong-Q native
controls. It proves static coefficient statements with
`runtime_execution_verified: false`. Q5/Q6 native and delivery observations
remain historical after the W2 source re-pin; Q7 does not refresh them. Daniel's
active GNN checkout and output remain outside this isolated capture.

Local wheel r7 is historical after two guarded Q7 inputs changed and before
this guidance refresh. It contains five cells, each with one actual installed
target-runtime case and 32 CPython 3.14 harness cases (165 passes total).
Wheel r8 and the 15 hosted platform/interpreter cells remain unrun. The
2,303-pass, 90.66% canonical Python observation remains rejected by its wider
source guard; the repaired orchestrator has 11 focused passes. A fresh guarded
canonical Python run, render preparation, production capture, two identical
accepted archives and the frozen H3 primary remain open. The maintained
[handoff](HANDOFF.md) and [next acceptance list](specs/comprehensive-science-improvement/NEXT.md)
own the pending source-currency gates.

## Quick start

Run operator commands from a source checkout. Installed wheels support the
packaged `FEPTopicCatalogue.default()` API and `fep-lean --help`; substantive
commands deliberately require the checkout-owned configuration, Lean
workspace, and manuscript assets. From another directory, pass
`--project-root /path/to/fep_lean` before the subcommand.

```bash
uv sync --locked --extra dev
uv run python docs/pin_audit.py --check-latest
uv run fep-lean catalogue
uv run fep-lean atlas
uv run fep-lean dashboard
uv run fep-lean setup
uv run fep-lean verify --fail-on-warnings \
  --receipt output/native-verification.json
uv run fep-lean preflight
uv run fep-lean run
```

Use `uv run fep-lean --help` for filters, workflow selection, and the explicit
checkout root. The equivalent maintained scripts are thin command wrappers in
[`scripts/`](scripts/).

The operator command quick reference lives at
[`docs/quickref.md`](docs/quickref.md).

## Source of truth

- [`config/catalogue_metadata.yaml`](config/catalogue_metadata.yaml) maintains
  the stable roster's descriptive and Mathlib metadata.
- [`config/theorem_maturity.yaml`](config/theorem_maturity.yaml) maintains the
  semantic review independently of syntactic compilation maturity.
- [`config/formalism_novelty.yaml`](config/formalism_novelty.yaml) records every
  post-baseline topic's nearest predecessors, invariant, carrier delta, and
  required composition theorem.
- [`config/formalism_relations.yaml`](config/formalism_relations.yaml) maintains
  reviewed formal, conceptual, and blocker relations plus retained open,
  partial, and satisfied capability history. Shared imports never create
  scientific-dependency edges.
- [`src/fep_lean/catalogue/bodies/`](src/fep_lean/catalogue/bodies/) contains
  the family-owned Lean bodies;
  [`registry.py`](src/fep_lean/catalogue/registry.py) validates their canonical
  order and [`latex.py`](src/fep_lean/catalogue/latex.py) derives theorem
  signatures.
- [`config/topics.yaml`](config/topics.yaml) and
  [`src/fep_lean/data/topics.yaml`](src/fep_lean/data/topics.yaml) are generated,
  byte-identical catalogue projections; regenerate them with
  [`scripts/_maint_build_topics_catalogue.py`](scripts/_maint_build_topics_catalogue.py).
- [`lean/FepSketches/fep_all.lean`](lean/FepSketches/fep_all.lean) is the tracked
  aggregate generated by
  [`scripts/_maint_build_fep_all_lean.py`](scripts/_maint_build_fep_all_lean.py).
- [`src/fep_lean/formal/manifest.py`](src/fep_lean/formal/manifest.py) owns the
  formal-resource roster. Canonical cross-topic proofs live in
  [`formal/compositions/`](src/fep_lean/formal/compositions/), while
  [`composed.lean`](src/fep_lean/formal/composed.lean) is the import-only
  aggregate; all tracked Lake projections are generated by
  [`scripts/_maint_build_formal_modules.py`](scripts/_maint_build_formal_modules.py).
- [`docs/formalism-coverage.md`](docs/formalism-coverage.md),
  [`docs/formalism-atlas.svg`](docs/formalism-atlas.svg), and
  [`docs/formalism-atlas.html`](docs/formalism-atlas.html) are generated views
  of the same canonical semantic graph.

## Review contracts

- [`ISA.md`](ISA.md) defines the ideal state, anti-criteria, and evidence gates.
- [`TODO.md`](TODO.md) is the canonical open-only backlog with behavior-based
  acceptance probes.
- [`CHANGELOG.md`](CHANGELOG.md) records release changes and their evidence
  boundary.
- [`manuscript/04i_formalism_catalogue_155.md`](manuscript/04i_formalism_catalogue_155.md)
  states the five new families, theorem assumptions, non-vacuity witnesses,
  and evidence boundaries in one authored chapter.
- [`HANDOFF.md`](HANDOFF.md) gives the next reviewer the operating protocol,
  evidence pointers, and extension backlog.

## Development checks

The complete release-gate list is maintained as "Required release gates" in
[`docs/testing.md`](docs/testing.md); the quick local dev checks are:

```bash
uv run pytest tests/ -q --cov=src --cov-fail-under=89 -m "not serial_lean"
uv run mypy src
uv run ruff check src tests scripts docs
```

The reproducible build and publication gates (release-bundle determinism,
browser acceptance capture, receipt validation) are documented in
[`HANDOFF.md`](HANDOFF.md); setup and pipeline gates live in
[`docs/getting-started.md`](docs/getting-started.md) and
[`docs/pipeline.md`](docs/pipeline.md).

## Layout

| Path | Purpose |
| --- | --- |
| `src/fep_lean/catalogue` | typed semantic model, family-owned canonical bodies, generation, and coverage projections |
| `src/fep_lean/formal` | packaged foundations, leaf compositions, import aggregate, and workspace projection |
| `src/fep_lean/verification` | read-only capability checks, Lean compiler bridge, declaration/axiom audit, and GNN artifact-proof extraction and manifest verification |
| `src/fep_lean/llm` | configured Hermes HTTP client |
| `src/fep_lean/gauss` | SQLite sessions and per-topic orchestration |
| `src/fep_lean/output` | evidence receipts, fail-closed rendering, figures, reports, the offline formalism atlas, and the typed numerical dashboard |
| `src/fep_lean/pipeline` | strict `full` and explicit offline `catalogue` modes |
| `lean` | pinned Lake workspace and tracked aggregate |
| `manuscript` | source chapters and generated publication inputs |

## Notation

Lean identifiers are deliberately topic-prefixed (`fepNNN_*`) and should be
read together with the corresponding invariant and `assumption_review` in
`config/theorem_maturity.yaml`. The generated appendix renders exact theorem
signatures; prose notation is never an alternative source for the Lean API.
