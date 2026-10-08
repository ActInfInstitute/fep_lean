# `fep_lean.methods` contract

- `model.py` owns source resolution (installed package data or an explicit
  checkout), strict YAML loading, policy and cross-corpus validation, the
  immutable `MathematicalPositioning` model, and the exact-query functions.
- `probes.py` owns the deterministic numerical boundary probes and the
  fixed-precision `classical_mds`. It imports nothing from `fep_lean`.
- `projection.py` owns the JSON and Markdown renderers, the combined artifact
  byte map, atomic export, and the non-mutating drift check.
- `visualization.py` owns the visual model, SVG panels, and the offline
  `mathematical-map.html`. It is not re-exported from `__init__.py`; import
  its names from `fep_lean.methods.visualization`.

This package is offline and non-proof. Do not add a Lean declaration, native
receipt, Hermes/OpenGauss call, upstream execution, or scientific promotion.
Declaration resolution is source-text validation, never compilation. Feature
proximity, MDS coordinates, and probes must never create a relation edge or
witness. `build_mathematical_positioning` reads owner bytes and must refuse
(raise `PositioningError`) when they disagree with the imported runtime
snapshot or change during analysis. Do not weaken the duplicate-key YAML
loader. Exports go through `atomic_write_bytes`; `mathematical_positioning_drift`
must stay read-only and must not create the output directory.

Generated copies under `src/fep_lean/data/` are byte copies of the canonical
`config/` and `specs/openai-math-methods/positioning.yaml` owners; refresh them
with `specs/openai-math-methods/generate_package_methods.py`, never by hand.
Changing any `methods/*.py` file changes the owner hashes it validates against.

```python
from fep_lean.methods import (
    BoundaryProbeError,
    MathematicalPositioning,
    PositioningError,
    SourceOrigin,
    analyze_topic,
    bernoulli_fisher,
    build_mathematical_positioning,
    classical_mds,
    cross_corpus_embedding,
    evaluate_boundary_probes,
    export_mathematical_positioning,
    extended_kl,
    finite_kl_totalized,
    inspect_family,
    inspect_theorem,
    inspect_topic,
    mathematical_positioning_bytes,
    mathematical_positioning_drift,
    package_resource_drift,
    positioning_neighbors,
)
```

The CLI branch is `fep-lean methods {inspect,neighbors,probe,analyze,theorem,embedding,export,check}`.
It needs no checkout (installed data is used); `export` writes only under
`--output-root`, and `check` is read-only. Test in
`tests/test_mathematical_methods.py` (import surface also in
`tests/test_subpackage_imports.py`; slice tests in
`specs/openai-math-methods/test_*.py`). The existing export tests write to
`tmp_path`; follow that.

See [README.md](README.md), [../AGENTS.md](../AGENTS.md),
[../../../docs/mathematical-methods.md](../../../docs/mathematical-methods.md),
and [../../../specs/openai-math-methods/README.md](../../../specs/openai-math-methods/README.md).
