"""Parent Polymarket FastMCP server.

Purpose:
    Compose the Gamma, Data API, and public CLOB FastMCP servers into a single
    Polymarket MCP entrypoint.

Design:
    The parent server is the primary object that MCP clients should connect to.
    It mounts the child domain servers under stable prefixes so tool names stay
    organized and collisions are avoided.

    Resource-to-tool exposure is optionally enabled so tool-centric clients,
    including many LangChain and LangGraph workflows, can still access
    canonical resources through ordinary tool calls.

Attributes:
    create_server:
        Factory for the parent composed FastMCP server.
    mcp:
        Module-level default Polymarket FastMCP server instance.

Examples:
    .. code-block:: python

        from polymarket_mcp.server import create_server

        mcp = create_server()
        mcp.run()

    .. code-block:: bash

        fastmcp run polymarket_mcp/server.py:mcp
"""

from __future__ import annotations

from fastmcp import FastMCP
from fastmcp.server.transforms import ResourcesAsTools

from polymarket_mcp.servers.clob_public_server import mcp as clob_public_server
from polymarket_mcp.servers.data_server import mcp as data_server
from polymarket_mcp.servers.gamma_server import mcp as gamma_server
from polymarket_mcp.settings import AppSettings, load_settings


def create_server(settings: AppSettings | None = None) -> FastMCP:
    """Build the composed Polymarket FastMCP server.

    Use this factory when you want a single MCP surface that exposes discovery,
    wallet analytics, and public order book functionality together.

    The returned server mounts:
    - ``gamma`` for market and event discovery,
    - ``data`` for wallet positions, activity, and trades,
    - ``clob`` for public order book, quote, and history reads.

    Resources may also be exposed as generated tools when configured, which is
    especially useful for tool-centric clients that do not use native MCP
    resource loading directly.

    Args:
        settings: Optional typed application settings. When omitted, default
            settings are loaded with :func:`load_settings`.

    Returns:
        FastMCP: Fully composed parent FastMCP server.

    Raises:
        None.

    Examples:
        >>> server = create_server()
        >>> server.name
        'polymarket'
    """
    resolved_settings = settings or load_settings()

    server = FastMCP(
        name="polymarket",
        instructions=(
            "Unified Polymarket MCP server. "
            "Use the gamma namespace for market and event discovery, "
            "the data namespace for wallet positions, activity, and trades, "
            "and the clob namespace for live public order books, quotes, and "
            "historical pricing. "
            "Do not use this server for authenticated trading actions in this "
            "version."
        ),
        strict_input_validation=True,
        mask_error_details=True,
    )

    server.mount(gamma_server, namespace="gamma")
    server.mount(data_server, namespace="data")
    server.mount(clob_public_server, namespace="clob")

    if resolved_settings.enable_resources_as_tools:
        server.add_transform(ResourcesAsTools(server))

    return server


mcp = create_server()


def main() -> None:
    """Run the default Polymarket MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
