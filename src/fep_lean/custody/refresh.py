"""The one sanctioned custody-refresh command, composing the settled phases.

``refresh`` composes the already-verified custody machinery in its
dependency-safe order and adds nothing new:

1. :func:`fep_lean.custody.census.census` — the read-only drift census.
2. :func:`fep_lean.custody.verify.verify` — the strict stop-gate against
   ``GATE_EXPECTATIONS``. A ``live-red`` record is never authorized; stale
   surfaces outside ``authorized_changes`` fail; a required surface missing
   from the census fails.
3. :func:`fep_lean.custody.apply.apply_refresh` — the settled 14-phase walk,
   writing only into the explicit staging tree.
4. The read-only verify set: the readiness matrix contract, the R0 custody
   successor validator, the terminal-acceptance validator, the diagnostics
   byte-equality probe, the custody test suites, the formalism audit
   receipt, and the pin audit.
5. The pre-capture owner gate: :func:`fep_lean.output.provenance.report_owner_errors`
   must return zero errors and the tip must be committed-clean before any
   native capture runs.
6. Optionally, the native Lean capture — fail-closed on every boundary: the
   subprocess exit code, post-capture rechecks (dirty tree, moved HEAD,
   owner drift), receipt presence, and an independent
   :func:`fep_lean.output.evidence.validate_native_lean_receipt` binding of
   the receipt to the live tree. A refresh report with a captured ``native``
   dict therefore implies a claim-ready receipt.

The known post-apply bridge cascade (source_binding FAILED naming an
authorized owner, freshness STALE) is reported as a warning with the
post-fold pin-cycle direction; it is never a failure and never remedied
here — pin cycles are coordinator-side.

Two orchestration modes reuse these gates and the same apply machinery
without ever running the verify-set subprocesses:

- :func:`plan_refresh` (``--plan``) — a read-only planning pass: reason,
  directories, dirty tip, HEAD, owner inventory, census, the mode verify
  gate (``GATE_EXPECTATIONS`` requireds plus the chore's ``--authorized``
  staleness set), the authorized-path roster check, and a direct
  matrix.yaml-toolchain-vs-lean-toolchain pin check. It writes the evidence
  journal and stops in state ``planned``.
- :func:`fixpoint_refresh` (``--fixpoint``) — the bounded staged fixpoint:
  round 1 stages from ``specs_dir``; every later round stages the previous
  round's flushed tree with the prior rounds' directive projections seeded
  into the walk. Convergence requires zero mutations, zero directives, and
  a byte-identical re-application into a throwaway directory; a repeated
  non-terminal state hash is a cycle and the round bound refuses. Terminal
  state ``awaiting-commit``; the staged candidate is the final round's
  flushed tree.

``--resume <journal-dir>`` is phase 3 and refuses with a clear stop in this
lane. Journals are schema-1 JSON files landed atomically under
``output/custody-journal/<operation-id>/`` (``--journal-dir`` overrides the
parent); ``--reason`` stays mandatory in every mode. Receipt re-issues the
fixpoint performs are dependency re-binds, not new execution evidence —
sealed historical observations are preserved.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from fep_lean.custody.apply import (
    DIAGNOSTICS,
    MATRIX,
    ApplyReport,
    PatchDirective,
    apply_refresh,
    dump_json_bytes,
)
from fep_lean.custody.census import census as census_from_tree
from fep_lean.custody.verify import GATE_EXPECTATIONS, Expectations
from fep_lean.custody.verify import verify as verify_gate
from fep_lean.output.evidence import validate_native_lean_receipt
from fep_lean.output.provenance import (
    report_owner_errors,
    source_owner_paths,
)

#: Receipt path for the optional native capture (cwd-relative convention).
NATIVE_RECEIPT = "output/native-verification.json"
#: Receipt path for the read-only bridge pin probe.
BRIDGE_PIN = "specs/gnn-bridge-w2-source-custody/source-pin.json"
#: Targeted custody suites (never the full battery).
CUSTODY_TEST_FILES = (
    "tests/test_horizon_acceptance.py",
    "tests/test_h3_preregistration.py",
)
#: Journal layout under the project root (``--journal-dir`` overrides it).
JOURNAL_DIR = "output/custody-journal"
#: The journal schema this lane writes; resume (phase 3) consumes it.
JOURNAL_SCHEMA_VERSION = 1
#: Default round bound for the staged fixpoint (``--max-rounds``).
DEFAULT_MAX_ROUNDS = 4
#: The plan-mode pin check this lane performs directly (the census/verify gate
#: never compares matrix.yaml's toolchain block against the live pin).
PLAN_PIN_CHECK = (
    "direct check: matrix.yaml toolchain.lean vs lean/lean-toolchain tail "
    "(the census/verify gate does not compare them)"
)


class RefreshRefused(RuntimeError):
    """A stop-gate, verify-set, or native-capture boundary refused the refresh."""


@dataclass(frozen=True)
class RefreshReport:
    """Outcome of one composed refresh, reported phase by phase."""

    reason: str
    authorized: tuple[str, ...]
    apply: ApplyReport
    verify_set: dict[str, Any]
    warnings: tuple[str, ...] = ()
    native: dict[str, Any] = field(default_factory=dict)


def _run(*command: str, root: Path) -> dict[str, Any]:
    """Run one fixed project command; never a mutation of custody surfaces."""
    result = subprocess.run(
        command,
        cwd=str(root),
        check=False,
        capture_output=True,
        text=True,
    )
    tail = "\n".join(((result.stdout or "") + (result.stderr or "")).splitlines()[-20:])
    return {"command": list(command), "exit_code": result.returncode, "tail": tail}


def _load_module(root: Path, relative: str, name: str) -> Any:
    """Load a standalone validator module by path, without package coupling."""
    path = root / relative
    if not path.is_file():
        raise RefreshRefused(f"validator module missing: {relative}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RefreshRefused(f"validator module unloadable: {relative}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _validate_terminal(root: Path) -> dict[str, Any]:
    from fep_lean.verification.horizon_acceptance import validate_terminal_acceptance

    accepted = validate_terminal_acceptance(root)
    return {
        "receipt_sha256": accepted.receipt_sha256,
        "mandatory_nodeids": len(accepted.mandatory_nodeids),
        "source_files": len(accepted.source_sha256),
    }


def _diagnostics_byte_equality(root: Path, specs_dir: Path) -> dict[str, Any]:
    """Recompute the diagnostics record; compare bytes against the live tree."""
    from fep_lean.verification.horizon_acceptance import diagnostic_record

    serialized = dump_json_bytes(diagnostic_record(root), relative=DIAGNOSTICS)
    live = (specs_dir / DIAGNOSTICS[len("specs/") :]).read_bytes()
    equal = serialized == live
    return {
        "path": DIAGNOSTICS,
        "byte_equal": equal,
        "detail": (
            "diagnostics.json byte-equals the recomputed diagnostic record"
            if equal
            else "diagnostics.json drifted from the recomputed diagnostic record"
        ),
    }


def _bridge_warning(root: Path) -> str | None:
    """Detect the known post-apply bridge cascade; read-only, never a failure.

    Without a GNN checkout the authoritative ``bridge status`` cannot run, so
    this probes the fep_lean half of the signature: live owner bytes vs the
    pin's recorded digests. Any mismatch is the authorized-edit cascade the
    coordinator's post-fold bridge pin cycle remedies.
    """
    pin_path = root / BRIDGE_PIN
    if not pin_path.is_file():
        return None
    try:
        pin = json.loads(pin_path.read_text(encoding="utf-8"))
        owners: dict[str, str] = pin["fep_lean"]["owners"]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return f"bridge pin unreadable ({BRIDGE_PIN}): {exc}"
    drifted = sorted(
        owner
        for owner, digest in owners.items()
        if not isinstance(digest, str)
        or not (root / owner).is_file()
        or hashlib.sha256((root / owner).read_bytes()).hexdigest() != digest
    )
    if not drifted:
        return None
    return (
        "bridge source binding is stale on: "
        + ", ".join(drifted)
        + " (freshness STALE cascade expected); run the post-fold bridge pin "
        "cycle (coordinator-side; this command never pins)"
    )


def refresh(
    specs_dir: Path,
    root: Path,
    output_dir: Path,
    authorized: tuple[str, ...] = (),
    reason: str = "",
    *,
    run_native: bool = False,
) -> RefreshReport:
    """Compose census → stop-gate → apply → verify set → optional native capture.

    The native tail is fail-closed: a nonzero capture exit, post-capture
    dirty/HEAD/owner drift, a missing receipt, or a receipt that is not
    claim-ready raises :class:`RefreshRefused`; no partial success is
    reported.
    """
    if not reason.strip():
        raise RefreshRefused("a non-empty --reason is required for the audit trail")
    if not specs_dir.is_dir():
        raise RefreshRefused(f"specs dir not found: {specs_dir}")
    if not root.is_dir():
        raise RefreshRefused(f"repo root not found: {root}")

    census = census_from_tree(specs_dir, root)
    ok, problems = verify_gate(census, GATE_EXPECTATIONS)
    if not ok:
        raise RefreshRefused("custody verify gate refused: " + "; ".join(problems))

    report = apply_refresh(
        specs_dir,
        root,
        output_dir,
        GATE_EXPECTATIONS,
        census=census,
        authorized_changes=authorized,
    )

    readiness = _load_module(
        root,
        "specs/done/horizon-2-smooth-stochastic/readiness/validate.py",
        "fep_lean_custody_readiness_validate",
    )
    h2_r0 = _load_module(
        root, "tests/_support/h2_r0_custody.py", "fep_lean_h2_r0_probe"
    )
    verify_set: dict[str, Any] = {
        "readiness": readiness.readiness_errors(root),
        "h2_r0_custody": h2_r0.validate_h2_r0_custody(root)["native_evidence"][
            "status"
        ],
        "terminal_acceptance": _validate_terminal(root),
        "diagnostics": _diagnostics_byte_equality(root, specs_dir),
        "pytest_custody": _run(
            "uv",
            "run",
            "--frozen",
            "--extra",
            "dev",
            "pytest",
            *CUSTODY_TEST_FILES,
            "-q",
            "--no-cov",
            root=root,
        ),
        "formalism_audit": _run(
            "uv",
            "run",
            "--frozen",
            "python",
            "scripts/audit_formalisms.py",
            "--receipt",
            "output/formalism-audit.json",
            root=root,
        ),
        "pin_audit": _run(
            "uv",
            "run",
            "--frozen",
            "python",
            "docs/pin_audit.py",
            "--check-latest",
            root=root,
        ),
    }
    failures = _verify_failures(verify_set)
    if failures:
        raise RefreshRefused("verify set failed: " + "; ".join(failures))

    warnings: list[str] = []
    bridge = _bridge_warning(root)
    if bridge is not None:
        warnings.append(bridge)

    native: dict[str, Any] = {}
    if run_native:
        owner_errors = report_owner_errors(root)
        if owner_errors:
            raise RefreshRefused(
                "pre-capture owner gate refused: " + "; ".join(owner_errors)
            )
        dirty = _git_dirty(root)
        if dirty:
            raise RefreshRefused(
                "native capture requires a committed clean tip; dirty: "
                + ", ".join(dirty)
            )
        head_before = _git_head(root)
        native = _run(
            "uv",
            "run",
            "fep-lean",
            "verify",
            "--fail-on-warnings",
            "--receipt",
            NATIVE_RECEIPT,
            root=root,
        )
        if native["exit_code"] != 0:
            raise RefreshRefused(
                f"native capture failed (exit {native['exit_code']}): "
                + native["tail"][:400]
            )
        dirty = _git_dirty(root)
        if dirty:
            raise RefreshRefused(
                "tree drifted during native capture: " + ", ".join(dirty[:5])
            )
        head_now = _git_head(root)
        if head_now != head_before:
            raise RefreshRefused(
                f"HEAD moved during native capture: {head_before} -> {head_now}"
            )
        owner_errors = report_owner_errors(root)
        if owner_errors:
            raise RefreshRefused(
                "owner drift during native capture: " + "; ".join(owner_errors)
            )
        receipt_path = root / NATIVE_RECEIPT
        if not receipt_path.is_file():
            raise RefreshRefused(
                f"native receipt missing after capture: {receipt_path}"
            )
        validation = validate_native_lean_receipt(receipt_path, project_root=root)
        if not validation["native_claim_ready"]:
            raise RefreshRefused(
                "native receipt is not claim-ready: "
                + "; ".join(validation["errors"])[:400]
            )
        native = {
            "command": native["command"],
            "exit_code": 0,
            "receipt": NATIVE_RECEIPT,
            "validation": {
                "claim_ready": True,
                "source_bound": validation["source_bound"],
                "live_catalogue_topics": validation["live_catalogue_topics"],
                "errors": [],
            },
        }
    return RefreshReport(
        reason=reason,
        authorized=authorized,
        apply=report,
        verify_set=verify_set,
        warnings=tuple(warnings),
        native=native,
    )


# ---------------------------------------------------------------------------
# Orchestration modes: read-only plan and the bounded staged fixpoint.
# Both reuse the census/verify-gate discipline and journal their evidence;
# neither ever runs the verify-set subprocesses or touches the live specs
# tree. The resume mode (phase 3) consumes the journals these modes write.
# ---------------------------------------------------------------------------


def _mode_gate(authorized: tuple[str, ...]) -> Expectations:
    """The plan/fixpoint verify gate: strict requireds plus the chore's
    authorized forced-change set.

    ``GATE_EXPECTATIONS`` itself is untouched; the mode gate keeps its
    required-intact surfaces, authorizes staleness only on the declared
    ``--authorized`` paths, and never authorizes a live-red record or a
    stale required surface (the comparator enforces both).
    """
    return Expectations(
        required_intact=GATE_EXPECTATIONS.required_intact,
        allowed_stale=frozenset(authorized),
    )


def _mode_gates(
    specs_dir: Path,
    root: Path,
    authorized: tuple[str, ...],
    reason: str,
    *,
    mode: str,
) -> dict[str, Any]:
    """Run the shared fail-closed pre-work gates for plan and fixpoint.

    Order is authoritative: reason, directories, dirty tip, HEAD, owner
    inventory, census, verify gate, pin check. The authorized-path roster
    check is plan-only (the fixpoint's authorized set is the chore's
    forced-change set, adjudicated by apply's drift ledger). Every refusal
    is a :class:`RefreshRefused` before any journal or staging write.
    """
    if not reason.strip():
        raise RefreshRefused("a non-empty --reason is required for the audit trail")
    if not specs_dir.is_dir():
        raise RefreshRefused(f"specs dir not found: {specs_dir}")
    if not root.is_dir():
        raise RefreshRefused(f"repo root not found: {root}")
    dirty = _git_dirty(root)
    if dirty:
        raise RefreshRefused(
            f"{mode} requires a committed clean tip; dirty: " + ", ".join(dirty)
        )
    head = _git_head(root)
    owner_errors = report_owner_errors(root)
    if owner_errors:
        raise RefreshRefused(f"{mode} owner gate refused: " + "; ".join(owner_errors))
    census = census_from_tree(specs_dir, root)
    gate = _mode_gate(authorized)
    ok, problems = verify_gate(census, gate)
    if not ok:
        raise RefreshRefused("custody verify gate refused: " + "; ".join(problems))
    _pin_toolchain_check(specs_dir, root)
    return {
        "head": head,
        "owner_errors": list(owner_errors),
        "owner_snapshot": _owner_snapshot(root),
        "census": census,
        "gate": gate,
        "stale": [record.path for record in census.stale()],
        "live_red": [record.path for record in census.live_red()],
        "pin_check": PLAN_PIN_CHECK,
    }


def _authorized_roster_check(root: Path, authorized: tuple[str, ...]) -> None:
    """Refuse authorized paths outside the reviewed source owners.

    A forced change must name a file the ownership manifest already reviews;
    anything else is unreviewed roster growth and is a coordinator decision,
    never this command's.
    """
    if not authorized:
        return
    roster = {path.relative_to(root).as_posix() for path in source_owner_paths(root)}
    unreviewed = sorted(
        path for path in authorized if Path(path).as_posix() not in roster
    )
    if unreviewed:
        raise RefreshRefused(
            "unreviewed roster growth: authorized paths outside the reviewed "
            "source owners: " + ", ".join(unreviewed)
        )


def _pin_toolchain_check(specs_dir: Path, root: Path) -> None:
    """Fail closed when matrix.yaml's toolchain block and the live pin diverge."""
    try:
        matrix = yaml.safe_load(
            (specs_dir / MATRIX[len("specs/") :]).read_text(encoding="utf-8")
        )
        toolchain = (root / "lean" / "lean-toolchain").read_text(encoding="utf-8")
    except (OSError, yaml.YAMLError) as exc:
        raise RefreshRefused(f"pin check unreadable: {exc}") from exc
    block = matrix.get("toolchain") if isinstance(matrix, dict) else None
    lean_pin = block.get("lean") if isinstance(block, dict) else None
    tag = toolchain.strip().rsplit(":", 1)[-1]
    if lean_pin != tag:
        raise RefreshRefused(
            f"pin/toolchain mismatch: matrix.yaml toolchain.lean {lean_pin!r} "
            f"!= lean/lean-toolchain {tag!r}"
        )


def _owner_snapshot(root: Path) -> list[dict[str, str]]:
    """Sorted source-owner paths with live digests (or a ``missing`` marker).

    The pre-work owner gate has already enforced ``report_owner_errors``;
    this snapshot is the resume mode's evidence of what the plan observed.
    A file the roster names but the tree lacks (only reachable under a
    stubbed gate in tests) is recorded as ``missing`` rather than hashed.
    """
    entries: list[dict[str, str]] = []
    seen: set[str] = set()
    for path in source_owner_paths(root):
        relative = path.relative_to(root).as_posix()
        if relative in seen:
            continue
        seen.add(relative)
        if path.is_file():
            entries.append(
                {
                    "path": relative,
                    "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
            )
        else:
            entries.append({"path": relative, "sha256": "missing"})
    return sorted(entries, key=lambda entry: entry["path"])


def _operation_id(pre_commit_head: str, reason: str, mode: str) -> str:
    """Deterministic within one run: sha256 over (head, reason, mode)."""
    payload = f"{pre_commit_head}\x1f{reason}\x1f{mode}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _persist_journal(
    journal: dict[str, Any],
    root: Path,
    operation_id: str,
    journal_dir: Path | None,
) -> Path:
    """Atomically land ``journal.json`` under the journal directory.

    ``journal_dir`` overrides the default ``root/output/custody-journal``;
    the operation id is always the last directory component so resume (phase
    3) can address a journal by its directory. The journal records its own
    landed path as evidence.
    """
    parent = journal_dir if journal_dir is not None else root / JOURNAL_DIR
    target = parent / operation_id / "journal.json"
    journal["journal_path"] = str(target)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.parent / f".{target.name}.{os.getpid()}.tmp"
    text = json.dumps(journal, indent=2, allow_nan=False) + "\n"
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, target)
    return target


