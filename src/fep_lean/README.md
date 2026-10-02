# `fep_lean`

The installable Python namespace for the FEP Lean catalogue and verification
pipeline.

- `catalogue/`: family-owned canonical bodies, validated registry, typed
  semantic review, package data, and deterministic coverage projections
- `formal/`: packaged foundations, leaf cross-topic compositions, import
  aggregate, and exact Lake projection
- `verification/`: pinned Lean/Lake checks, native compilation, and
  declaration/axiom auditing
- `llm/`: Hermes provider client
- `gauss/`: SQLite session storage and per-topic runner
- `pipeline/`: catalogue and strict full-mode orchestration
- `output/`: evidence receipts, reports, figures, manuscript variables,
  fail-closed rendering, the offline formalism atlas, and the formal-kernel
  validation dashboard

Use public imports such as:

```python
from fep_lean.catalogue import FEPTopicCatalogue
from fep_lean.output import (
    build_formal_kernel_dashboard,
    build_formalism_atlas,
    validate_native_lean_receipt,
)
from fep_lean.verification import LeanVerifier, run_formalism_audit
```

The wheel intentionally provides no obsolete top-level compatibility modules.

## Interpreter contract

`requires-python = ">=3.10"` declares the packaging floor. The isolated wheel
checks install real dependencies into fresh environments outside the checkout,
verify API/resource parity and CLI behavior, and exercise CPython 3.10–3.14.
The 2026-09-30 local macOS checks pass that interpreter set; Ubuntu and Windows
use the declared CI matrix and need their own hosted result before a platform
acceptance claim. See [development](../../docs/development.md) for the boundary.

Development and evidence validation remain pinned to CPython 3.14 in
`.python-version`; mypy's 3.12 target is a separate static setting. Q7's current
`ast.dump` scaffold contract explicitly refuses unsupported interpreters before
parsing. That guard limits Q7 evidence validation, not installation or ordinary
catalogue API use. The authorized version-stable scaffold replacement and
coordinated custody re-pin remain open in [TODO.md](../../TODO.md).
