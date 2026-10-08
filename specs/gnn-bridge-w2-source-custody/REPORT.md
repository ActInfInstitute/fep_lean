# W2 source custody delivery — wave-1 record

The current implementation and receipts are documented in the
[wave-2 delivery report](WAVE2-REPORT.md). The details below record the earlier
wave-1 snapshot; its former hashes and counts are historical.

Verified locally on 2026-09-04. The bridge now checks explicit source owners,
emitted documents, and numerical receipts without silently rewriting evidence.
The shared implementation is `src/fep_lean/bridge/`; legacy P1, P3, P4b, and W1
scripts delegate to that implementation.

## Behavior and custody

`fep-lean bridge pin --gnn-root PATH` records the actual owner roster and SHA-256
of working-tree bytes. Git commits remain descriptive: FEP
`b9d315cb448a7e3c8e54a6e4b26c78aef929d73a`, GNN
`64d49355acf197a0570b06ab334d97570774be64`. Both checkouts contained existing
uncommitted work. Neither commit alone identifies the tested implementation.
The retained [source pin](source-pin.json) owns that distinction.

Owner additions, deletions, missing files, escapes, symlinks, and changed bytes
invalidate the pin. Emission compiles the verified emitter source buffer,
avoiding timestamp-valid cached Python bytecode. The pin and emitted documents
are excluded from their own digest inputs. Only the four unique permitted
Signature custody fields can be refreshed; all other text, order, and
multiplicity remain part of content equality. Individual output files use
atomic replacement and preserve mtimes when bytes already match.

The finite and continuous documents were explicitly emitted from this pin.
Read-only status reports all six checks passing: source binding, finite
freshness, continuous freshness, syntax surface, contract mirror, and formal
projection. Both documents report `FRESH`.

## Evidence

- `tests/test_gnn_bridge_operations.py` and `tests/test_subprocess_watchdog.py`:
  **55 passed**. These cover content/custody tampering, numeric policy validation,
  CLI errors, legacy behavior, and actual subprocess deadline behavior.
- Ten actual read-only commands returned zero: bridge status, both emitter
  checks, certificate verification, both legacy emitter checks, W1 status,
  legacy P3 comparison, Q5 generation check, and Q5 native receipt check.
  Fifteen retained files had identical SHA-256 and nanosecond mtimes before
  and after. Local evidence: `/tmp/gnn-fep-readonly-final.json`.
- A comparison receipt was explicitly written to
  `output/bridge/w2-numerical.json` and independently validated. Its identified
  historical P3 results pass the numerical comparisons, while
  `execution_source_verified` and `native_claim_ready` both remain `false`.
  A current source pin does not prove that historical execution used it.
- Strict mypy passed for ten bridge/extractor/verification files. Full FEP
  source Ruff passed. Native artifact evidence has its own
  [Q5 report](../gnn-bridge-q5-artifact-proof/REPORT.md).

## Boundaries

This delivery establishes bridge custody and deterministic operations. It does
not verify arbitrary Python extraction, execute the retained PyMDP runner,
establish C/EFE equivalence, or accept continuous dynamics. ActiveInference.jl
artifact proofs follow separate backend work. The
[H2 terminal audit](../done/horizon-2-smooth-stochastic/readiness/07-terminal-audit-20260904.md)
does not close wider H2 acceptance or open H3.

The pre-existing W1 REPORT was preserved byte-for-byte. No baseline files were
deleted and neither repository HEAD changed. Final aggregate validation and
cross-repository delivery are recorded in each repository's ISA and the GNN
coordinated delivery report.
