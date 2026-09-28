"""Single canonical command-line interface for fep_lean."""

from __future__ import annotations

import argparse
import json
import logging
import os
import subprocess
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from fep_lean._paths import project_root, project_root_errors
from fep_lean.bridge import operations
from fep_lean.bridge.custody import validate_binding
from fep_lean.catalogue.generation import (
    catalogue_projection_drift,
    check_or_write,
    fep_all_projection_drift,
)
from fep_lean.catalogue.topics import FEPTopicCatalogue
from fep_lean.output.evidence import (
    build_native_lean_receipt,
    validate_native_lean_receipt,
    write_native_lean_receipt,
)
from fep_lean.output.formal_kernel_dashboard import (
    formal_kernel_dashboard_drift,
    write_formal_kernel_dashboard,
)
from fep_lean.output.formalism_atlas import (
    atlas_projection_drift,
    write_formalism_atlas,
)
from fep_lean.output.manuscript import (
    build_manuscript_vars,
    manuscript_projection_drift,
)
from fep_lean.output.render_log import receipt_defects
from fep_lean.pipeline.orchestrator import run_pipeline, run_single_topic
from fep_lean.verification._subprocess import run_process_group
from fep_lean.verification._toolchain import find_executable, subprocess_env
from fep_lean.verification.environment import run_validation_checks
from fep_lean.verification.lean_verifier import LeanVerifier


def _configure_logging(verbose: bool) -> None:
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _setup(root: Path) -> int:
    """Acquire the checked-in workspace without resolving new dependency pins."""
    import re
    import shutil

    from fep_lean.verification._toolchain import (
        lean_version_matches_pin,
        pinned_lean_semver,
        read_mathlib_tag,
        read_toolchain_pin,
        resolved_mathlib_revision,
    )

    lean_dir = Path(os.environ.get("FEP_LEAN_DIR", str(root / "lean"))).resolve()
    repair = (
        "Inspect git diff -- lean/lean-toolchain lean/lakefile.lean "
        "lean/lake-manifest.json uv.lock; preserve intentional edits, then restore "
        "these files together from the intended reviewed commit and rerun setup. "
        "Do not run lake update to repair ordinary setup."
    )
    try:
        timeout = int(os.environ.get("FEP_LEAN_SETUP_TIMEOUT_SEC", "1800"))
    except ValueError:
        print("setup failed: FEP_LEAN_SETUP_TIMEOUT_SEC must be an integer", flush=True)
        return 1
    if timeout < 1:
        print("setup failed: FEP_LEAN_SETUP_TIMEOUT_SEC must be positive", flush=True)
        return 1
    deadline = time.monotonic() + timeout
    pins = [
        lean_dir / name
        for name in ("lean-toolchain", "lakefile.lean", "lake-manifest.json")
    ] + [root / "uv.lock"]
    try:
        snapshot = {path: path.read_bytes() for path in pins}
        toolchain = read_toolchain_pin(lean_dir)
        tag = read_mathlib_tag(lean_dir)
        manifest = json.loads(snapshot[lean_dir / "lake-manifest.json"])
        packages = manifest.get("packages") if isinstance(manifest, dict) else None
        if (
            not toolchain
            or tag != "v" + str(pinned_lean_semver(toolchain))
            or not isinstance(packages, list)
            or not packages
            or manifest.get("packagesDir") != ".lake/packages"
            or any(
                not isinstance(package, dict)
                or package.get("type") != "git"
                or not re.fullmatch(r"[0-9a-f]{40}", str(package.get("rev", "")))
                for package in packages
            )
        ):
            raise ValueError("invalid or mismatched toolchain/Mathlib/manifest pins")
        mathlib = [package for package in packages if package.get("name") == "mathlib"]
        if len(mathlib) != 1 or mathlib[0].get("inputRev") != tag:
            raise ValueError(
                "manifest Mathlib inputRev does not match lakefile/toolchain"
            )
        revision = resolved_mathlib_revision(lean_dir)
    except (OSError, ValueError) as exc:
        print(f"setup failed: {exc}. {repair}", flush=True)
        return 1

    def check_pins() -> None:
        for path, original in snapshot.items():
            if not path.is_file() or path.read_bytes() != original:
                raise ValueError(f"setup pin drift: {path}. {repair}")

    env = subprocess_env(lean_dir)
    # Setup deliberately installs into the requested (or ordinary) elan home,
    # unlike read-only verification's temporary writable-home fallback.
    elan_home = Path(os.environ.get("ELAN_HOME", str(Path.home() / ".elan")))
    env["ELAN_HOME"] = str(elan_home)
    for name in ("XDG_CACHE_HOME", "MATHLIB_CACHE_DIR"):
        if name in os.environ:
            env[name] = os.environ[name]

    def run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
        check_pins()
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(list(command), timeout)
        print(f"[fep_lean setup] {' '.join(command)}", flush=True)
        try:
            result = run_process_group(
                command, cwd=lean_dir, env=env, timeout=remaining, check=False
            )
            if result.stdout:
                print(result.stdout, end="", flush=True)
            if result.stderr:
                print(result.stderr, end="", flush=True)
        finally:
            check_pins()
        if result.returncode:
            raise subprocess.CalledProcessError(result.returncode, list(command))
        return result

    try:
        lake = find_executable("lake", lean_dir)
        if not lake:
            elan = os.environ.get("FEP_LEAN_ELAN_EXE") or shutil.which("elan")
            if not elan and (elan_home / "bin" / "elan").is_file():
                elan = str(elan_home / "bin" / "elan")
            if not elan:
                raise ValueError(
                    "elan is unavailable; install elan or set FEP_LEAN_ELAN_EXE"
                )
            run([elan, "toolchain", "install", toolchain])
            toolchain_bin = (
                elan_home
                / "toolchains"
                / toolchain.replace("/", "--").replace(":", "---")
                / "bin"
            )
            lake = str(toolchain_bin / "lake")
        lake_version = run([lake, "--version"]).stdout
        if f"(Lean version {pinned_lean_semver(toolchain)})" not in lake_version:
            raise ValueError(
                f"Lake does not report {toolchain}; install that toolchain with elan "
                "and remove a mismatched FEP_LEAN_LAKE_EXE override"
            )
        # With a validated manifest, ordinary Lake loading materializes its
        # exact revisions. --wfail rejects out-of-date dependency warnings.
        actual_lean = run([lake, "--wfail", "env", "lean", "--version"]).stdout
        if not lean_version_matches_pin(actual_lean, toolchain):
            raise ValueError(f"actual Lean does not match {toolchain}")
        actual_revision = run(
            ["git", "-C", str(lean_dir / ".lake/packages/mathlib"), "rev-parse", "HEAD"]
        ).stdout.strip()
        if actual_revision != revision:
            raise ValueError(
                "materialized Mathlib revision does not match the manifest"
            )
        run([lake, "--wfail", "exe", "cache", "get"])
        run([lake, "--wfail", "build", "FepSketches"])
        print(
            f"[fep_lean setup] OK | lean: {actual_lean.strip()} | mathlib: {revision}",
            flush=True,
        )
        return 0
    except (OSError, ValueError, subprocess.SubprocessError) as exc:
        print(f"setup failed: {exc}. For pin/manifest errors: {repair}", flush=True)
        return exc.returncode if isinstance(exc, subprocess.CalledProcessError) else 1


