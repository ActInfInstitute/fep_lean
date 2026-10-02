# Testing

Run from the project root:

```bash
uv run pytest tests/ -q --cov=src --cov-fail-under=89 -m "not serial_lean"
```

The suite uses real temporary files, SQLite databases, subprocesses, and local
HTTP servers. Environment variables isolate secrets and expensive external
integration tests; they do not manufacture successful execution results.

Required release gates are:

```bash
uv lock --check && uv pip check
uv run python scripts/_maint_build_topics_catalogue.py --check
uv run python scripts/_maint_build_fep_all_lean.py --check
uv run python scripts/_maint_build_formal_modules.py --check
uv run python scripts/theorem_maturity_audit.py --check
uv run python scripts/build_formalism_coverage.py --check
uv run python scripts/_maint_build_lean_landscape.py --check
uv run python scripts/build_formalism_atlas.py --check
uv run python scripts/build_formal_kernel_dashboard.py --check
uv run pytest tests/ -q --cov=src --cov-fail-under=89 -m "not serial_lean"
uv run mypy src
uv run ruff check src tests scripts docs
uv run ruff format --check src tests scripts docs
git diff --check
uv run python docs/check_links.py --strict --include-root
uv run python docs/md_hygiene.py --strict
uv run python docs/pin_audit.py --check-latest
uv run python docs/xref_audit.py
uv run python docs/theorem_ref_audit.py
uv run python docs/citation_audit.py
uv run fep-lean catalogue
uv run python scripts/build_render_fonts.py --check
uv run python scripts/check_render_log.py --verify-receipt
uv run python scripts/render_manuscript.py --check
uv run python scripts/build_manuscript_figures.py
uv run python scripts/build_manuscript_figures.py --check
```

Native formal acceptance additionally requires the pinned toolchain and
Mathlib build:

```bash
cd lean && lake build FepSketches
cd .. && uv run python scripts/audit_formalisms.py \
  --receipt output/formalism-audit.json
uv run fep-lean verify --fail-on-warnings \
  --receipt output/native-verification.json
```

Hermes/OpenGauss full validation additionally requires external credentials;
`fep-lean preflight` reports each missing capability without modifying the
workspace.

The atlas and dashboard tests validate deterministic projection and
accessibility contracts. The atlas visualizes authored provenance; the
dashboard visualizes selected finite examples. Neither is deductive evidence.
See [formal-kernel methods](formal-kernel-methods.md) for the evidence matrix.


## Installed-wheel runtime matrix

The `distribution` CI job uses a CPython 3.14 test harness and fresh target
environments for CPython 3.10--3.14 on Ubuntu, macOS, and Windows. It tests
installed API/catalogue loading, complete Lean/YAML resource parity, isolated
imports, CLI help, explicit checkout selection, and Q7's refusal before parsing
on unsupported validator interpreters. Runtime dependency resolution is
independent of the validator's locked environment. It does not reuse the
checkout or parent site-packages and does not compile Lean.

```bash
FEP_DISTRIBUTION_PYTHON=3.12 \
  uv run --locked python -m pytest tests/test_distribution.py -q -s --no-cov
```

The hosted matrix must pass before claiming its platform compatibility; a local
macOS run does not establish Linux or Windows acceptance. Versions after 3.14,
alternate interpreters, and native/full-mode acceptance on Windows remain
outside this matrix's evidence.

## Documentation and render CI boundaries

Root Markdown and `docs/` prose PRs run a read-only documentation gate after
materializing generated manuscript inputs. The classifier takes publication
inputs, receipts, font records, generated scientific projections, and source
changes through the full workflow. Its regression tests execute the actual
classifier against real temporary Git histories. No Lean build is scheduled
for the prose-only PR lane; main pushes still run full integration.

The render lane uploads accepted products only after fail-closed acceptance
and freshness checks. The same-SHA artifact includes the PDF and logs, receipts,
font/renderer provenance, source hashes, and artifact hashes. Source drift or a
missing required output prevents upload. Retained CI evidence must be validated
against the live source and intended SHA before import or publication; it is
never a substitute for the release gates above. See the
[retained-render procedure](development.md#documentation-prs-and-retained-renders).

## Transport and capability deadlines

Hermes reads successful and HTTP error bodies inside the same wall-clock
deadline worker with the same byte limit. The loopback probes exercise slow
200/403/503 streams, oversized success/error bodies, and preserved ordinary
HTTP error status and excerpts; they use no provider credentials or external
endpoint. A failed diagnostic body preserves an already observed HTTP status
and its authentication/rate-limit policy. Failures without a known HTTP error
status remain typed transient transport failures.

Gauss doctor and Lean/Lake version checks use the existing process-group runner
on POSIX. Real child/grandchild probes verify that deadlines stop both
generations and release inherited pipes, while preserving the optional-doctor
result policy. These process-tree probes do not establish Windows native
acceptance.

## Publication capture controls

The focused capture tests run real disposable producer/check processes and the
existing numerical witness owner. They cover repeated resume, selective DAG
invalidation, source changes and directory membership changes, retained prior
and partial artifacts, tampered history, path containment, one budget across
failed reuse and recapture, and two-archive parity with strict validator controls.
Planning is tested with process creation forbidden, including the public CLI.

```bash
uv run python -m pytest tests/test_release_bundle.py -q \
  -k publication_capture --no-cov
uv run python -m pytest tests/test_subprocess_watchdog.py -q --no-cov
```

The shared supervisor's POSIX controls launch an actual outer worker, a nested
shared-helper session and its grandchild. They test outer timeout and worker
crash cleanup, inner timeout preserving its caller, normal output/exit behavior
and unrelated-session survival. Raw detached sessions that bypass the helper
remain outside descendant cleanup; post-cancellation pipe drain is bounded.
Other platforms have direct-child cleanup only.

Capture custody controls race an actual final-file or ancestor symlink swap
against descriptor reads and journal writes. Unsupported capture platforms
refuse before journal creation or process launch. The installed-wheel matrix
executes disposable capture, nested helpers and selective resume on POSIX;
on Windows it checks the typed capture rejection while exercising the supported
package, resource and CLI surfaces.

These controls establish the capture mechanism. Current production acceptance
requires executing the complete explicit capture DAG against frozen current
inputs, retaining its strict native/audit/Python/render/browser evidence and
both accepted archives. Focused tests, static readiness and an old journal do
not substitute for that execution.
