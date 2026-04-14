"""Typed domain and tool I/O models for Polymarket MCP.

Purpose:
    Centralize normalized domain objects and MCP-facing input/output models.

Design:
    Models are grouped by API domain:
    - Gamma for discovery
    - Data for wallet and trade reads
    - CLOB for public order books and quotes

Attributes:
    __all__:
        Curated public exports for model modules.
"""

from __future__ import annotations

__all__ = [
    "gamma",
    "data",
    "clob",
]
