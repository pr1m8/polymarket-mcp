"""Tests for Data API service normalization."""

from __future__ import annotations

import pytest

from polymarket_mcp.models.data import TradesArgs, WalletArgs
from polymarket_mcp.services.data import DataApiService
from polymarket_mcp.settings import load_settings


@pytest.mark.asyncio
async def test_get_positions_normalizes_wallet_positions(monkeypatch: pytest.MonkeyPatch) -> None:
    """Current positions should normalize mixed payload key styles."""
    service = DataApiService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/positions"
        assert params == {"user": "0xabc"}
        return [
            {
                "marketSlug": "fed-cut",
                "question": "Will the Fed cut?",
                "outcome": "Yes",
                "size": "12.5",
                "avgPrice": "0.41",
                "currentValue": "7.8",
                "realizedPnl": "1.2",
                "unrealizedPnl": "0.5",
            }
        ]

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.get_positions(WalletArgs(user="0xabc"))

    assert len(result) == 1
    assert result[0].market_slug == "fed-cut"
    assert result[0].title == "Will the Fed cut?"
    assert result[0].avg_price == 0.41
    assert result[0].realized_pnl == 1.2


@pytest.mark.asyncio
async def test_get_activity_normalizes_recent_activity(monkeypatch: pytest.MonkeyPatch) -> None:
    """Wallet activity should normalize type, market, and timestamp fields."""
    service = DataApiService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/activity"
        assert params == {"user": "0xabc"}
        return [
            {
                "type": "buy",
                "market_slug": "fed-cut",
                "title": "Will the Fed cut?",
                "outcome": "Yes",
                "price": "0.45",
                "size": "3",
                "time": "1700000000",
            }
        ]

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.get_activity(WalletArgs(user="0xabc"))

    assert len(result) == 1
    assert result[0].activity_type == "buy"
    assert result[0].market_slug == "fed-cut"
    assert result[0].timestamp == 1700000000


@pytest.mark.asyncio
async def test_get_trades_normalizes_trade_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """Trade rows should normalize user, side, and timestamp fields."""
    service = DataApiService(load_settings())

    async def fake_get(path: str, *, params: dict[str, object] | None = None):
        assert path == "/trades"
        assert params == {"user": "0xabc", "limit": 10}
        return [
            {
                "marketSlug": "fed-cut",
                "outcome": "Yes",
                "price": "0.55",
                "size": "8",
                "side": "buy",
                "user": "0xabc",
                "time": "1700000001",
            }
        ]

    monkeypatch.setattr(service._client, "get", fake_get)

    result = await service.get_trades(TradesArgs(user="0xabc", limit=10))

    assert len(result) == 1
    assert result[0].side == "buy"
    assert result[0].user == "0xabc"
    assert result[0].timestamp == 1700000001
