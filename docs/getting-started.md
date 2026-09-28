# Getting started

These are checkout workflows. Keep `.python-version`, `pyproject.toml`,
`uv.lock`, `config/`, the canonical and projected formal resources, and the
`lean/` pin triple together. The wheel packages the catalogue but still needs
an explicit source checkout for configuration, verification, and publication.
Outside that checkout, put the global option before the subcommand:

```bash
fep-lean --project-root /path/to/fep_formal catalogue
```

## Catalogue-only tier

Install uv and use Python 3.14, the validator version in `.python-version`.
The packaging floor in `pyproject.toml` is not the validator contract. From
the checkout root:

```bash
uv sync --locked --extra dev
uv run --locked fep-lean catalogue
uv run --locked fep-lean atlas --check
uv run --locked fep-lean dashboard --check
```

Dependency installation requires network access unless already cached. Once
installed, catalogue mode is offline and needs no Lean, Hermes, OpenGauss,
provider credentials, donor cache, or coordinator tooling. Its report records
zero verified topics. The atlas is a structural view; the dashboard is
numerical, non-proof evidence.

## Native Lean tier

Add elan, Git, and access to the pinned Lean release and Mathlib cache hosts.
The following installer source is pinned to the same commit as CI; elan then
acquires the exact Lean toolchain recorded in the checkout:

```bash
curl -sSf https://raw.githubusercontent.com/leanprover/elan/0e36a07b9bbcc5381fa6250df109f9a4f94d7bac/elan-init.sh -o elan-init.sh
sh elan-init.sh -y --default-toolchain none
export PATH="$HOME/.elan/bin:$PATH"
uv run --locked fep-lean setup
uv run --locked fep-lean verify --topic fep-001 --fail-on-warnings
```

`setup` preserves the checked-in pins and uses a total deadline of 1800
seconds, configurable with `FEP_LEAN_SETUP_TIMEOUT_SEC`. The shell entry point
`bash scripts/_maint_bootstrap_lean_toolchain.sh` delegates to the same setup
implementation. Neither entry point updates the manifest. See
[the pinned acquisition and repair procedure](lean4.md#lock-preserving-setup).
An empty `ELAN_HOME` is supported; elan must already be installed or supplied
via `FEP_LEAN_ELAN_EXE`. Cache acquisition can require several gigabytes and
several minutes. Do not copy another checkout's `.lake/packages` as a recipe.

After setup, the maintained formal kernel and catalogue have distinct checks:

```bash
uv run --locked python scripts/_maint_build_formal_modules.py --check
(cd lean && lake build FepSketches)
uv run --locked python scripts/audit_formalisms.py --receipt output/formalism-audit.json
uv run --locked fep-lean verify --fail-on-warnings --receipt output/native-verification.json
```

The build checks projected formal modules; the audit resolves declarations
and their axioms; `verify` compiles canonical topic bodies. A one-topic smoke
is evidence for that topic only. Full native receipt validation belongs to a
settled source snapshot. None of these requires Hermes or OpenGauss. See
[formal-kernel methods](formal-kernel-methods.md).

## Publication-render tier

Add the shared rendering-template checkout, its matching project registration,
XeLaTeX/TeX packages, pandoc, `rsvg-convert`, the mermaid CLI, and the fonts
selected by `manuscript/preamble.md`. Pass a real template path explicitly;
a symlink into a deleted worktree is not a portable dependency.

```bash
uv run --locked fep-lean catalogue
uv run --locked python scripts/build_manuscript_figures.py
uv run --locked python scripts/build_render_fonts.py --probe
uv run --locked python scripts/render_publication.py --template /path/to/template
```

Follow the
[local render runbook](../scripts/README.md#local-render-runbook) for template
registration, font diagnostics, acceptance, and diagnosing a local
`check_render_log.py --verify-receipt` failure without paying for an
unnecessary render: it separates missing generated inputs from real
manuscript-source drift. A successful native build is not render acceptance,
and generated manuscript values are not native proof.

## External full-mode tier

Add configured Hermes and OpenGauss, including the provider credentials for
`OPENROUTER_API_KEY` or the configured Anthropic-compatible Hermes endpoint.
Keep credentials outside the checkout. Native setup alone does not provide
these services.

```bash
uv run --locked fep-lean preflight
uv run --locked fep-lean run
```

`preflight` is read-only. `setup` acquires Lean dependencies; normal verification
does not install them. A failed full run returns nonzero and creates no
successful report. Full success requires every selected result to compile
without `sorry` or warnings; `review` also requires its prose-review stage.
A complete selected-topic run is not automatically a full-catalogue,
publication-ready receipt.

Checkout portability does not resolve Q7's interpreter-dependent scaffold
serialization: its Python 3.14 guard and custody contract remain unchanged.