def _directive_records(directives: tuple[PatchDirective, ...]) -> list[dict[str, str]]:
    return [
        {
            "path": directive.path,
            "phase": directive.phase,
            "anchor": directive.anchor.decode("utf-8", errors="replace"),
            "replacement": directive.replacement.decode("utf-8", errors="replace"),
        }
        for directive in directives
    ]


def plan_refresh(
    specs_dir: Path,
    root: Path,
    authorized: tuple[str, ...] = (),
    reason: str = "",
    *,
    journal_dir: Path | None = None,
) -> dict[str, Any]:
    """Read-only planning pass; the journal is the only artifact.

    No test/audit subprocess runs and the staged apply never runs: the plan
    composes the census comparator and the gate comparator only, both of
    which hash bytes without executing writers. Terminal state ``planned``.
    """
    gates = _mode_gates(specs_dir, root, authorized, reason, mode="plan")
    # Plan-only roster gate: a forced change must name a reviewed source
    # owner (no roster auto-growth). The fixpoint's authorized set is the
    # chore's forced-change set; its drift accounting is apply's ledger.
    _authorized_roster_check(root, authorized)
    journal: dict[str, Any] = {
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "mode": "plan",
        "reason": reason,
        "authorized": list(authorized),
        "pre_commit_head": gates["head"],
        "owner_snapshot": gates["owner_snapshot"],
        "owner_errors": gates["owner_errors"],
        "census": {
            "stale": gates["stale"],
            "live_red": gates["live_red"],
            "authorized": list(authorized),
        },
        "verify_gate": {"ok": True, "problems": []},
        "pin_check": gates["pin_check"],
        "phases": [],
        "state": "planned",
        "next_action": (
            "coordinator commit; then fep-lean custody refresh --resume <journal-dir>"
        ),
        "updated_at": _utc_now_iso(),
    }
    _persist_journal(
        journal, root, _operation_id(gates["head"], reason, "plan"), journal_dir
    )
    return journal


