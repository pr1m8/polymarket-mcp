"""Typed public CLOB service adapter.

Purpose:
    Fetch Polymarket public order book and pricing payloads and normalize them
    into stable models.
"""

from __future__ import annotations

from typing import Any

from polymarket_mcp.http import JsonHttpClient
from polymarket_mcp.models.clob import (
    OrderBook,
    OrderBookLevel,
    PriceHistoryArgs,
    PriceHistoryPoint,
    PriceQuote,
    TokenArgs,
    TokensArgs,
)
from polymarket_mcp.settings import AppSettings


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


class ClobPublicService:
    """Service wrapper for public CLOB endpoints.

    Args:
        settings: Application settings.

    Returns:
        ClobPublicService: Configured service adapter.
    """

    def __init__(self, settings: AppSettings) -> None:
        self._client = JsonHttpClient(
            base_url=settings.clob_base_url,
            timeout=settings.request_timeout_seconds,
            domain="clob",
            user_agent=settings.user_agent,
        )

    def _normalize_level(self, payload: object) -> OrderBookLevel | None:
        """Normalize one book level.

        Args:
            payload: Upstream level payload.

        Returns:
            OrderBookLevel | None: Normalized level when parseable.
        """
        if not isinstance(payload, dict):
            return None
        price = _to_optional_float(payload.get("price"))
        size = _to_optional_float(payload.get("size"))
        if price is None or size is None:
            return None
        return OrderBookLevel(price=price, size=size)

    def _normalize_book(self, token_id: str, payload: dict[str, Any]) -> OrderBook:
        """Normalize one book payload.

        Args:
            token_id: Token identifier used for the lookup.
            payload: Upstream book payload.

        Returns:
            OrderBook: Normalized order book.
        """
        bids = [
            level
            for item in payload.get("bids", [])
            if (level := self._normalize_level(item)) is not None
        ]
        asks = [
            level
            for item in payload.get("asks", [])
            if (level := self._normalize_level(item)) is not None
        ]
        return OrderBook(
            token_id=token_id,
            bids=bids,
            asks=asks,
            midpoint=_to_optional_float(payload.get("midpoint")),
            spread=_to_optional_float(payload.get("spread")),
            timestamp=_to_optional_int(payload.get("timestamp")),
        )

    def _normalize_quote(self, token_id: str, payload: dict[str, Any]) -> PriceQuote:
        """Normalize one quote payload.

        Args:
            token_id: Token identifier used for the lookup.
            payload: Upstream quote payload.

        Returns:
            PriceQuote: Normalized quote.
        """
        return PriceQuote(
            token_id=token_id,
            price=_to_optional_float(payload.get("price")),
            midpoint=_to_optional_float(payload.get("midpoint")),
            spread=_to_optional_float(payload.get("spread")),
        )

    async def get_book(self, args: TokenArgs) -> OrderBook:
        """Get one normalized order book.

        Args:
            args: Single-token lookup arguments.

        Returns:
            OrderBook: Normalized order book.
        """
        data = await self._client.get("/book", params=args.model_dump())
        return self._normalize_book(args.token_id, data)

    async def get_books(self, args: TokensArgs) -> list[OrderBook]:
        """Get multiple normalized order books.

        Args:
            args: Multi-token lookup arguments.

        Returns:
            list[OrderBook]: Normalized order books.
        """
        data = await self._client.post("/books", json_body=args.model_dump())
        if isinstance(data, list):
            raw_books = data
        elif isinstance(data, dict):
            raw_books = data.get("books") or data.get("data") or []
        else:
            raw_books = []

        books: list[OrderBook] = []
        for token_id, payload in zip(args.token_ids, raw_books, strict=False):
            if isinstance(payload, dict):
                books.append(self._normalize_book(token_id, payload))
        return books

    async def get_price(self, args: TokenArgs) -> PriceQuote:
        """Get one normalized price quote.

        Args:
            args: Single-token lookup arguments.

        Returns:
            PriceQuote: Normalized price quote.
        """
        data = await self._client.get("/price", params=args.model_dump())
        return self._normalize_quote(args.token_id, data)

    async def get_prices(self, args: TokensArgs) -> list[PriceQuote]:
        """Get multiple normalized price quotes.

        Args:
            args: Multi-token lookup arguments.

        Returns:
            list[PriceQuote]: Normalized price quotes.
        """
        data = await self._client.get(
            "/prices",
            params={"token_ids": ",".join(args.token_ids)},
        )

        quotes: list[PriceQuote] = []
        if isinstance(data, dict):
            for token_id in args.token_ids:
                payload = data.get(token_id)
                if isinstance(payload, dict):
                    quotes.append(self._normalize_quote(token_id, payload))
                else:
                    quotes.append(
                        PriceQuote(
                            token_id=token_id,
                            price=_to_optional_float(payload),
                        )
                    )
        return quotes

    async def get_midpoint(self, args: TokenArgs) -> PriceQuote:
        """Get midpoint data for one token.

        Args:
            args: Single-token lookup arguments.

        Returns:
            PriceQuote: Quote with midpoint populated when available.
        """
        data = await self._client.get("/midpoint", params=args.model_dump())
        if isinstance(data, dict):
            return self._normalize_quote(args.token_id, data)
        return PriceQuote(token_id=args.token_id, midpoint=_to_optional_float(data))

    async def get_spread(self, args: TokenArgs) -> PriceQuote:
        """Get spread data for one token.

        Args:
            args: Single-token lookup arguments.

        Returns:
            PriceQuote: Quote with spread populated when available.
        """
        data = await self._client.get("/spread", params=args.model_dump())
        if isinstance(data, dict):
            return self._normalize_quote(args.token_id, data)
        return PriceQuote(token_id=args.token_id, spread=_to_optional_float(data))

    async def get_price_history(self, args: PriceHistoryArgs) -> list[PriceHistoryPoint]:
        """Get normalized historical prices.

        Args:
            args: History query arguments.

        Returns:
            list[PriceHistoryPoint]: Historical price points.
        """
        data = await self._client.get(
            "/prices-history",
            params=args.model_dump(exclude_none=True),
        )

        if isinstance(data, dict):
            raw_points = data.get("history") or data.get("data") or []
        elif isinstance(data, list):
            raw_points = data
        else:
            raw_points = []

        points: list[PriceHistoryPoint] = []
        for item in raw_points:
            if not isinstance(item, dict):
                continue
            timestamp = _to_optional_int(item.get("timestamp") or item.get("t"))
            price = _to_optional_float(item.get("price") or item.get("p"))
            if timestamp is None or price is None:
                continue
            points.append(PriceHistoryPoint(timestamp=timestamp, price=price))
        return points
