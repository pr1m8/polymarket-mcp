"""Tests for Gamma service normalization."""

from __future__ import annotations

import pytest

from polymarket_mcp.models.gamma import ListEventsArgs, ListMarketsArgs, SearchPublicArgs
from polymarket_mcp.services.gamma import GammaService
from polymarket_mcp.settings import load_settings


@pytest.mark.asyncio
async def test_gamma_search_public_normalizes_market_payloads(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gamma search should normalize list and dict payload variants."""
    service = GammaService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/public-search"
        assert params == {"query": "fed", "limit": 2}
        return {
            "markets": [
                {
                    "id": 1,
                    "slug": "fed-cut",
                    "question": "Will the Fed cut?",
                    "active": True,
                    "closed": False,
                    "liquidity": "123.4",
                    "volume": "500",
                    "eventSlug": "fed-event",
                    "clobTokenIds": [101, 202],
                }
            ]
        }

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.search_public(SearchPublicArgs(query="fed", limit=2))

    assert len(result) == 1
    assert result[0].slug == "fed-cut"
    assert result[0].liquidity == 123.4
    assert result[0].volume == 500.0
    assert result[0].event_slug == "fed-event"
    assert result[0].clob_token_ids == ["101", "202"]


@pytest.mark.asyncio
async def test_gamma_list_events_normalizes_nested_markets(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gamma events should normalize nested market payloads."""
    service = GammaService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/events"
        assert params == {"limit": 1, "active": True, "closed": False}
        return [
            {
                "id": 5,
                "slug": "fed-event",
                "title": "Fed Event",
                "active": True,
                "closed": False,
                "markets": [
                    {"slug": "fed-cut", "question": "Will the Fed cut?"},
                    {"slug": "fed-hold", "question": "Will the Fed hold?"},
                ],
            }
        ]

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.list_events(ListEventsArgs(limit=1, active=True, closed=False))

    assert len(result) == 1
    assert result[0].slug == "fed-event"
    assert [market.slug for market in result[0].markets] == ["fed-cut", "fed-hold"]


@pytest.mark.asyncio
async def test_gamma_list_markets_uses_structured_filters(monkeypatch: pytest.MonkeyPatch) -> None:
    """Gamma market listing should pass through structured filters."""
    service = GammaService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/markets"
        assert params == {
            "limit": 5,
            "active": True,
            "closed": False,
            "slug": "fed-cut",
        }
        return [{"slug": "fed-cut"}]

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.list_markets(
        ListMarketsArgs(limit=5, active=True, closed=False, slug="fed-cut")
    )

    assert [market.slug for market in result] == ["fed-cut"]
