# Lean 4 workspace

The workspace pins `leanprover/lean4:v4.34.1` and the matching Mathlib
`v4.34.1` release, with `lean/lake-manifest.json` recording the exact Mathlib
revision those pins resolve to. These are exact reproducibility pins for the
newest stable Lean/Mathlib release pair, not floating aliases: release
candidates and nightlies do not replace the stable line. The networked pin
audit re-derives the newest valid pair from the live ecosystem against that
manifest: it checks Lean's stable releases in descending order and accepts
only the newest release with a validated matching Mathlib tag, so the audited
pins stay in step with what the workspace actually builds with. A newer Lean
release without that tag is reported as pending ecosystem support rather
than installed into an incompatible workspace.

The [v4.34.1 release notes](https://lean-lang.org/doc/reference/latest/releases/v4.34.1/)
describe the newest feature-bearing stable release. The workspace follows it
because Lean and the matching
[Mathlib4 v4.34.1 release](https://github.com/leanprover-community/mathlib4/releases/tag/v4.34.1)
are both available. A documentation page lag never justifies downgrading an
installed, verified stable release.

```bash
uv run fep-lean setup
uv run python docs/pin_audit.py --check-latest
uv run fep-lean verify --fail-on-warnings --receipt output/native-verification.json
uv run python scripts/audit_formalisms.py --receipt output/formalism-audit.json
cd lean
lake build
lake build FepSketches
```

## Lock-preserving setup

From a checkout synchronized with `uv sync --locked --extra dev`, use
`uv run --locked fep-lean setup` or
`bash scripts/_maint_bootstrap_lean_toolchain.sh`. Both use the same bounded
implementation. It validates the toolchain, Mathlib tag, and committed
manifest before acquisition, and checks that the pin triple and `uv.lock`
remain byte-identical after each subprocess. An explicit Lake executable
must report the pinned compiler version. Without Lake, setup uses elan to
install exactly the checkout's toolchain; set `FEP_LEAN_ELAN_EXE` if elan is
not on PATH. `ELAN_HOME` may point to a new empty directory. Set
`XDG_CACHE_HOME` or `MATHLIB_CACHE_DIR` to isolate downloaded cache artifacts
as well; setup forwards these locations to its acquisition subprocesses.

The underlying acquisition sequence is:

```bash
elan toolchain install "$(cat lean/lean-toolchain)"
cd lean
lake exe cache get
lake build FepSketches
```

Pinned Lake reads existing manifest revisions for these commands. It has no
uv-style `--locked` option. The guarded setup entry points are preferred over
running the commands by hand: Lake can generate a missing manifest, so setup
rejects missing/corrupt pins before Lake runs. It never invokes `lake update`
or ignores a failed cache acquisition. The setup deadline covers installation,
cache acquisition, and build together; timeout kills the subprocess group.
A cache failure is a failure, not authorization for an unbudgeted source build.

On a pin error, inspect `git diff -- lean/lean-toolchain lean/lakefile.lean
lean/lake-manifest.json uv.lock`. Preserve intentional edits, then restore
these files together from the intended reviewed commit and rerun setup. Do
not repair ordinary setup with `lake update`. If a consistent reviewed pin
set still fails, retain the command log and diagnose the acquisition/toolchain
failure before changing dependencies. Setup reports unexpected pin drift
and stops; it does not overwrite user changes to hide drift.

To check idempotency, record SHA-256 hashes of those four files, run setup
twice with one isolated `ELAN_HOME`, compare all three hash snapshots, and
require zero tracked pin diff. Then run
`uv run --locked fep-lean verify --topic fep-001 --fail-on-warnings` and record
the actual compiler version and `.lake/packages/mathlib` Git revision. Keep
separate Linux and macOS receipts; one platform's result does not establish
the other's. This smoke does not replace full native receipt validation.

## Deliberate toolchain upgrades

When a newer compatible stable pair appears, update both canonical pins, run
`lake update` and the Mathlib cache acquisition, migrate every warning or
compiler error in canonical sources, and regenerate the native and formalism
receipts. CI and the scheduled latest-stable workflow reject a stale compatible
pair; they do not silently select a different compiler.

Canonical topic bodies live in family modules under
[`src/fep_lean/catalogue/bodies/`](../src/fep_lean/catalogue/bodies/).
[`registry.py`](../src/fep_lean/catalogue/registry.py) validates and merges them,
and [`latex.py`](../src/fep_lean/catalogue/latex.py) projects theorem signatures.
The tracked aggregate
[`lean/FepSketches/fep_all.lean`](../lean/FepSketches/fep_all.lean) is regenerated with
[`scripts/_maint_build_fep_all_lean.py`](../scripts/_maint_build_fep_all_lean.py).
CI rejects regeneration drift, proof holes, and Lean warnings in the aggregate.

Reusable foundations and cross-topic theorems have separate canonical owners
under [`src/fep_lean/formal/`](../src/fep_lean/formal/); the exact module set
and roles are declared in `manifest.py`. Leaf modules under `compositions/` own
proofs that consume multiple stable topic namespaces, while `composed.lean` is
their import-only aggregate.
[`scripts/_maint_build_formal_modules.py`](../scripts/_maint_build_formal_modules.py)
projects every manifested Lean source byte-for-byte into `lean/FepSketches/`.
For a dependency-ordered navigation map of the formal modules, see
[`lean-landscape.md`](lean-landscape.md), generated by
[`scripts/_maint_build_lean_landscape.py`](../scripts/_maint_build_lean_landscape.py)
(with a `--check` freshness gate).
Formal
relations in `config/formalism_relations.yaml` must name a qualified declaration
from this or another canonical module. The formalism audit resolves all primary
and semantic-evidence declarations and runs `#print axioms` over every one. A
zero exit code is insufficient: the receipt requires one parsed axiom result
per declaration, normalizes hard-wrapped Lean messages, binds actual Lean and
the resolved Mathlib revision, and rejects missing output, stale projections,
warnings, `sorryAx`, or axioms outside the versioned trusted set (`propext`,
`Classical.choice`, `Quot.sound`).

The [formal-kernel methods](formal-kernel-methods.md) page explains the
probability, information, active-inference, blanket, geometry, and convergence
contracts and why projection, build, audit, native receipt, visualization, and
full-run evidence remain distinct.

## Catalogue source of truth {#catalogue-source-of-truth}

Metadata, semantic review, novelty records, and the family body registry are
maintained separately and joined strictly by the schema-2 roster seal.
`config/topics.yaml` and packaged `src/fep_lean/data/topics.yaml` must be
byte-identical. The strict loader checks the generated schema before execution.

## Cursor Lean 4 commands {#cursor-lean4-commands}

Use the canonical local commands above. Editor integrations should invoke the
same pinned Lake workspace rather than a separately discovered compiler.

## Mathlib4 modules used in fep_lean {#mathlib4-modules-used-in-fep_lean}

Each canonical body declares the narrow Mathlib modules it needs; the generated
coverage map records distinct modules and topic-to-import edges. The metadata
`mathlib` field is a navigation hint and is not accepted as import evidence.

`LeanVerifier` writes only transient `_verify_*.lean` files beneath
`lean/FepSketches/`; these are removed after each compilation.
