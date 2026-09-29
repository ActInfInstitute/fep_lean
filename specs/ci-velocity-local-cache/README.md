# CI-velocity local cache slice

Purpose: make repeat local verification fast by reusing the worktree-local
`lean/.lake` state across worktree resets. `lean_cache.py` wraps any local
verify-class command with a content-keyed snapshot of `lean/.lake`.

## Safety model

- The store holds **only derived Lake build outputs**. Custody receipts under
  `output/` and `specs/` are never cached; custody gates stay unconditional,
  uncached steps.
- The cache key is a sha256 over the bytes of `lean/lean-toolchain`,
  `lean/lakefile.lean`, and `lean/lake-manifest.json`, so a pin change selects
  a different snapshot instead of mixing states.
- Lake traces rebuild changed sources, so reuse cannot mask source drift.
- Unless `--skip-build` is passed, the wrapper runs `lake --wfail build
  FepSketches` after the cache fetch and before the wrapped command, mirroring
  CI's lean lane (cache-get → aggregate build → verify): `lake env lean`
  resolves `FepSketches.*` imports only through the built library, so a
  verify-class command without a built aggregate fails closed on every topic
  importing it.
- While a `lake`/`lean` process is already running, the wrapper refuses to
  start (exact-name precheck): concurrent Lake invocations in one worktree
  race the same `.lake` state.
- The pin triple is validated before any Lake invocation, mirroring the
  t-0058 guarded setup, and the snapshotted pin files (including `uv.lock`)
  are re-checked after the cache fetch and again after the wrapped command.
- Per the W4-PORTABLE-CHECKOUT/t-0058 finding, `lake --wfail exe cache get`
  is rejected as a failure on nonzero exit **and** on exit zero when the
  output carries the pinned cache CLI's terminal incomplete-cache verdict
  ("some files were not found in the cache") -- the same matcher upstream
  setup uses, so a recovered 404 retry inside an otherwise complete fetch
  does not false-fail a healthy run.

## Usage

```bash
# Default store, restore on hit, run the command, refresh on success:
uv run python specs/ci-velocity-local-cache/lean_cache.py -- uv run --locked fep-lean verify --fail-on-warnings

# Escape hatch: skip restore and refresh entirely:
uv run python specs/ci-velocity-local-cache/lean_cache.py --no-cache -- make lint

# Skip the aggregate pre-build (the wrapped command manages its own builds):
uv run python specs/ci-velocity-local-cache/lean_cache.py --skip-build -- uv run fep-lean catalogue

# Non-default store location (flag or environment):
uv run python specs/ci-velocity-local-cache/lean_cache.py --store /tmp/store -- echo ok
FEP_LEAN_CACHE_DIR=/tmp/store uv run python specs/ci-velocity-local-cache/lean_cache.py -- echo ok

# Print the computed content key (docs/CI debugging) and exit:
uv run python specs/ci-velocity-local-cache/lean_cache.py --key-print
```

Defaults: store is `$FEP_LEAN_CACHE_DIR`, else `~/.cache/fep-lean/lean-build`.
Unknown flags exit 2 with usage. Restore never clobbers an existing
`lean/.lake`; refresh rebuilds the snapshot after every successful run (cheap
APFS clones on darwin; on Linux the re-clone cost is accepted and documented).

## CI mirror

`.github/workflows/ci.yml` restores `lean/.lake/build` under a
`lean-build-v2-` key derived from the same three pin files (plus a per-commit
save suffix), matching the local store's key derivation on the pin inputs.
Source content hashes are deliberately excluded on both sides: Lake's own
content-hashed trace rebuild is what keeps a reused snapshot from masking
source drift.
