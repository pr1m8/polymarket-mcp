"""Pytest fixtures and import-time test setup.

Purpose:
    Provide shared fixtures and path setup for the Polymarket MCP test suite.

Design:
    The real ``fastmcp`` package is not required for these tests. A lightweight
    module stub is injected into ``sys.modules`` during test collection so the
    package can be imported without the optional runtime dependency.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path

import pytest

from tests.helpers.fake_fastmcp import install_fake_fastmcp

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

fastmcp_module = install_fake_fastmcp()


@pytest.fixture()
def fake_fastmcp() -> types.ModuleType:
    """Return the fake ``fastmcp`` module used in tests.

    Args:
        None.

    Returns:
        types.ModuleType: The injected fake ``fastmcp`` module.

    Raises:
        None.
    """
    return fastmcp_module
