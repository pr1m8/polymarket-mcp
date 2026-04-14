"""Polymarket MCP package.

Purpose:
    Provide a typed FastMCP integration for Polymarket market discovery,
    wallet/activity reads, and public CLOB order book and price reads.

Design:
    The package is organized around three layers:
    1. typed domain and tool I/O models,
    2. service adapters that normalize upstream API payloads, and
    3. FastMCP server modules that expose those services as tools and resources.

    A parent server composes the domain-specific MCP servers into one unified
    Polymarket MCP surface.

Attributes:
    __all__:
        Curated public package API.
    __version__:
        Package version string.

Examples:
    .. code-block:: python

        from polymarket_mcp import create_server

        mcp = create_server()
"""

from __future__ import annotations

from polymarket_mcp.server import create_server

__all__ = ["create_server"]

__version__ = "0.1.0"