def _print_result(result: object) -> int:
    payload = result.as_dict() if hasattr(result, "as_dict") else result
    print(json.dumps(payload, indent=2, default=str))
    return 0 if getattr(result, "complete", False) else 1


def _display(root: Path, path: Path) -> str:
    """Render *path* for display, relative to *root* when possible."""
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _atlas(root: Path, *, check: bool) -> int:
    """Write or fail-closed drift-check the formalism atlas projection."""
    return check_or_write(
        root,
        atlas_projection_drift,
        write_formalism_atlas,
        "formalism atlas projections are current",
        check=check,
    )


def _dashboard(root: Path, *, check: bool) -> int:
    """Write or fail-closed drift-check the formal-kernel dashboard."""
    return check_or_write(
        root,
        formal_kernel_dashboard_drift,
        write_formal_kernel_dashboard,
        "formal-kernel dashboard projections are current",
        check=check,
    )


def _verify(
    root: Path,
    topic_ids: list[str] | None,
    area: str | None,
    *,
    receipt_path: Path | None = None,
    fail_on_warnings: bool = False,
) -> int:
    """Compile catalogue sketches with Lean only, without Hermes or Gauss."""
    try:
        catalogue = FEPTopicCatalogue.from_yaml(root / "config" / "topics.yaml")
        topics = catalogue.topics
        if topic_ids:
            known = {topic.id for topic in topics}
            unknown = sorted(set(topic_ids) - known)
            if unknown:
                raise ValueError(f"unknown topic ids: {', '.join(unknown)}")
            topics = tuple(topic for topic in topics if topic.id in topic_ids)
        if area:
            topics = tuple(topic for topic in topics if topic.area == area)
        if not topics:
            raise ValueError("no catalogue topics matched the requested filters")
    except (OSError, KeyError, TypeError, ValueError) as exc:
        print(
            json.dumps(
                {
                    "status": "error",
                    "mode": "lean-only",
                    "complete": False,
                    "failure_reason": str(exc),
                }
            )
        )
        return 1

    verifier = LeanVerifier(lean_dir=root / "lean", project_root=root)
    mathlib_ok, mathlib_message = verifier.check_mathlib_built()
    if not mathlib_ok:
        print(
            json.dumps(
                {
                    "status": "error",
                    "mode": "lean-only",
                    "complete": False,
                    "catalogue_topics": len(topics),
                    "verified_topics": 0,
                    "mathlib": mathlib_message,
                    "results": [],
                },
                indent=2,
            )
        )
        return 1

    results = verifier.verify_batch([(topic.id, topic.lean_sketch) for topic in topics])
    result_payload = []
    for result in results:
        row = result.as_dict()
        # The verifier removes its temporary source file before returning;
        # do not publish a path that is already stale in the CLI receipt.
        row["lean_file"] = None
        result_payload.append(row)
    compiled_without_sorry = sum(
        result.compiles and not result.has_sorry for result in results
    )
    warning_count = sum(len(getattr(result, "warnings", [])) for result in results)
    verified = sum(
        result.compiles and not result.has_sorry and not getattr(result, "warnings", [])
        for result in results
    )
    sorry_count = sum(result.has_sorry for result in results)
    complete = (
        len(results) == len(topics)
        and compiled_without_sorry == len(topics)
        and (not fail_on_warnings or warning_count == 0)
    )
    receipt_validation: dict[str, Any] | None = None
    if receipt_path is not None:
        receipt = write_native_lean_receipt(
            receipt_path,
            build_native_lean_receipt(root, [topic.id for topic in topics], results),
        )
        receipt_validation = validate_native_lean_receipt(receipt, project_root=root)
        complete = complete and bool(receipt_validation.get("valid", False))
    print(
        json.dumps(
            {
                "status": "ok" if complete else "error",
                "mode": "lean-only",
                "complete": complete,
                "catalogue_topics": len(topics),
                "verified_topics": verified,
                "compiled_without_sorry_topics": compiled_without_sorry,
                "warning_count": warning_count,
                "sorry_count": sorry_count,
                "mathlib": mathlib_message,
                "receipt": str(receipt_path) if receipt_path is not None else None,
                "native_claim_ready": (
                    receipt_validation.get("native_claim_ready", False)
                    if receipt_validation is not None
                    else False
                ),
                "results": result_payload,
            },
            indent=2,
            default=str,
        )
    )
    return 0 if complete else 1


