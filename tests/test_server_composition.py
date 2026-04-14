"""Tests for parent MCP server composition."""

from __future__ import annotations

import importlib
import sys

from polymarket_mcp.settings import AppSettings


def test_create_server_mounts_child_servers_and_optional_transforms(
    fake_fastmcp,
) -> None:
    """Parent server should mount the three child servers and add transforms when enabled."""
    for module_name in list(sys.modules):
        if module_name.startswith("polymarket_mcp"):
            sys.modules.pop(module_name)

    server_module = importlib.import_module("polymarket_mcp.server")
    server = server_module.create_server(
        AppSettings(enable_resources_as_tools=True)
    )

    prefixes = [prefix for prefix, _ in server.mounts]
    assert prefixes == ["gamma", "data", "clob"]
    assert len(server.transforms) == 1
    assert server.name == "polymarket"


def test_create_server_can_disable_resources_as_tools(fake_fastmcp) -> None:
    """Parent server should omit transforms when resource toolification is disabled."""
    for module_name in list(sys.modules):
        if module_name.startswith("polymarket_mcp"):
            sys.modules.pop(module_name)

    server_module = importlib.import_module("polymarket_mcp.server")
    server = server_module.create_server(
        AppSettings(enable_resources_as_tools=False)
    )

    assert len(server.mounts) == 3
    assert server.transforms == []
