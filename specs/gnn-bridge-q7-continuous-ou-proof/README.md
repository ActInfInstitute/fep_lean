# Q7: fixed scalar OU artifact and coefficient-error certificate

This slice connects a current canonical GNN JAX render of the P4b scalar OU
document to exact real one-step coefficients and bounds the error of its six
embedded binary64 parameters. The retained [native receipt](native_receipt.json)
is historical and remains unchanged. The [updated proof report](REPORT.md)
separates that earlier record from the accepted isolated recapture r3 and
seven-stage postcapture closure r2. The exact new native receipt is retained
under the scientific improvement evidence directory, with native claim ready
and runtime execution unverified. Guidance/source currency still requires fresh
read-only checks after this prose edit.

The exact source model is `FEPComposed.SmoothReferenceKernel.selectedDynamics`
(rate 1, center 0, diffusion variance rate 2), its unit-duration `selectedFilter`,
and its centered unit-variance `selectedPrior`. The independent expected contract
requires `a = Real.exp (-1)`, `q = 1 - a^2`, identity observation, unit observation
variance, and passive control. This is not Q3 prior-gauge denotation: F and Q are
consumed here. P4b's declared `[1,1]` prior mean and emitted length-one vector are
explicitly frozen representations, not a claim of Q3 `ContinuousConforms`.

The artifact extractor reads literal assignments without importing or executing
the runner. Decimal source text is retained as an exact decimal rational, while
the parsed finite Python binary64 value is separately retained as an exact
dyadic rational. These values are not equated. No claim of correctly rounded
`Real.exp` evaluation is made: P4b currently uses powers of a rounded constant.

The Lean probe uses the pinned `Real.exp_one_near_20` bound to prove independently
that the actual dyadic F and Q are within `10^-15` of their exact OU formulas.
It then bounds one-step mean error by `epsilon * abs mean`, variance error by
`(2 * variance + 1) * epsilon`, and the stationary variance defect by
`3 * epsilon`. A nonstationary witness has mean 1 and variance 2, so replacing
prediction by the prior cannot pass the same narrow approximation bound. A
scalar Joseph-update identity connects the exact real arithmetic formulas.

The bounds concern real arithmetic over decoded coefficients. They do not bound
JAX arithmetic, solve operations, sampling, or accumulated trajectory error.
This slice proves no compiler/extractor correctness, generic LGSSM equivalence,
continuous path, SDE solution, control theorem, or physical applicability.

`refresh_render.py --fep-root ... --gnn-root ...` retains a canonical render under
this slice with before/after owner digests and exact input bytes. It invokes
`extract_pomdp_from_file(strict_validation=True)` followed by
`POMDPRenderProcessor._pomdp_to_gnn_spec` and public `render_gnn_spec(..., 'jax', ...)`.
An initial discovery run found that the generic dispatcher rejected this model
at a categorical A/B/C/D requirement; the parent repaired the dispatcher and
the final retained fixture is refreshed through that generic public route.
It never executes the emitted runner. `generate_probe.py` creates the probe and
manifest; `generate_probe.py --check` compares bytes without writing. The parent
receipt engine owns source/toolchain/native custody and must check the manifest's
complete `receipt_contract` before accepting evidence. A generated manifest is
explicitly not native evidence.

The retained P4b `NUM_TIMESTEPS=1` observes the prior and never exercises F or Q:
`kalman_step(..., first=True)` skips prediction, and transitions run only for
`range(1, T)`. Separate numerical evidence must invoke `first=False` on a
nonstationary belief or use at least two samples. The GNN three-step nonstationary regression exercises that runtime route.
It remains execution evidence, distinct from the static coefficient proof.

## Interpreter contract for the frozen scaffold

The [schema-1 serialization protocol](scaffold-serialization.md) retains all
reviewed AST fields, types and order, with only absent/empty
`FunctionDef.type_params` normalized. Ordinary comments and locations are
excluded; type comments are retained. Unknown grammar, fields and nonempty
type parameters fail closed. The schema-2 expected contract explicitly binds
this serialization and the independently reviewed new scaffold digest.