RENDER_RECEIPT = Path("docs") / "render-acceptance.json"
NATIVE_RECEIPT = Path("output") / "native-verification.json"
SOURCE_PIN = Path(operations.PIN)


_STATUS_BOUNDARY = (
    "status composes existing read-only checks; exit 0 means the report "
    "composed, never that the evidence is current. Each section's state and "
    "boundary are the authority. Nothing here compiles Lean, runs Hermes or "
    "OpenGauss, executes the test suite, writes bytes, or repairs drift."
)


@dataclass(frozen=True)
class SectionReport:
    """One evidence-currency section with its explicit capability boundary."""

    name: str
    state: str
    findings: tuple[str, ...]
    composes: tuple[str, ...]
    boundary: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "state": self.state,
            "findings": list(self.findings),
            "composes": list(self.composes),
            "boundary": self.boundary,
        }


@dataclass(frozen=True)
class StatusReport:
    """Typed ``fep-lean status`` payload: sections, never proof claims."""

    sections: tuple[SectionReport, ...]

    @property
    def status(self) -> str:
        """``ok`` when the report composed; section states carry currency."""
        return "ok" if len(self.sections) == 4 else "error"

    def as_dict(self) -> dict[str, Any]:
        # The top-level native_claim_ready flag must agree with the
        # native_verification_receipt section's state: the sections are the
        # authority, and a hardcoded False contradicted a claim_ready section
        # (observed 2026-09-10 after the wave-2 evidence refresh).
        native_ready = any(
            section.name == "native_verification_receipt"
            and section.state == "claim_ready"
            for section in self.sections
        )
        return {
            "schema_version": 1,
            "status": self.status,
            "evidence_plane": "evidence currency and provenance",
            "boundary": _STATUS_BOUNDARY,
            "native_claim_ready": native_ready,
            "sections": [section.as_dict() for section in self.sections],
        }


