"""Typed Data API domain and tool I/O models.

Purpose:
    Define normalized wallet, activity, and trade models for the Polymarket
    Data API along with MCP input and output contracts.

Design:
    These models separate raw upstream payloads from normalized internal models
    and MCP-facing tool outputs.

Attributes:
    WalletArgs:
        Input model for wallet-scoped queries.
    TradesArgs:
        Input model for trade queries.
    Position:
        Normalized wallet position model.
    ActivityItem:
        Normalized wallet activity model.
    Trade:
        Normalized trade model.
    WalletPositionsOutput:
        MCP output envelope for current positions.
    WalletActivityOutput:
        MCP output envelope for activity.
    TradesOutput:
        MCP output envelope for trades.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field


class WalletArgs(BaseModel):
    """Arguments for wallet-scoped Data API queries.

    Args:
        user: Wallet address, usually in ``0x...`` format.

    Returns:
        WalletArgs: Validated wallet arguments.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> args = WalletArgs(user="0xabc")
        >>> args.user
        '0xabc'
    """

    model_config = ConfigDict(extra="forbid")

    user: str = Field(min_length=1)


class TradesArgs(BaseModel):
    """Arguments for Data API trade queries.

    Args:
        market: Optional market identifier or slug when supported upstream.
        user: Optional wallet address to scope trades.
        limit: Maximum number of trades to return.

    Returns:
        TradesArgs: Validated trade query arguments.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> args = TradesArgs(user="0xabc", limit=10)
        >>> args.limit
        10
    """

    model_config = ConfigDict(extra="forbid")

    market: str | None = None
    user: str | None = None
    limit: int = Field(default=25, ge=1, le=200)


class Position(BaseModel):
    """Normalized wallet position model."""

    model_config = ConfigDict(extra="allow")

    market_slug: str | None = None
    title: str | None = None
    outcome: str | None = None
    size: float | None = None
    avg_price: float | None = None
    current_value: float | None = None
    realized_pnl: float | None = None
    unrealized_pnl: float | None = None


class ActivityItem(BaseModel):
    """Normalized wallet activity model."""

    model_config = ConfigDict(extra="allow")

    activity_type: str | None = None
    market_slug: str | None = None
    title: str | None = None
    outcome: str | None = None
    price: float | None = None
    size: float | None = None
    timestamp: int | None = None


class Trade(BaseModel):
    """Normalized trade model."""

    model_config = ConfigDict(extra="allow")

    market_slug: str | None = None
    outcome: str | None = None
    price: float | None = None
    size: float | None = None
    side: str | None = None
    user: str | None = None
    timestamp: int | None = None


class WalletPositionsOutput(BaseModel):
    """Tool output for current or closed wallet positions."""

    model_config = ConfigDict(extra="forbid")

    user: str
    positions: list[Position] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of positions.

        Returns:
            int: Number of returned positions.
        """
        return len(self.positions)


class WalletActivityOutput(BaseModel):
    """Tool output for wallet activity."""

    model_config = ConfigDict(extra="forbid")

    user: str
    activity: list[ActivityItem] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of activity rows.

        Returns:
            int: Number of returned rows.
        """
        return len(self.activity)


class TradesOutput(BaseModel):
    """Tool output for trade queries."""

    model_config = ConfigDict(extra="forbid")

    trades: list[Trade] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of trades.

        Returns:
            int: Number of returned trades.
        """
        return len(self.trades)
