"""Pytest fixtures and import-time test setup.

Purpose:
    Provide shared fixtures and path setup for the Polymarket MCP test suite.

Design:
    The real ``fastmcp`` package is not required for these tests. A lightweight
    module stub is injected into ``sys.modules`` during test collection so the
    package can be imported without the optional runtime dependency.
"""

from __future__ import annotations

import asyncio
import inspect
import sys
import types
from pathlib import Path

import pytest

from tests.helpers.fake_fastmcp import (
    build_fake_fastmcp_modules,
    install_fake_fastmcp,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

try:
    import fastmcp  # noqa: F401
except ImportError:
    install_fake_fastmcp()


def pytest_configure(config: pytest.Config) -> None:
    """Register local pytest configuration used across the suite."""
    config.addinivalue_line(
        "markers",
        "asyncio: run async tests in a local asyncio event loop",
    )


@pytest.hookimpl(tryfirst=True)
def pytest_pyfunc_call(pyfuncitem: pytest.Function) -> bool | None:
    """Run ``@pytest.mark.asyncio`` tests without an external plugin.

    This keeps the suite self-contained in the PDM environment while still
    allowing real async service and MCP integration tests.
    """
    if "asyncio" not in pyfuncitem.keywords:
        return None
    if pyfuncitem.config.pluginmanager.hasplugin("asyncio"):
        return None
    if not inspect.iscoroutinefunction(pyfuncitem.obj):
        return None

    testargs = {
        name: pyfuncitem.funcargs[name]
        for name in pyfuncitem._fixtureinfo.argnames
    }
    asyncio.run(pyfuncitem.obj(**testargs))
    return True


@pytest.fixture()
def fake_fastmcp(monkeypatch: pytest.MonkeyPatch) -> types.ModuleType:
    """Install and return a fake ``fastmcp`` module for import-time tests.

    Args:
        None.

    Returns:
        types.ModuleType: The injected fake ``fastmcp`` module.

    Raises:
        None.
    """
    modules = build_fake_fastmcp_modules()
    for module_name, module in modules.items():
        monkeypatch.setitem(sys.modules, module_name, module)
    return modules["fastmcp"]
