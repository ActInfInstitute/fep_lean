# Q6: concrete Julia embedded-input proof

Historical local observation dated 2026-09-04. The then-selected schema-2
native receipt passed retained validation after source pinning, canonical
rendering, deterministic probe regeneration and native compilation. The
[retained native JSON](native_receipt.json) remains unchanged. Its source-bound
and delivery observations are historical after the W2 re-pin; Q7's new native
evidence does not supply current Q6 acceptance.

## Claim and scope

The embedded JSON tables of two canonical Boolean Julia runners agree with independently authored symmetric and asymmetric Lean payloads. Both canonical render routes have retained source provenance.

The runner transforms C and does not consume E in its action selector. These are raw-input equalities, not consumed-C, package-agent, Julia runtime, or EFE equivalence.

## Retained evidence

- [Canonical render provenance](render_provenance.json) binds the actual renderer command, input/output bytes, source pin, and unchanged owners.
- [Generated proof manifest](generated/artifact_proof_manifest.json) binds extraction and probe generation separately from native evidence.
- [Native receipt](native_receipt.json) binds the immutable slice contract, shared engine, exact checked Python/probe buffers, recursive formal imports, resolved compiler binaries, commands, and native transcripts.
- The 2 positive probe(s) compiled without warnings or `sorryAx`; all 5 named theorem reports use only standard axioms.
- Dated reported receipt SHA-256: `adcb65c953d00f32e4ff4f7923f91ba4629f6e9928ee9cff770418b5c22e4bed`.
- Actual retained JSON SHA-256, read on 2026-10-02: `8d680a73bd68f23562169110b23c813c7544aa73e8c0ffbce798ff18b780da01`. This file records historical compiler version `v4.33.1`; it is not rewritten to match the earlier report or current pin.

| Theorem | Native axiom result |
| --- | --- |
| `FEPProbe.Q6JuliaEmbeddedInputAsym.asymEmbeddedInput_eq_expected` | standard axioms only |
| `FEPProbe.Q6JuliaEmbeddedInputAsym.asymExpected_differs_from_Q2` | standard axioms only |
| `FEPProbe.Q6JuliaEmbeddedInput.symEmbeddedInput_Q2_carrierMasses` | standard axioms only |
| `FEPProbe.Q6JuliaEmbeddedInput.symEmbeddedInput_Q4_conditional` | standard axioms only |
| `FEPProbe.Q6JuliaEmbeddedInput.symEmbeddedInput_eq_Q2` | standard axioms only |

## Regression evidence

At the dated wave-2 epoch, Q6 passed both positive probes and the normalized previous/action-axis rejection.
Q7 passed its positive 12-theorem census and both wrong-coefficient rejections.
Its initial notation-scope and tactic-linter defects were repaired without
changing theorem statements, bounds, or warning policy. The independent read-only
review confirmed that scope and the repair. Q5's native regressions passed in
the frozen full baseline; its schema-2 receipt was then freshly compiled.

That historical integrated nonserial Python suite passed 1,460 tests with seven skips,
529 native deselections, and 89.83% coverage. See the
[coordinated wave-2 report](../gnn-bridge-w2-source-custody/WAVE2-REPORT.md) for
exact test scopes, source-freeze evidence, and the separate H2 acceptance record.

## Reproduction

Follow [the slice README](README.md) to refresh canonical rendering and regenerate
probes after source changes. Native compilation is explicit and serialized:

```bash
GNN_ROOT=/absolute/path/to/GeneralizedNotationNotation
uv run python specs/gnn-bridge-q6-activeinference-artifact/verify_native.py --compile --gnn-root "$GNN_ROOT" --receipt output/bridge/q6-native-candidate.json
uv run python specs/gnn-bridge-q6-activeinference-artifact/verify_native.py --check --gnn-root "$GNN_ROOT" --receipt output/bridge/q6-native-candidate.json
```

Use a fresh candidate path per capture and check that same candidate against
the same named GNN root; never overwrite the historical native JSON.
Default and `--check` validation are read-only. A source, contract, artifact,
import, or toolchain change invalidates the corresponding receipt. Content
custody assumes trusted local Python and toolchain binaries; it is not a sandbox
or independent host/compiler authentication. Publication and provider-backed
execution retain their separate acceptance requirements.
