"""Typed Gamma API service adapter.

Purpose:
    Fetch Polymarket Gamma data and normalize it into stable domain models.

Design:
    This module is the normalization boundary between raw upstream payloads and
    the rest of the package. MCP-facing code should depend on these typed
    models rather than raw JSON dictionaries.

Attributes:
    GammaService:
        Service wrapper for Gamma market-discovery endpoints.
"""

from __future__ import annotations

from typing import Any

from polymarket_mcp.http import JsonHttpClient
from polymarket_mcp.models.gamma import (
    Event,
    ListEventsArgs,
    ListMarketsArgs,
    Market,
    SearchPublicArgs,
)
from polymarket_mcp.settings import AppSettings


def _to_optional_str(value: object) -> str | None:
    """Coerce a value to an optional string.

    Args:
        value: Arbitrary upstream value.

    Returns:
        str | None: String value when present, otherwise ``None``.

    Raises:
        None.

    Examples:
        >>> _to_optional_str(123)
        '123'
        >>> _to_optional_str(None) is None
        True
    """
    if value is None:
        return None
    return str(value)


def _to_optional_bool(value: object) -> bool | None:
    """Coerce a value to an optional boolean.

    Args:
        value: Arbitrary upstream value.

    Returns:
        bool | None: Boolean value when clearly coercible, otherwise ``None``.

    Raises:
        None.

    Examples:
        >>> _to_optional_bool(True)
        True
        >>> _to_optional_bool(None) is None
        True
    """
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return bool(value)


def _to_optional_float(value: object) -> float | None:
    """Coerce a value to an optional float.

    Args:
        value: Arbitrary upstream value.

    Returns:
        float | None: Float value when coercible, otherwise ``None``.

    Raises:
        ValueError: If coercion fails.

    Examples:
        >>> _to_optional_float("1.25")
        1.25
        >>> _to_optional_float(None) is None
        True
    """
    if value is None:
        return None
    return float(value)


def _coerce_token_ids(value: object) -> list[str]:
    """Normalize CLOB token identifiers into a string list.

    Args:
        value: Upstream token identifier payload.

    Returns:
        list[str]: Normalized token IDs.

    Raises:
        None.

    Examples:
        >>> _coerce_token_ids(["1", 2])
        ['1', '2']
        >>> _coerce_token_ids(None)
        []
    """
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