def catalogue_products_section(
    root: Path, catalogue: FEPTopicCatalogue | None = None
) -> SectionReport:
    """Compare offline catalogue build products against their generators."""
    composes = (
        "fep_lean.catalogue.generation.catalogue_projection_drift",
        "fep_lean.catalogue.generation.fep_all_projection_drift",
        "fep_lean.output.manuscript.manuscript_projection_drift",
    )
    boundary = (
        "Compares generated projections byte-for-byte against their canonical "
        "generators. It does not compile Lean, run Hermes or OpenGauss, "
        "execute the test suite, or prove any theorem: current means only "
        "that generators and products agree on bytes."
    )
    stale: list[Path] = []
    findings: list[str] = []
    try:
        stale.extend(catalogue_projection_drift(root))
    except (OSError, ValueError) as exc:
        findings.append(f"topic catalogue projections unreadable: {exc}")
    try:
        stale.extend(fep_all_projection_drift(root))
    except (OSError, ValueError) as exc:
        findings.append(f"aggregate Lean projection unreadable: {exc}")
    try:
        cat = catalogue or FEPTopicCatalogue.from_yaml(root / "config" / "topics.yaml")
        expected_vars = build_manuscript_vars(
            cat,
            root,
            output_root=root / "output",
            cache_test_count=False,
        )
        stale.extend(
            manuscript_projection_drift(
                root,
                catalogue=cat,
                output_root=root / "output",
                expected_variables=expected_vars,
            )
        )
    except (OSError, ValueError) as exc:
        # The test census refuses to run a collection here; a missing cache is
        # the census boundary, not a drift verdict on the manuscript.
        findings.append(
            "manuscript projections not compared: test-collection census "
            f"cache missing or stale ({exc})"
        )
    if stale:
        findings.extend(f"stale or missing: {_display(root, path)}" for path in stale)
    state = "stale" if stale else "current"
    return SectionReport(
        name="catalogue_build_products",
        state=state,
        findings=tuple(findings),
        composes=composes,
        boundary=boundary,
    )


def render_receipt_section(
    root: Path,
    *,
    receipt_path: Path | None = None,
    manuscript_dir: Path | None = None,
) -> SectionReport:
    receipt = receipt_path or root / RENDER_RECEIPT
    manuscript = manuscript_dir or root / "manuscript"
    composes = (
        "fep_lean.output.render_log.receipt_defects",
        "fep_lean.output.render_log.manuscript_source_digests",
    )
    boundary = (
        "The receipt binds an accepted render to the authored manuscript text "
        "and LaTeX preamble as of that render. It does not re-run the render, "
        "does not cover values a {{token}} resolves to (manuscript projection "
        "drift owns that surface), and says nothing about Lean, Hermes, or "
        "OpenGauss evidence."
    )
    defects = receipt_defects(receipt, manuscript)
    if not receipt.is_file():
        state = "missing"
    elif defects:
        state = "stale"
    else:
        state = "current"
    return SectionReport(
        name="render_receipt_freshness",
        state=state,
        findings=defects,
        composes=composes,
        boundary=boundary,
    )


