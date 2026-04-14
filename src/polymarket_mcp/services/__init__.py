"""Typed service adapters for Polymarket MCP.

Purpose:
    Group service modules that normalize upstream API payloads before they are
    exposed through MCP tools and resources.

Design:
    Each service module owns one Polymarket API domain and converts raw JSON
    into stable internal models.
"""

from __future__ import annotations

__all__ = [
    "gamma",
    "data",
    "clob_public",
]
