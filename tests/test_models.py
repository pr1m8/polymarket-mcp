"""Tests for typed Polymarket MCP models."""

from __future__ import annotations

from polymarket_mcp.models.clob import PriceHistoryOutput, PriceHistoryPoint, PriceQuotesOutput, PriceQuote
from polymarket_mcp.models.data import WalletActivityOutput, WalletPositionsOutput, Position, ActivityItem, TradesOutput, Trade
from polymarket_mcp.models.gamma import SearchMarketsOutput, Market, ListEventsOutput, Event


def test_search_markets_output_count_computed_field() -> None:
    """Search market output should expose a computed count."""
    output = SearchMarketsOutput(
        query="fed",
        markets=[Market(slug="one"), Market(slug="two")],
    )

    assert output.count == 2


def test_list_events_output_count_computed_field() -> None:
    """Event listing output should expose a computed count."""
    output = ListEventsOutput(events=[Event(slug="one"), Event(slug="two")])

    assert output.count == 2


def test_data_output_counts_are_derived_from_items() -> None:
    """Wallet and trade output envelopes should count items correctly."""
    positions = WalletPositionsOutput(user="0xabc", positions=[Position(), Position()])
    activity = WalletActivityOutput(user="0xabc", activity=[ActivityItem()])
    trades = TradesOutput(trades=[Trade(), Trade(), Trade()])

    assert positions.count == 2
    assert activity.count == 1
    assert trades.count == 3


def test_clob_output_counts_are_derived_from_items() -> None:
    """CLOB output envelopes should count quotes and price points correctly."""
    quotes = PriceQuotesOutput(quotes=[PriceQuote(token_id="1"), PriceQuote(token_id="2")])
    history = PriceHistoryOutput(
        token_id="1",
        interval="1h",
        points=[
            PriceHistoryPoint(timestamp=1, price=0.5),
            PriceHistoryPoint(timestamp=2, price=0.6),
        ],
    )

    assert quotes.count == 2
    assert history.count == 2