def bridge_pin_section(root: Path, gnn_root: Path | None = None) -> SectionReport:
    """Report GNN bridge source-pin presence and, when possible, staleness."""
    composes = (
        "fep_lean.bridge.operations.check_sources",
        "fep_lean.bridge.custody.validate_binding",
    )
    pin = root / SOURCE_PIN
    if not pin.is_file():
        return SectionReport(
            name="bridge_source_pin",
            state="not_pinned",
            findings=(
                "specs/gnn-bridge-w2-source-custody/source-pin.json: not pinned",
            ),
            composes=composes,
            boundary=(
                "No source pin exists, so no bridge evidence is bound to owner "
                "bytes. Pin presence alone establishes nothing about the "
                "current sibling tree: comparing working-tree bytes requires "
                "the explicitly named GNN checkout, and a fresh pin is not "
                "evidence of correctness or of native proof."
            ),
        )
    try:
        data = operations.read_object(pin)
        findings = [
            f"fep_lean commit recorded: {data['fep_lean'].get('commit', '?')}",
            f"gnn commit recorded: {data['gnn'].get('commit', '?')}",
        ]
        errors: list[str]
        if gnn_root is not None:
            errors = operations.check_sources(root, gnn_root, data)
        else:
            fep_entry = data.get("fep_lean")
            owners = fep_entry.get("owners") if isinstance(fep_entry, dict) else None
            if not isinstance(owners, dict):
                errors = ["malformed fep_lean source binding"]
            else:
                errors = validate_binding(
                    root, owners, operations.owner_roster(root, "fep_lean")
                )
                errors = [f"fep_lean: {error}" for error in errors]
            findings.append(
                "gnn owner bytes not compared: pass --gnn-root with the "
                "explicit GNN checkout to validate both sides"
            )
    except (OSError, KeyError, TypeError, ValueError) as exc:
        return SectionReport(
            name="bridge_source_pin",
            state="error",
            findings=(f"unreadable or malformed source pin: {exc}",),
            composes=composes,
            boundary=(
                "A malformed pin is a custody failure, not a stale-but-trusted "
                "reference; re-pin explicitly after reviewing owner changes."
            ),
        )
    findings.extend(errors)
    state = "current" if not errors else "stale"
    return SectionReport(
        name="bridge_source_pin",
        state=state,
        findings=tuple(findings),
        composes=composes,
        boundary=(
            "Custody binds owner bytes, not a perpetually refreshed HEAD. "
            "Currency here means the pinned working trees still match; it is "
            "not native proof, not semantic review, and not proof that an "
            "older execution artifact was produced by these sources."
        ),
    )


def native_receipt_section(
    root: Path, *, receipt_path: Path | None = None
) -> SectionReport:
    """Read the native verification receipt with its claim boundary."""
    receipt = receipt_path or root / NATIVE_RECEIPT
    composes = ("fep_lean.output.evidence.validate_native_lean_receipt",)
    if not receipt.is_file():
        return SectionReport(
            name="native_verification_receipt",
            state="missing",
            findings=("output/native-verification.json: absent",),
            composes=composes,
            boundary=(
                "No native receipt exists, so no Lean compilation claim is "
                "bound to current sources. Catalogue-mode output must never "
                "be read as Lean evidence."
            ),
        )
    validation = validate_native_lean_receipt(receipt, project_root=root)
    findings = [
        f"valid: {validation.get('valid', False)}",
        f"native_claim_ready: {validation.get('native_claim_ready', False)}",
        f"selected topics: {validation.get('selected_topics', 0)}",
        f"verified topics: {validation.get('verified_topics', 0)}",
        f"warnings: {validation.get('warning_count', 0)}",
        f"sorry: {validation.get('sorry_count', 0)}",
    ]
    findings.extend(str(error) for error in validation.get("errors", []))
    state = "claim_ready" if validation.get("native_claim_ready") else "not_claim_ready"
    return SectionReport(
        name="native_verification_receipt",
        state=state,
        findings=tuple(findings),
        composes=composes,
        boundary=(
            "Claim readiness covers exact-source native compilation of the "
            "selected roster at the recorded digests, with zero errors, "
            "warnings, and sorry. It is not a Hermes/OpenGauss full run, not "
            "semantic review of a theorem proxy, and not a proof of the FEP; "
            "compilation of a Lean body never promotes its disposition."
        ),
    )


def build_status_report(root: Path, gnn_root: Path | None = None) -> StatusReport:
    """Compose the four evidence-currency sections for *root*."""
    return StatusReport(
        sections=(
            catalogue_products_section(root),
            render_receipt_section(root),
            bridge_pin_section(root, gnn_root),
            native_receipt_section(root),
        )
    )