The [runtime parity record](generated/scaffold-runtime-parity.json) observes
56,968 identical candidate bytes on real CPython 3.10.20, 3.11.15, 3.12.13,
3.13.15 and 3.14.4, with all 11 semantic/schema controls on each runtime.
The [canonical bytes](generated/scaffold-canonical.json) hash to
`b34a350a0c66bd611c19cd87e2343592c6ee7d15ed2fd6e422b1f891597febec`.
The earlier 62,013-byte `f8dfe844…` observation is historical for the fixture
before its NumPyro-only branch was removed from the canonical JAX output.
Reproduce those observations with installed runtimes, without network access:

```bash
uv run --locked python specs/gnn-bridge-q7-continuous-ou-proof/generate_probe.py \
  --record-scaffold-portability
uv run --locked python specs/gnn-bridge-q7-continuous-ou-proof/generate_probe.py --check
```

Candidate serialization parity is static syntax evidence. Actual
`scaffold_digest`, extraction and receipt validation still accept exactly
**CPython 3.14** and refuse unsupported interpreters before parsing. The
installed-wheel matrix checks both candidate parity and that refusal. Q5/Q6
whole-file custody has its own evidence boundaries. Their native and delivery
observations remain historical after the W2 source re-pin; this Q7 capture does
not refresh them. The previous Q7 native receipt is retained as history;
updating hashes cannot replace a new native capture.

Acceptance requires focused extraction/custody-negative tests, current render
provenance, exact probe regeneration, native compilation with no warnings or
`sorryAx`, and axiom reports containing only the established standard axioms.
The implementation is integrated; changes require fresh source-bound evidence.

## Current isolated native evidence and reproduction

The [public Q7 observation](../comprehensive-science-improvement/evidence/public-q7-closure-20261002-r1/summary.json)
records recapture r3 accepted across 12 stages in 644.5096 seconds: seven actual
accepted substages of failed r2 were freshly revalidated, and stages 8–12
actually ran in r3. All 124 pure
controls pass without skips. The isolated GNN pair owns its Git checkout and
private copied runtime at exact commit
`536d949829f6aed11dc540e5c5dec77578b25016`; all 703 owners are bound, with
191 FEP and 291 native owners guarded. The active GNN checkout/output remain
outside this isolated work.

The exact [new native receipt copy](../comprehensive-science-improvement/evidence/q7-accepted-native-retention-20261002-r1/native-receipt.json)
has SHA-256 `b0ecf640fffa06f019d67c74a2d02e22715120165a98d218d61f49f98366bc3b`.
It records `native_claim_ready: true`, `runtime_execution_verified: false`,
the warning-free positive probe and all 12 standard-axiom results.
The public observation also records postcapture closure r2 accepted across
seven actual stages in 1,648.1618 seconds, including the real positive
axiom census and both wrong-F/wrong-Q native controls. Its outer process exits
0 with accepted transport. The dated [post-guidance observation](../comprehensive-science-improvement/evidence/public-q7-current-doc-20261002-r1/summary.json)
records independent review and three passing read-only checks with stable source
custody; that acceptance closes the portability backlog probe.
Full operator-custody records remain local. The public summary is observational;
only the separately validated official native receipt supplies the native claim.

For a new coordinated capture, refresh the exact selected owners first. Use a
fresh candidate path and the same explicitly named GNN root for both commands;
never overwrite the historical `native_receipt.json`:

```bash
GNN_ROOT=/absolute/path/to/GeneralizedNotationNotation
uv run python specs/gnn-bridge-q7-continuous-ou-proof/verify_native.py \
  --compile --gnn-root "$GNN_ROOT" --receipt output/bridge/q7-native-candidate.json
uv run python specs/gnn-bridge-q7-continuous-ou-proof/verify_native.py \
  --check --gnn-root "$GNN_ROOT" --receipt output/bridge/q7-native-candidate.json
```
