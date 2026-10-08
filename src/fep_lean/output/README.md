# Output and evidence projections

This package owns deterministic artifacts and typed evidence boundaries:

- `evidence.py` builds and independently validates native Lean receipts;
- `formal_kernel_dashboard.py` evaluates deterministic finite witnesses and
  renders the offline validation dashboard;
- `formalism_atlas.py` projects canonical coverage into offline SVG and HTML;
- `manuscript.py` builds variables and exact generated appendices;
- `rendering.py` resolves manuscript variables without mutating sources;
- `figures.py` creates deterministic catalogue figures; and
- `reporter.py` writes hash-bound catalogue/full report bundles.

The atlas consumes `build_formalism_coverage`; it never invents edges or infers
scientific dependency from imports. Use `write_formalism_atlas` to generate and
`atlas_projection_drift` to validate the tracked views.

The dashboard also consumes the coverage metrics, but its curves are numerical
diagnostics rather than theorem evidence. Each of the seventeen family witnesses
owns typed equality, inequality, or predicate checks with per-check tolerances;
a panel passes only when their conjunction and its boundary observation pass.
Use `write_formal_kernel_dashboard` to generate the SVG/HTML pair and
`formal_kernel_dashboard_drift` to validate the tracked bytes.

Receipts and projections are not interchangeable. A visualized node is not a
compile claim, a native topic receipt is not full-mode evidence, and a report
must pass its own independent validator.
