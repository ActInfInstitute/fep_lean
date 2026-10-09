"""The required-check list has one owner (AGENTS.md) and CI executes it."""

from __future__ import annotations

import re
import shlex
from pathlib import Path

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
AGENTS = PROJECT_ROOT / "AGENTS.md"
CI = PROJECT_ROOT / ".github" / "workflows" / "ci.yml"
SECONDARY_DOCS = ("docs/development.md", "docs/testing.md")

#: AGENTS.md commands CI does not execute verbatim. Empty on purpose: a
#: required check that hosted CI never runs is a drifted contract. Add an entry
#: only with the reason a command is local-only.
LOCAL_ONLY: dict[str, str] = {}

#: Commands CI runs that the "Required checks" block deliberately omits.
#: Normalised form -> why. Generation (non-``--check``) steps materialise
#: inputs for later gates; the rest are hosted-only orchestration whose
#: inputs (JUnit files, per-OS interpreters) do not exist on a workstation.
HOSTED_ONLY = {
    "python scripts/build_formalism_atlas.py": "render-deps: generates the atlas",
    "python scripts/build_formal_kernel_dashboard.py": "render-deps: generates it",
    "fep-lean --project-root . methods export --output-root "
    "docs/mathematical-positioning": "render-deps: generates the methods export",
    "python scripts/build_render_fonts.py": "render: generates the font record",
    "python scripts/render_publication.py": "render: the publication render itself",
    "pytest tests/test_distribution.py -q -s --no-cov": "distribution matrix cell",
    "pytest specs/openai-math-methods/test_distribution_methods.py -q -s --no-cov": (
        "distribution matrix cell"
    ),
    "pytest tests/test_browser_capture.py::"
    "test_live_chrome_blocks_and_records_a_delayed_outbound_request "
    "tests/test_browser_capture.py::"
    "test_live_chrome_replay_terminates_every_profile_writer -q -n 0 --cov=src "
    "--cov-append --cov-report=xml --cov-fail-under=89 "
    "--junitxml=output/live-chrome-acceptance.xml": "isolated live Chrome component",
    "python specs/publication-browser-acceptance/validate_acceptance.py "
    "--collection output/python-acceptance-collection.json "
    "--parallel-junit output/python-acceptance.xml "
    "--chrome-junit output/live-chrome-acceptance.xml --coverage coverage.xml "
    "--output output/python-acceptance-summary.json": "needs the hosted JUnit files",
}

_TRACKED_PREFIXES = ("uv run", "lake ", "git diff", "uv lock", "uv pip")


def normalise(command: str) -> str:
    """Canonical form: drop ``uv run [--locked]``, ``python -m``, redirections."""
    command = re.split(r"\s+(?:2>&1|\|)\s*", command, maxsplit=1)[0]
    tokens = shlex.split(command.strip().strip("()").strip())
    if tokens[:2] == ["uv", "run"]:
        tokens = tokens[2:]
        if tokens and tokens[0] == "--locked":
            tokens = tokens[1:]
    if tokens[:3] == ["python", "-m", "pytest"]:
        tokens = ["pytest", *tokens[3:]]
    return " ".join(tokens)


def split_commands(script: str) -> list[str]:
    """Split a shell snippet into commands, joining ``\\`` continuations.

    Comments, heredoc bodies and control flow are skipped; ``a && b`` is two
    commands and ``(cd d && c)`` is ``c``.
    """
    commands: list[str] = []
    heredoc_end: str | None = None
    joined = re.sub(r"\\\n\s*", " ", script)
    for raw in joined.splitlines():
        line = raw.strip()
        if heredoc_end is not None:
            if line == heredoc_end:
                heredoc_end = None
            continue
        if not line or line.startswith("#"):
            continue
        heredoc = re.search(r"<<-?\s*'?(\w+)'?\s*$", line)
        if heredoc:
            heredoc_end = heredoc.group(1)
            continue  # inline python is not a repository command
        line = line.strip("()")
        for part in re.split(r"\s*&&\s*", line):
            part = part.strip().strip("()").strip()
            if part.startswith("cd "):
                continue
            if part.startswith(_TRACKED_PREFIXES):
                commands.append(part)
    return commands


