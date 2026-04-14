"""Typed CLOB public domain and tool I/O models.

Purpose:
    Define normalized public order book, pricing, and history models for the
    Polymarket CLOB API along with MCP inputs and outputs.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field


class TokenArgs(BaseModel):
    """Arguments for single-token CLOB reads."""

    model_config = ConfigDict(extra="forbid")

    token_id: str = Field(min_length=1)


class TokensArgs(BaseModel):
    """Arguments for multi-token CLOB reads."""

    model_config = ConfigDict(extra="forbid")

    token_ids: list[str] = Field(min_length=1, max_length=50)


class PriceHistoryArgs(BaseModel):
    """Arguments for price history reads."""

    model_config = ConfigDict(extra="forbid")

    token_id: str = Field(min_length=1)
    interval: str = "1h"
    start_ts: int | None = None
    end_ts: int | None = None


class OrderBookLevel(BaseModel):
    """Single normalized order book level."""

    model_config = ConfigDict(extra="forbid")

    price: float
    size: float


class OrderBook(BaseModel):
    """Normalized public order book."""

    model_config = ConfigDict(extra="allow")

    token_id: str
    bids: list[OrderBookLevel] = Field(default_factory=list)
    asks: list[OrderBookLevel] = Field(default_factory=list)
    midpoint: float | None = None
    spread: float | None = None
    timestamp: int | None = None


class PriceQuote(BaseModel):
    """Normalized price quote."""

    model_config = ConfigDict(extra="allow")

    token_id: str
    price: float | None = None
    midpoint: float | None = None
    spread: float | None = None


class PriceHistoryPoint(BaseModel):
    """Normalized historical price point."""

    model_config = ConfigDict(extra="allow")

    timestamp: int
    price: float


class OrderBookOutput(BaseModel):
    """Tool output for one order book."""

    model_config = ConfigDict(extra="forbid")

    book: OrderBook


class PriceQuoteOutput(BaseModel):
    """Tool output for one price quote."""

    model_config = ConfigDict(extra="forbid")

    quote: PriceQuote


class PriceQuotesOutput(BaseModel):
    """Tool output for multiple price quotes."""

    model_config = ConfigDict(extra="forbid")

    quotes: list[PriceQuote] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of quotes.

        Returns:
            int: Number of returned quotes.
        """
        return len(self.quotes)


class PriceHistoryOutput(BaseModel):
    """Tool output for historical prices."""

    model_config = ConfigDict(extra="forbid")

    token_id: str
    interval: str
    points: list[PriceHistoryPoint] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of history points.

        Returns:
            int: Number of returned points.
        """
        return len(self.points)
