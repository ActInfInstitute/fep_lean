# fep_lean/src/

**Version**: v1.6.0 | **Status**: Active | **Last Updated**: October 2026

The installable package is rooted at `src/fep_lean/`; `src/` is only the
standard packaging layout and is not itself importable.

## Directory Structure
The package is divided into eleven domain subpackages. The public root
`fep_lean/__init__.py` re-exports the stable high-level entrypoints. There are
no compatibility modules named `catalogue`, `pipeline`, or `output`.

| Subpackage | Responsibility | Key Exports |
|---|---|---|
| `fep_lean/catalogue/` | Typed semantic and catalogue model | `FEPTopicCatalogue`, `SemanticDisposition` |
| `fep_lean/methods/` | Portable mathematical positioning and boundary diagnostics | `build_mathematical_positioning`, `inspect_topic` |
| `fep_lean/formal/` | Packaged cross-topic Lean resources | `formal_projection_drift` |
| `fep_lean/verification/` | Lean 4 / Lake verification and declaration audit | `LeanVerifier`, `run_formalism_audit` |
| `fep_lean/gauss/` | OpenGauss SQLite & Runner | `OpenGaussClient`, `GaussRunner` |
| `fep_lean/llm/` | LLM API interface (Hermes) | `HermesExplainer`, `HermesConfig` |
| `fep_lean/output/` | Evidence and artifact generation | `validate_native_lean_receipt`, `build_formalism_atlas`, `Reporter` |
| `fep_lean/pipeline/` | Orchestration (4-stage DAG) | `FEPPipeline`, `run_pipeline`, `run_single_topic` |
| `fep_lean/bridge/` | Explicit GNN custody and interchange | `pin_sources`, `emit`, `verify_document` |
| `fep_lean/custody/` | Evidence census, staged refresh and resume | `census`, `verify`, `Census` |
| `fep_lean/prove2me/` | Explicit authenticated remote formalization | `Prove2meConfig`, `Prove2meClient` |

## Imports

Internal modules use qualified subpackage imports for modularity:

```python
from fep_lean.catalogue import FEPTopicCatalogue
from fep_lean.verification import LeanVerifier
```

The `fep_lean.*` namespace is required both from a checkout and an installed
wheel. Tests include an isolated wheel/import/CLI smoke to pin that contract.

## See also

- [../AGENTS.md](../AGENTS.md)
