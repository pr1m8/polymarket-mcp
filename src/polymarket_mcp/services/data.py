"""Typed Data API service adapter.

Purpose:
    Fetch Polymarket Data API payloads and normalize them into stable wallet and
    trade models.

Design:
    This module is the normalization boundary between raw Data API responses and
    MCP-facing code.
"""

from __future__ import annotations

from typing import Any

from polymarket_mcp.http import JsonHttpClient
from polymarket_mcp.models.data import (
    ActivityItem,
    Position,
    Trade,
    TradesArgs,
    WalletArgs,
)
from polymarket_mcp.settings import AppSettings


def _to_optional_str(value: object) -> str | None:
    """Coerce a value to an optional string."""
    if value is None:
        return None
    return str(value)


def _to_optional_float(value: object) -> float | None:
    """Coerce a value to an optional float."""
    if value is None:
        return None
    return float(value)


def _to_optional_int(value: object) -> int | None:
    """Coerce a value to an optional integer."""
    if value is None:
        return None
    return int(value)


class DataApiService:
    """Service wrapper for Polymarket Data API.

    Args:
        settings: Application settings.

    Returns:
        DataApiService: Configured service adapter.
    """

    def __init__(self, settings: AppSettings) -> None:
        self._client = JsonHttpClient(
            base_url=settings.data_base_url,
            timeout=settings.request_timeout_seconds,
            domain="data",
            user_agent=settings.user_agent,
        )

    def _normalize_position(self, payload: dict[str, Any]) -> Position:
        """Normalize a raw position payload.

        Args:
            payload: Upstream position dictionary.

        Returns:
            Position: Normalized position model.
        """
        return Position(
            market_slug=_to_optional_str(
                payload.get("market_slug") or payload.get("marketSlug")
            ),
            title=_to_optional_str(payload.get("title") or payload.get("question")),
            outcome=_to_optional_str(payload.get("outcome")),
            size=_to_optional_float(payload.get("size")),
            avg_price=_to_optional_float(
                payload.get("avg_price") or payload.get("avgPrice")
            ),
            current_value=_to_optional_float(
                payload.get("current_value") or payload.get("currentValue")
            ),
            realized_pnl=_to_optional_float(
                payload.get("realized_pnl") or payload.get("realizedPnl")
            ),
            unrealized_pnl=_to_optional_float(
                payload.get("unrealized_pnl") or payload.get("unrealizedPnl")
            ),
        )

    def _normalize_activity(self, payload: dict[str, Any]) -> ActivityItem:
        """Normalize a raw activity payload.

        Args:
            payload: Upstream activity dictionary.

        Returns:
            ActivityItem: Normalized activity model.
        """
        return ActivityItem(
            activity_type=_to_optional_str(
                payload.get("activity_type") or payload.get("type")
            ),
            market_slug=_to_optional_str(
                payload.get("market_slug") or payload.get("marketSlug")
            ),
            title=_to_optional_str(payload.get("title") or payload.get("question")),
            outcome=_to_optional_str(payload.get("outcome")),
            price=_to_optional_float(payload.get("price")),
            size=_to_optional_float(payload.get("size")),
            timestamp=_to_optional_int(
                payload.get("timestamp") or payload.get("time")
            ),
        )

    def _normalize_trade(self, payload: dict[str, Any]) -> Trade:
        """Normalize a raw trade payload.

        Args:
            payload: Upstream trade dictionary.

        Returns:
            Trade: Normalized trade model.
        """
        return Trade(
            market_slug=_to_optional_str(
                payload.get("market_slug") or payload.get("marketSlug")
            ),
            outcome=_to_optional_str(payload.get("outcome")),
            price=_to_optional_float(payload.get("price")),
            size=_to_optional_float(payload.get("size")),
            side=_to_optional_str(payload.get("side")),
            user=_to_optional_str(payload.get("user")),
            timestamp=_to_optional_int(
                payload.get("timestamp") or payload.get("time")
            ),
        )

    async def get_positions(self, args: WalletArgs) -> list[Position]:
        """Get normalized current positions for a wallet.

        Args:
            args: Wallet query arguments.

        Returns:
            list[Position]: Current wallet positions.
        """
        data = await self._client.get("/positions", params=args.model_dump())
        return [
            self._normalize_position(item)
            for item in data
            if isinstance(item, dict)
        ]

    async def get_closed_positions(self, args: WalletArgs) -> list[Position]:
        """Get normalized closed positions for a wallet.

        Args:
            args: Wallet query arguments.

        Returns:
            list[Position]: Closed wallet positions.
        """
        data = await self._client.get("/closed-positions", params=args.model_dump())
        return [
            self._normalize_position(item)
            for item in data
            if isinstance(item, dict)
        ]

    async def get_activity(self, args: WalletArgs) -> list[ActivityItem]:
        """Get normalized wallet activity.

        Args:
            args: Wallet query arguments.

        Returns:
            list[ActivityItem]: Wallet activity rows.
        """
        data = await self._client.get("/activity", params=args.model_dump())
        return [
            self._normalize_activity(item)
            for item in data
            if isinstance(item, dict)
        ]

    async def get_trades(self, args: TradesArgs) -> list[Trade]:
        """Get normalized trades.

        Args:
            args: Trade query arguments.

        Returns:
            list[Trade]: Matching trade rows.
        """
        data = await self._client.get(
            "/trades",
            params=args.model_dump(exclude_none=True),
        )
        return [
            self._normalize_trade(item)
            for item in data
            if isinstance(item, dict)
        ]
