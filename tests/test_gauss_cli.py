"""gauss_cli helpers — isolated real local version probe only."""

from __future__ import annotations

import os

import pytest

import fep_lean.gauss.cli as gauss_cli

pytestmark = pytest.mark.timeout(180)


@pytest.mark.skipif(
    "gauss" in os.environ.get("FEP_LEAN_TOOLS_MISSING", ""), reason="gauss CLI missing"
)
def test_gauss_version_real_without_project_root() -> None:
    ok, msg = gauss_cli.check_gauss_cli(None, require=True)
    assert ok is True
    assert "gauss" in msg.lower()
