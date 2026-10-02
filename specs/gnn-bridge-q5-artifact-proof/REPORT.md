# Q5: concrete PyMDP artifact proof

Historical local observation dated 2026-09-04. The then-selected schema-2
native receipt passed retained validation after source pinning, canonical
rendering, deterministic probe regeneration and native compilation. The
[retained native JSON](native_receipt.json) remains unchanged. Its source-bound
and delivery observations are historical after the W2 re-pin; Q7's new native
evidence does not supply current Q5 acceptance.

## Claim and scope

The five literal tables of the canonical symmetric PyMDP runner equal the independent Q2 payload and its carrier masses. A handcrafted asymmetric control agrees with its independent Lean payload.

No Python execution, general extractor/compiler correctness, or C/EFE equivalence is established.

## Retained evidence

- [Canonical render provenance](render_provenance.json) binds the actual renderer command, input/output bytes, source pin, and unchanged owners.
- [Generated proof manifest](generated/artifact_proof_manifest.json) binds extraction and probe generation separately from native evidence.
- [Native receipt](native_receipt.json) binds the immutable slice contract, shared engine, exact checked Python/probe buffers, recursive formal imports, resolved compiler binaries, commands, and native transcripts.
- The 2 positive probe(s) compiled without warnings or `sorryAx`; all 6 named theorem reports use only standard axioms.
- Dated reported receipt SHA-256: `4fc01a2a8ec03f850aa006b06b472263f9f30ed9d0213d07a729b7ec06647268`.
- Actual retained JSON SHA-256, read on 2026-10-02: `81264af09ce1bedd9553cfd2ea0bf8cd3caa134a08018ec0f667b063ed8c6b8d`. This file records historical compiler version `v4.34.0`; it is not rewritten to match the earlier report or current pin.

| Theorem | Native axiom result |
| --- | --- |
| `FEPProbe.Q5ArtifactProofAsym.asymArtifactTables_faithful` | standard axioms only |
| `FEPProbe.Q5ArtifactProofAsym.asymExpected_ne_symBoolPayload` | standard axioms only |
| `FEPProbe.Q5ArtifactProof.symArtifactTables_faithful` | standard axioms only |
| `FEPProbe.Q5ArtifactProof.symArtifact_aMass_eq_original` | standard axioms only |
| `FEPProbe.Q5ArtifactProof.symArtifact_carrierMasses` | standard axioms only |
| `FEPProbe.Q5ArtifactProof.symArtifact_statement5Pymdp` | standard axioms only |

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
uv run python specs/gnn-bridge-q5-artifact-proof/verify_native.py --compile --gnn-root "$GNN_ROOT" --receipt output/bridge/q5-native-candidate.json
uv run python specs/gnn-bridge-q5-artifact-proof/verify_native.py --check --gnn-root "$GNN_ROOT" --receipt output/bridge/q5-native-candidate.json
```

Use a fresh candidate path per capture and check that same candidate against
the same named GNN root; never overwrite the historical native JSON.
Default and `--check` validation are read-only. A source, contract, artifact,
import, or toolchain change invalidates the corresponding receipt. Content
custody assumes trusted local Python and toolchain binaries; it is not a sandbox
or independent host/compiler authentication. Publication and provider-backed
execution retain their separate acceptance requirements.
