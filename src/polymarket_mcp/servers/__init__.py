"""FastMCP server modules for Polymarket domains.

Purpose:
    Group domain-specific FastMCP servers for Gamma discovery, Data API reads,
    and public CLOB reads.

Design:
    Each module exposes one domain-focused ``mcp`` server object. The parent
    server composes them into a single public entrypoint.

Attributes:
    __all__:
        Curated public exports for server modules.
"""

from __future__ import annotations

__all__ = [
    "gamma_server",
    "data_server",
    "clob_public_server",
]
