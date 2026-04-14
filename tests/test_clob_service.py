"""Tests for public CLOB service normalization."""

from __future__ import annotations

import pytest

from polymarket_mcp.models.clob import PriceHistoryArgs, TokenArgs, TokensArgs
from polymarket_mcp.services.clob_public import ClobPublicService
from polymarket_mcp.settings import load_settings


@pytest.mark.asyncio
async def test_get_book_normalizes_bids_and_asks(monkeypatch: pytest.MonkeyPatch) -> None:
    """Order books should normalize levels and summary fields."""
    service = ClobPublicService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/book"
        assert params == {"token_id": "123"}
        return {
            "bids": [{"price": "0.48", "size": "10"}],
            "asks": [{"price": "0.52", "size": "12"}],
            "midpoint": "0.50",
            "spread": "0.04",
            "timestamp": "1700000002",
        }

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.get_book(TokenArgs(token_id="123"))

    assert result.token_id == "123"
    assert result.bids[0].price == 0.48
    assert result.asks[0].size == 12.0
    assert result.midpoint == 0.5
    assert result.timestamp == 1700000002


@pytest.mark.asyncio
async def test_get_prices_normalizes_mixed_quote_shapes(monkeypatch: pytest.MonkeyPatch) -> None:
    """Bulk quotes should normalize both dict and scalar payloads."""
    service = ClobPublicService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/prices"
        assert params == {"token_ids": "1,2"}
        return {
            "1": {"price": "0.4", "midpoint": "0.41", "spread": "0.02"},
            "2": "0.7",
        }

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.get_prices(TokensArgs(token_ids=["1", "2"]))

    assert len(result) == 2
    assert result[0].token_id == "1"
    assert result[0].midpoint == 0.41
    assert result[1].token_id == "2"
    assert result[1].price == 0.7


@pytest.mark.asyncio
async def test_get_price_history_normalizes_history_points(monkeypatch: pytest.MonkeyPatch) -> None:
    """Historical price reads should normalize time-series points."""
    service = ClobPublicService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/prices-history"
        assert params == {"token_id": "123", "interval": "1h"}
        return {"history": [{"t": "1", "p": "0.4"}, {"timestamp": "2", "price": "0.5"}]}

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.get_price_history(PriceHistoryArgs(token_id="123", interval="1h"))

    assert [point.timestamp for point in result] == [1, 2]
    assert [point.price for point in result] == [0.4, 0.5]
