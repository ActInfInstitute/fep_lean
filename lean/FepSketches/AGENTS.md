# `lean/FepSketches/` contract

Generated Lean library root. Do not hand-edit any `.lean` file here.

- `fep_all.lean` — whole-catalogue target, built from the body registry by
  `scripts/_maint_build_fep_all_lean.py`.
  Check: `uv run python scripts/_maint_build_fep_all_lean.py --check`
- `composed.lean`, `compositions/*.lean`, and the foundation/leaf modules — byte-exact
  projections of the manifested package resources (`src/fep_lean/formal/manifest.py`),
  built by `scripts/_maint_build_formal_modules.py`.
  Check: `uv run python scripts/_maint_build_formal_modules.py --check`

Change the owning body, manifest, or generator, then regenerate. Verifier-owned
temporary probes (`_verify_*.lean`) are created and removed by `LeanVerifier`; never
commit them. See [../AGENTS.md](../AGENTS.md) for the workspace contract.
