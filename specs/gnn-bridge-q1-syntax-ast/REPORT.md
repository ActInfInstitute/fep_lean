# Q1 report — GNN syntax AST and decidable well-formedness

Slice: `specs/gnn-bridge-q1-syntax-ast` · Direction 2 phase Q1 ·
2026-09-03 · worker: Direction-2 (Q1).

## What was frozen

The Q1 syntax surface is frozen in [README.md](./README.md) ("Frozen Q1 syntax
surface"): normative base `GeneralizedNotationNotation/doc/gnn/gnn_syntax.md`
(GNN v1.1), evidenced by the four canonical exemplars under
`GeneralizedNotationNotation/input/gnn_files/{discrete,continuous}`. Five
required sections, eight optional sections as typed wrappers, at-most-once per
kind in canonical exemplar order, state-space declaration grammar (names over
alphanumeric + `_` + `π` + `'`, positive literal or name-reference dimensions,
`type=float|int|bool`, verbatim v1.1 `default=`), connection grammar
(`A>B`, `A-B`, optional `:label`). Deferred boundaries are listed in the same
section and mirrored in the spec's no-go register.

## What was implemented

- New foundation module `src/fep_lean/formal/gnn_document.lean`, namespace
  `FEP.GnnDocument`, projected byte-for-byte to
  `lean/FepSketches/gnn_document.lean` by
  `scripts/_maint_build_formal_modules.py`. It compiles on `import Init`
  alone — no Mathlib dependency, no `sorry`, no new axioms.
- AST: `GnnVersion`, `GnnSectionKind` (13 kinds, `rank` = frozen order),
  `GnnValueType`, `GnnDim` (lit/ref), `GnnDecl`, `ConnKind`,
  `GnnConnection`, `GnnParamEntry`, `GnnTimeEntry`, `GnnBinding`,
  `GnnParameter`, `GnnSection` (typed-wrapper sum type), `GnnDocument`.
- Decidable well-formedness: `documentWellFormed` (Bool) +
  `WellFormed` (Prop) with a `Decidable` instance, composed of
  `requiredSectionsPresent` (GNN-E001), `sectionsInCanonicalOrder`
  (rank-strictly-increasing = order + at-most-once), `declWellFormed` /
  `noDuplicateNames` (GNN-E004), `connectionWellFormed` (token grammar),
  `dimRefsResolve` (dimension references resolve to declared variables or
  `ModelParameters` keys — the decidable mechanical fragment),
  `connectionsReferenceDecls` (GNN-E003 strict),
  `parameterizationVarsDeclared` (GNN-W003 strict),
  `ontologyVarsDeclared`.
- Exemplar smoke values transcribed from all four exemplars:
  `actinfPomdpExcerpt`, `simpleMdpExcerpt`, `continuousNavigationExcerpt`,
  `predictiveCodingExcerpt`, plus `v11FeatureExcerpt` (`default=uniform`,
  annotated edges). Ten malformed variants each isolate one rule: missing
  required section, out-of-order sections, undeclared endpoint, bad label
  character, duplicate declaration, nonpositive dimension, unresolvable
  dimension reference, invalid section identifier, undeclared
  parameterization variable, undeclared ontology variable.
- Registration: one `FormalModule` row appended to `FORMAL_MODULES` in
  `src/fep_lean/formal/manifest.py` (foundation, `FEP.GnnDocument`); the
  pinned roster test `tests/test_formal_composition.py::
  test_formal_module_manifest_is_the_single_explicit_resource_roster` was
  extended with the same resource/module/namespace entry — the only
  non-additive edit, required by the manifest contract.

## Verification (evidence plane: native Lean compilation + repo gates)

- `cd lean && lake build FepSketches` — completed successfully (8761 jobs);
  a targeted rebuild of the touched module emits zero warnings, and grep of
  the build output finds no `warning`, `error`, `sorry`, or `axiom`.
- `lake env lean src/fep_lean/formal/gnn_document.lean` — silent (no errors,
  no warnings); all fifteen smoke decisions (`decide`) pass.
- `uv run python scripts/_maint_build_formal_modules.py --check` — OK.
- `uv run python scripts/_maint_build_fep_all_lean.py --check` — OK.
- `uv run python scripts/build_formalism_coverage.py --check` and
  `uv run fep-lean atlas --check` — regenerated
  (`docs/formalism-coverage.{json,md}`, `docs/formalism-atlas.{svg,html}`)
  after the roster change, then OK. `fep-lean dashboard --check` — OK
  (roster-independent).
- `uv run ruff check` / `ruff format --check` on touched Python files —
  passed; `uv run mypy src` — no issues in 71 source files.
- Focused pytest: `test_formal_composition.py`,
  `test_formal_foundations.py`, `test_formalism_coverage.py` — 33 passed.
  Remaining roster-consumer files — 104 passed, 8 failed, all in
  `test_formalism_audit.py`.
- Failure attribution (not this slice): those 8 tests fail because an
  uncommitted in-flight change by another worker
  (`git diff HEAD -- src/fep_lean/verification/formalism_audit.py`)
  replaced `subprocess.run` with `run_process_group`, which the module's
  hermetic tests do not intercept (they monkeypatch only
  `formalism_audit.subprocess.run` and `find_executable`). Proof: running
  `tests/test_formalism_audit.py` with an out-of-repo pytest plugin tha
  shims `formalism_audit.run_process_group` back through `subprocess.run`
  passes all 25 tests. The Q1 declaration closure is theorem-free-module
  safe: `test_probe_resolves_primaries_and_prints_evidence_axioms` (which
  asserts `imports == FORMAL_MODULES`) passes as-is. This slice neither
  owns nor repairs that refactor.
  Provenance (read-only git): `test_formalism_audit.py` is unmodified
  relative to HEAD, while `formalism_audit.py` carries the uncommitted
  refactor and `src/fep_lean/verification/_subprocess.py` (whose
  `run_process_group` executes probes via `subprocess.Popen`) is untracked —
  the refactor is concurrent-change interference owned by its author.

## Evidence firewall

Everything above establishes only that the AST and its decidable
well-formedness compile warning-free and decide the exemplar-derived samples
as specified. It establishes nothing about GNN pipeline behavior, model
semantics, or any catalogue/novelty/relation claim (bridge contract section 7;
README decision 7).

## Explicit follow-ups

- Full `input/gnn_files/` corpus transcription and decision (Q1 acceptance
  remainder; listed unchecked in the spec README).
- Version-gating decision for `default=`/`:label` under `GNN v1` vs `v1.1`
  (GNN-side question, per contract section 9).
- Numeric dimension/parameter consistency and ontology-term vocabulary
  predicate (Q2-facing slices).