def _state_hash(specs_dir: Path, overlay: dict[str, bytes]) -> str:
    """sha256 over the sorted path→digest map of a fixpoint candidate state.

    The candidate is a staged specs tree (hashed under its ``specs/`` prefix)
    plus the carried directive projections for repo-side paths. A repeated
    hash means a round consumed a state it had already consumed.
    """
    entries: dict[str, str] = {}
    for path in sorted(specs_dir.rglob("*")):
        if path.is_file():
            relative = "specs/" + path.relative_to(specs_dir).as_posix()
            entries[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
    for relative, data in overlay.items():
        entries[relative] = hashlib.sha256(data).hexdigest()
    digest = hashlib.sha256()
    for relative in sorted(entries):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(entries[relative].encode("ascii"))
        digest.update(b"\0")
    return digest.hexdigest()


def _tree_bytes_map(tree: Path) -> dict[str, bytes]:
    return {
        path.relative_to(tree).as_posix(): path.read_bytes()
        for path in sorted(tree.rglob("*"))
        if path.is_file()
    }


def _reapplication_is_byte_identical(
    input_specs: Path,
    root: Path,
    round_dir: Path,
    round_census: Any,
    gate: Expectations,
    authorized: tuple[str, ...],
    carry: dict[str, bytes],
) -> bool:
    """Re-run the same walk from the same input; require identical bytes."""
    throwaway = round_dir.parent / (round_dir.name + "-recheck")
    try:
        recheck = apply_refresh(
            input_specs,
            root,
            throwaway,
            gate,
            census=round_census,
            authorized_changes=authorized,
            seeded_projections=carry,
        )
        return recheck.directives == () and _tree_bytes_map(
            round_dir
        ) == _tree_bytes_map(throwaway)
    finally:
        shutil.rmtree(throwaway, ignore_errors=True)


def fixpoint_refresh(
    specs_dir: Path,
    root: Path,
    output_dir: Path,
    authorized: tuple[str, ...] = (),
    reason: str = "",
    *,
    max_rounds: int = DEFAULT_MAX_ROUNDS,
    journal_dir: Path | None = None,
) -> dict[str, Any]:
    """Bounded staged fixpoint over the settled 14-phase order.

    Round 1 stages from ``specs_dir``; every later round stages the previous
    round's flushed tree with the carried directive projections seeded into
    the view. Convergence requires zero mutations, zero directives, and a
    byte-identical re-application into a throwaway directory; a repeated
    non-terminal state hash is a cycle and a bound overrun refuses. Terminal
    state ``awaiting-commit``; the staged candidate is the final round's
    flushed tree.
    """
    if max_rounds < 1:
        raise RefreshRefused(f"--max-rounds must be at least 1, got {max_rounds}")
    gates = _mode_gates(specs_dir, root, authorized, reason, mode="fixpoint")
    if output_dir.resolve() == specs_dir.resolve():
        raise RefreshRefused("fixpoint staging must not be the live specs tree")
    output_dir.mkdir(parents=True, exist_ok=True)
    census = gates["census"]
    gate = gates["gate"]
    rounds: list[dict[str, Any]] = []
    seen: set[str] = set()
    carry: dict[str, bytes] = {}
    input_specs = specs_dir
    input_hash = ""
    round_dir = output_dir
    converged_round: int | None = None
    for round_number in range(1, max_rounds + 1):
        input_hash = _state_hash(input_specs, carry)
        if input_hash in seen:
            raise RefreshRefused(
                f"fixpoint cycle detected at round {round_number}: candidate "
                f"state hash {input_hash[:16]} already occurred before convergence"
            )
        round_dir = output_dir / f"round-{round_number}"
        report = apply_refresh(
            input_specs,
            root,
            round_dir,
            gate,
            census=census,
            authorized_changes=authorized,
            seeded_projections=carry,
        )
        record: dict[str, Any] = {
            "round": round_number,
            "input": str(input_specs),
            "staging": str(round_dir),
            "input_state_hash": input_hash,
            "mutations": sorted(report.mutations),
            "directives": _directive_records(report.directives),
            "zero_mutations": not report.mutations,
            "zero_directives": not report.directives,
            "byte_identical_reapplication": None,
            "converged": False,
        }
        if not report.mutations and not report.directives:
            identical = _reapplication_is_byte_identical(
                input_specs, root, round_dir, census, gate, authorized, carry
            )
            record["byte_identical_reapplication"] = identical
            if identical:
                record["converged"] = True
                rounds.append(record)
                converged_round = round_number
                break
            raise RefreshRefused(
                f"fixpoint re-application diverged at round {round_number}: "
                "the zero-effect walk is not byte-identical"
            )
        record["output_state_hash"] = _state_hash(round_dir, report.projections)
        seen.add(input_hash)
        rounds.append(record)
        carry = report.projections
        input_specs = round_dir
    if converged_round is None:
        raise RefreshRefused(
            f"fixpoint did not converge within {max_rounds} rounds; last "
            f"candidate state hash {input_hash[:16]}"
        )
    journal: dict[str, Any] = {
        "schema_version": JOURNAL_SCHEMA_VERSION,
        "mode": "fixpoint",
        "reason": reason,
        "authorized": list(authorized),
        "pre_commit_head": gates["head"],
        "owner_snapshot": gates["owner_snapshot"],
        "owner_errors": gates["owner_errors"],
        "census": {
            "stale": gates["stale"],
            "live_red": gates["live_red"],
            "authorized": list(authorized),
        },
        "verify_gate": {"ok": True, "problems": []},
        "pin_check": gates["pin_check"],
        "evidence_note": (
            "receipt re-issues are dependency re-binds, not new execution evidence"
        ),
        "phases": rounds,
        "rounds_completed": converged_round,
        "staged_candidate": str(round_dir),
        "state": "awaiting-commit",
        "next_action": (
            "coordinator commit; then fep-lean custody refresh --resume <journal-dir>"
        ),
        "updated_at": _utc_now_iso(),
    }
    _persist_journal(
        journal,
        root,
        _operation_id(gates["head"], reason, "fixpoint"),
        journal_dir,
    )
    return journal


def _verify_failures(verify_set: dict[str, Any]) -> list[str]:
    """Collect dict-shaped verify-set failures; validator raises fail closed."""
    failures: list[str] = []
    readiness = verify_set["readiness"]
    if readiness:
        failures.append("readiness errors: " + "; ".join(readiness))
    diagnostics = verify_set["diagnostics"]
    if not diagnostics["byte_equal"]:
        failures.append(str(diagnostics["detail"]))
    for key in ("pytest_custody", "formalism_audit", "pin_audit"):
        run = verify_set[key]
        if run["exit_code"] != 0:
            failures.append(f"{key} exit {run['exit_code']}: {run['tail']}")
    return failures


def _git_dirty(root: Path) -> list[str]:
    """The porcelain dirty list; the native receipt binds live source bytes."""
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=str(root),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return [f"git status failed: {result.stderr.strip()[:200]}"]
    return result.stdout.splitlines()


def _git_head(root: Path) -> str:
    """The committed HEAD sha; the capture must observe one unmoved tip."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=str(root),
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"git rev-parse failed: {result.stderr.strip()[:200]}"
    return result.stdout.strip()