def report_to_json(report: StatusReport) -> str:
    """Serialize the report for the CLI's JSON output convention."""
    return json.dumps(report.as_dict(), indent=2, default=str)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fep-lean",
        description="Strict FEP Lean catalogue and verification pipeline",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=None,
        help="source checkout containing config/, lean/, manuscript/, and src/",
    )
    parser.add_argument("--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    from fep_lean.bridge.cli import add_arguments

    add_arguments(sub.add_parser("bridge", help="source-bound GNN bridge operations"))

    from fep_lean.custody.cli import add_arguments

    add_arguments(
        sub.add_parser("custody", help="H2.7 evidence-custody census and apply")
    )
    sub.add_parser("setup", help="explicitly acquire/build the pinned Lean workspace")
    sub.add_parser("preflight", help="run read-only full-mode capability checks")
    verify = sub.add_parser("verify", help="compile catalogue sketches with Lean only")
    verify.add_argument("--area")
    verify.add_argument("--topic", action="append", dest="topics")
    verify.add_argument(
        "--receipt",
        type=Path,
        help="atomically write a typed native-Lean verification receipt",
    )
    verify.add_argument(
        "--fail-on-warnings",
        action="store_true",
        help="treat any Lean warning as a verification failure",
    )
    catalogue = sub.add_parser(
        "catalogue", help="generate deterministic offline catalogue artifacts"
    )
    catalogue.add_argument("--area")
    catalogue.add_argument("--topic", action="append", dest="topics")
    atlas = sub.add_parser(
        "atlas", help="generate the offline formalism composition atlas"
    )
    atlas.add_argument(
        "--check", action="store_true", help="fail if atlas projections are stale"
    )
    dashboard = sub.add_parser(
        "dashboard", help="generate the offline formal-kernel validation dashboard"
    )
    dashboard.add_argument(
        "--check", action="store_true", help="fail if dashboard projections are stale"
    )
    run = sub.add_parser("run", help="run full Hermes, Lean, and SQLite verification")
    run.add_argument("--area")
    run.add_argument("--topic", action="append", dest="topics")
    run.add_argument(
        "--workflow", choices=("verify", "draft", "prove", "review"), default="verify"
    )
    topic = sub.add_parser("topic", help="verify one exact topic")
    topic.add_argument("topic_id")
    topic.add_argument(
        "--workflow", choices=("verify", "draft", "prove", "review"), default="verify"
    )
    sub.add_parser("report", help="run catalogue mode and emit a complete report")
    status = sub.add_parser(
        "status",
        help=(
            "read-only evidence-currency report composing existing checks; "
            "exit 0 means the report composed, not that evidence is current"
        ),
    )
    status.add_argument(
        "--gnn-root",
        type=Path,
        default=None,
        help=(
            "explicit GNN checkout for full source-pin comparison; omit to "
            "report pin presence and the fep_lean side only"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    _configure_logging(args.verbose or os.environ.get("FEP_LEAN_VERIFY_VERBOSE") == "1")
    previous_project_dir = os.environ.get("FEP_LEAN_PROJECT_ROOT")
    if args.project_root is not None:
        os.environ["FEP_LEAN_PROJECT_ROOT"] = str(args.project_root.resolve())
    try:
        root = project_root()
        missing = project_root_errors(root)
        if missing:
            print(
                json.dumps(
                    {
                        "status": "error",
                        "complete": False,
                        "project_root": str(root),
                        "failure_reason": (
                            "substantive fep-lean commands require a source checkout; "
                            "pass --project-root /path/to/fep_lean. Missing: "
                            + ", ".join(missing)
                        ),
                    },
                    indent=2,
                )
            )
            return 1
        if args.command == "setup":
            return _setup(root)
        if args.command == "bridge":
            from fep_lean.bridge.cli import run as run_bridge

            return run_bridge(root, args)
        if args.command == "custody":
            from fep_lean.custody.cli import run as run_custody

            return run_custody(root, args)
        if args.command == "preflight":
            result = run_validation_checks(root, mode="full")
            print(json.dumps(result, indent=2))
            return 0 if result["status"] == "ok" else 1
        if args.command == "verify":
            return _verify(
                root,
                args.topics,
                args.area,
                receipt_path=args.receipt,
                fail_on_warnings=args.fail_on_warnings,
            )
        if args.command == "catalogue":
            return _print_result(
                run_pipeline(
                    mode="catalogue", area_filter=args.area, topic_filter=args.topics
                )
            )
        if args.command == "atlas":
            return _atlas(root, check=args.check)
        if args.command == "dashboard":
            return _dashboard(root, check=args.check)
        if args.command == "run":
            return _print_result(
                run_pipeline(
                    mode="full",
                    area_filter=args.area,
                    topic_filter=args.topics,
                    workflow=args.workflow,
                )
            )
        if args.command == "topic":
            return _print_result(
                run_single_topic(args.topic_id, mode="full", workflow=args.workflow)
            )
        if args.command == "report":
            return _print_result(run_pipeline(mode="catalogue"))
        if args.command == "status":
            print(report_to_json(build_status_report(root, args.gnn_root)))
            return 0
        parser.error(f"unsupported command: {args.command}")
        return 2
    finally:
        if args.project_root is not None:
            if previous_project_dir is None:
                os.environ.pop("FEP_LEAN_PROJECT_ROOT", None)
            else:
                os.environ["FEP_LEAN_PROJECT_ROOT"] = previous_project_dir


if __name__ == "__main__":
    raise SystemExit(main())