class GammaService:
    """Service wrapper for Polymarket Gamma.

    Args:
        settings: Application settings.

    Returns:
        GammaService: Configured service adapter.

    Raises:
        None.

    Examples:
        >>> from polymarket_mcp.settings import load_settings
        >>> service = GammaService(load_settings())
        >>> service.__class__.__name__
        'GammaService'
    """

    def __init__(self, settings: AppSettings) -> None:
        self._client = JsonHttpClient(
            base_url=settings.gamma_base_url,
            timeout=settings.request_timeout_seconds,
            domain="gamma",
            user_agent=settings.user_agent,
        )

    def _normalize_market(self, payload: dict[str, Any]) -> Market:
        """Normalize a raw Gamma market payload.

        Args:
            payload: Upstream market dictionary.

        Returns:
            Market: Normalized market model.

        Raises:
            KeyError: If required upstream fields are missing.

        Examples:
            >>> service = object.__new__(GammaService)
            >>> market = service._normalize_market({"slug": "x"})
            >>> market.slug
            'x'
        """
        return Market(
            id=_to_optional_str(payload.get("id")),
            slug=str(payload["slug"]),
            question=_to_optional_str(payload.get("question")),
            active=_to_optional_bool(payload.get("active")),
            closed=_to_optional_bool(payload.get("closed")),
            liquidity=_to_optional_float(payload.get("liquidity")),
            volume=_to_optional_float(payload.get("volume")),
            event_slug=(
                _to_optional_str(payload.get("eventSlug"))
                or _to_optional_str(payload.get("event_slug"))
            ),
            clob_token_ids=_coerce_token_ids(
                payload.get("clobTokenIds") or payload.get("clob_token_ids")
            ),
        )

    def _normalize_event(self, payload: dict[str, Any]) -> Event:
        """Normalize a raw Gamma event payload.

        Args:
            payload: Upstream event dictionary.

        Returns:
            Event: Normalized event model.

        Raises:
            KeyError: If required upstream fields are missing.

        Examples:
            >>> service = object.__new__(GammaService)
            >>> event = service._normalize_event({"slug": "x"})
            >>> event.slug
            'x'
        """
        raw_markets = payload.get("markets") or []
        markets = [
            self._normalize_market(item)
            for item in raw_markets
            if isinstance(item, dict)
        ]
        return Event(
            id=_to_optional_str(payload.get("id")),
            slug=str(payload["slug"]),
            title=(
                _to_optional_str(payload.get("title"))
                or _to_optional_str(payload.get("name"))
            ),
            active=_to_optional_bool(payload.get("active")),
            closed=_to_optional_bool(payload.get("closed")),
            markets=markets,
        )

    async def search_public(self, args: SearchPublicArgs) -> list[Market]:
        """Search Gamma public entities and return normalized markets.

        Args:
            args: Structured free-text search arguments.

        Returns:
            list[Market]: Matching normalized markets.

        Raises:
            httpx.HTTPError: If the upstream request fails.

        Examples:
            .. code-block:: python

                service = GammaService(settings)
                markets = await service.search_public(
                    SearchPublicArgs(query="fed decision", limit=5),
                )
        """
        data = await self._client.get(
            "/public-search",
            params=args.model_dump(exclude_none=True),
        )

        if isinstance(data, list):
            raw_candidates = data
        elif isinstance(data, dict):
            raw_candidates = data.get("markets") or data.get("data") or []
        else:
            raw_candidates = []

        return [
            self._normalize_market(item)
            for item in raw_candidates
            if isinstance(item, dict) and item.get("slug")
        ]

    async def list_markets(self, args: ListMarketsArgs) -> list[Market]:
        """List Gamma markets as normalized models.

        Args:
            args: Structured market filter arguments.

        Returns:
            list[Market]: Matching normalized markets.

        Raises:
            httpx.HTTPError: If the upstream request fails.

        Examples:
            .. code-block:: python

                markets = await service.list_markets(
                    ListMarketsArgs(limit=5, active=True),
                )
        """
        data = await self._client.get(
            "/markets",
            params=args.model_dump(exclude_none=True),
        )
        return [
            self._normalize_market(item)
            for item in data
            if isinstance(item, dict) and item.get("slug")
        ]

    async def get_market_by_slug(self, slug: str) -> Market:
        """Get one market by slug.

        Args:
            slug: Canonical market slug from the Polymarket URL.

        Returns:
            Market: Matching normalized market.

        Raises:
            httpx.HTTPError: If the upstream request fails.
            KeyError: If the upstream payload is missing required fields.

        Examples:
            .. code-block:: python

                market = await service.get_market_by_slug("fed-decision")
        """
        data = await self._client.get(f"/markets/slug/{slug}")
        return self._normalize_market(data)

    async def list_events(self, args: ListEventsArgs) -> list[Event]:
        """List Gamma events as normalized models.

        Args:
            args: Structured event filter arguments.

        Returns:
            list[Event]: Matching normalized events.

        Raises:
            httpx.HTTPError: If the upstream request fails.

        Examples:
            .. code-block:: python

                events = await service.list_events(
                    ListEventsArgs(limit=5, active=True),
                )
        """
        data = await self._client.get(
            "/events",
            params=args.model_dump(exclude_none=True),
        )
        return [
            self._normalize_event(item)
            for item in data
            if isinstance(item, dict) and item.get("slug")
        ]

    async def get_event_by_slug(self, slug: str) -> Event:
        """Get one event by slug.

        Args:
            slug: Canonical event slug from the Polymarket URL.

        Returns:
            Event: Matching normalized event.

        Raises:
            httpx.HTTPError: If the upstream request fails.
            KeyError: If the upstream payload is missing required fields.

        Examples:
            .. code-block:: python

                event = await service.get_event_by_slug("fed-event")
        """
        data = await self._client.get(f"/events/slug/{slug}")
        return self._normalize_event(data)

    async def list_tags(self) -> list[dict[str, Any]]:
        """List raw Gamma tags.

        Args:
            None.

        Returns:
            list[dict[str, Any]]: Tag payloads.

        Raises:
            httpx.HTTPError: If the upstream request fails.
        """
        data = await self._client.get("/tags")
        return list(data)

    async def list_series(self) -> list[dict[str, Any]]:
        """List raw Gamma series.

        Args:
            None.

        Returns:
            list[dict[str, Any]]: Series payloads.

        Raises:
            httpx.HTTPError: If the upstream request fails.
        """
        data = await self._client.get("/series")
        return list(data)

    async def list_sports(self) -> list[dict[str, Any]]:
        """List raw Gamma sports metadata.

        Args:
            None.

        Returns:
            list[dict[str, Any]]: Sports payloads.

        Raises:
            httpx.HTTPError: If the upstream request fails.
        """
        data = await self._client.get("/sports")
        return list(data)

    async def list_teams(self) -> list[dict[str, Any]]:
        """List raw Gamma teams metadata.

        Args:
            None.

        Returns:
            list[dict[str, Any]]: Team payloads.

        Raises:
            httpx.HTTPError: If the upstream request fails.
        """
        data = await self._client.get("/teams")
        return list(data)