def agents_commands() -> list[str]:
    text = AGENTS.read_text(encoding="utf-8")
    section = text.split("## Required checks", 1)[1].split("\n## ", 1)[0]
    blocks = re.findall(r"```bash\n(.*?)```", section, flags=re.DOTALL)
    assert blocks, "AGENTS.md 'Required checks' has no bash block"
    return [normalise(c) for block in blocks for c in split_commands(block)]


def ci_commands() -> list[str]:
    workflow = yaml.safe_load(CI.read_text(encoding="utf-8"))
    commands: list[str] = []
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if isinstance(step.get("run"), str):
                commands += [normalise(c) for c in split_commands(step["run"])]
    return commands


def _covers(ci: str, required: str) -> bool:
    """CI runs ``required`` verbatim; pytest may add options (xdist, junit)."""
    if ci == required:
        return True
    ci_tokens, required_tokens = ci.split(), required.split()
    return (
        required_tokens[0] == ci_tokens[0] == "pytest"
        and required_tokens[1] == ci_tokens[1]
        and all(token in ci_tokens for token in required_tokens)
    )


def test_normaliser_handles_continuations_chains_and_prefixes() -> None:
    script = (
        "uv lock --check && uv pip check\n"
        "# comment\n"
        "uv run --locked python -m pytest a.py \\\n  -q --no-cov\n"
        "(cd lean && lake build FepSketches) 2>&1 | tee log\n"
        "uv run python - <<'PY'\nuv run python hidden.py\nPY\n"
    )
    assert [normalise(c) for c in split_commands(script)] == [
        "uv lock --check",
        "uv pip check",
        "pytest a.py -q --no-cov",
        "lake build FepSketches",
    ]


def test_every_required_check_is_executed_by_ci_or_explicitly_local() -> None:
    required, ci = agents_commands(), ci_commands()
    assert len(required) > 25, "AGENTS.md required-check parse looks truncated"
    missing = [
        command
        for command in required
        if command not in LOCAL_ONLY and not any(_covers(c, command) for c in ci)
    ]
    assert not missing, f"AGENTS.md checks that ci.yml never runs: {missing}"


def test_every_ci_gate_is_listed_in_agents_or_explicitly_hosted_only() -> None:
    required = agents_commands()
    unlisted = sorted(
        {
            command
            for command in ci_commands()
            if command not in HOSTED_ONLY
            and not any(_covers(command, r) for r in required)
        }
    )
    assert not unlisted, (
        f"ci.yml gates missing from AGENTS.md 'Required checks': {unlisted}"
    )


def test_allow_lists_carry_no_dead_entries() -> None:
    ci = set(ci_commands())
    stale = [c for c in HOSTED_ONLY if c not in ci]
    assert not stale, f"HOSTED_ONLY entries CI no longer runs: {stale}"
    agents = set(agents_commands())
    assert not [c for c in LOCAL_ONLY if c not in agents]


@pytest.mark.parametrize("relative", SECONDARY_DOCS)
def test_secondary_docs_link_to_the_owner_instead_of_copying_the_list(
    relative: str,
) -> None:
    text = (PROJECT_ROOT / relative).read_text(encoding="utf-8")
    assert "AGENTS.md#required-checks" in text
    required = set(agents_commands())
    for block in re.findall(r"```bash\n(.*?)```", text, flags=re.DOTALL):
        shared = [c for c in split_commands(block) if normalise(c) in required]
        assert len(shared) < 4, f"{relative} re-lists required checks: {shared}"


def test_readme_points_at_the_owner_and_no_dangling_heading() -> None:
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")
    assert "AGENTS.md#required-checks" in readme
    assert "Required release gates" not in readme
