# Documentation contract

All documentation is local to this checkout. Keep links relative to the file
that owns them, keep toolchain/model claims synchronized with the canonical
configuration, and mark generated values as generated data.

The complete local check list is maintained in [testing.md](testing.md); the
release gate is [release.md](release.md), checked by `release_check.py`. The
documentation-specific gates from the project root are:

```bash
uv run python docs/check_links.py --strict --include-root
uv run python docs/md_hygiene.py --strict --include-root
uv run python docs/xref_audit.py
```

`--include-root` widens `check_links.py` and `md_hygiene.py` from `docs/**` to
every root `*.md`, every `AGENTS.md` / `README.md` under `src/`, `tests/`,
`config/`, `scripts/`, `lean/`, and `manuscript/`, and the non-historical
documents under `specs/`. Historical trees are explicitly excluded because
they are retained receipts: `specs/done/**`, `specs/**/evidence/**`,
`specs/**/gnn_output*`, `specs/**/gnn-input`, and `specs/**/fixtures`. Repair a
broken link there by annotating the exclusion, never by rewriting the file.

Use `uv run fep-lean catalogue` to materialize manuscript variables and the
unified appendix before checking manuscript cross-references.

`formalism-coverage.*`, `formalism-atlas.*`, and
`formal-kernel-dashboard.*` are generated projections. Edit their canonical
catalogue, relation, formal-module, or renderer owners, never the generated
bytes. The dashboard is explanatory numerical evidence and never substitutes
for Lean compilation or the declaration/axiom audit.
