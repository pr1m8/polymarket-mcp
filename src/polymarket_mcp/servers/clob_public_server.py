"""FastMCP public CLOB server for Polymarket order books and pricing.

Purpose:
    Expose read-only order book, quote, and history tools for the Polymarket
    CLOB API.

Design:
    This module is for live market-state reads only. Tool docstrings help an
    LLM choose the correct tool for books, spot quotes, midpoint/spread, and
    historical price queries.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

from polymarket_mcp.models.clob import (
    OrderBookOutput,
    PriceHistoryArgs,
    PriceHistoryOutput,
    PriceQuoteOutput,
    PriceQuotesOutput,
    TokenArgs,
    TokensArgs,
)
from polymarket_mcp.services.clob_public import ClobPublicService
from polymarket_mcp.settings import load_settings

settings = load_settings()
service = ClobPublicService(settings)

mcp = FastMCP(
    name="polymarket-clob-public",
    instructions=(
        "Use this server for live public order book and pricing reads. "
        "Do not use it for market discovery or wallet analytics."
    ),
    mask_error_details=True,
    strict_input_validation=True,
)


@mcp.tool
async def get_book(args: TokenArgs) -> OrderBookOutput:
    """Fetch the current order book for one token.

    Use this tool when the user wants live market microstructure such as bids,
    asks, depth, spread, or liquidity around the current price.

    Prefer this tool over ``get_price`` when depth matters, not just the current
    quote. Do not use this tool for market discovery; Gamma tools are better
    for finding the right market or token first.

    The input should be a single CLOB token ID, not a market slug or wallet
    address. A common next step is to summarize book depth or compare books
    across multiple tokens.

    Args:
        args: Single-token lookup arguments.

    Returns:
        OrderBookOutput: One normalized order book.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_book(TokenArgs(token_id="123"))
    """
    return OrderBookOutput(book=await service.get_book(args))


@mcp.tool
async def get_books(args: TokensArgs) -> list[OrderBookOutput]:
    """Fetch current order books for multiple tokens.

    Use this tool when the user wants to compare liquidity or depth across
    several known tokens at once.

    Prefer this tool over repeated single-token lookups when you already know
    multiple token IDs. Do not use this tool if you still need to identify
    which market or token is relevant.

    The input should be a list of CLOB token IDs. A common next step is to rank
    the returned books by spread, depth, or visible liquidity.

    Args:
        args: Multi-token lookup arguments.

    Returns:
        list[OrderBookOutput]: Normalized order books in bulk.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_books(TokensArgs(token_ids=["1", "2"]))
    """
    return [OrderBookOutput(book=book) for book in await service.get_books(args)]


@mcp.tool
async def get_price(args: TokenArgs) -> PriceQuoteOutput:
    """Fetch a current price quote for one token.

    Use this tool when the user wants the current quoted price or implied level
    for a known token but does not need the full order book.

    Prefer this tool over ``get_book`` when a lightweight spot quote is enough.
    Prefer ``get_midpoint`` or ``get_spread`` when the question is specifically
    about those metrics.

    The input should be a single CLOB token ID. A common next step is to
    compare the quote with historical prices or fetch the full book.

    Args:
        args: Single-token lookup arguments.

    Returns:
        PriceQuoteOutput: One normalized price quote.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_price(TokenArgs(token_id="123"))
    """
    return PriceQuoteOutput(quote=await service.get_price(args))


@mcp.tool
async def get_prices(args: TokensArgs) -> PriceQuotesOutput:
    """Fetch current price quotes for multiple tokens.

    Use this tool when the user wants a quick multi-token quote snapshot without
    needing full order books for each token.

    Prefer this tool over repeated single-token quote calls when several token
    IDs are already known. Do not use this tool for discovery or wallet-level
    analysis.

    The input should be a list of CLOB token IDs. A common next step is to rank
    tokens by price or follow up with ``get_book`` on the most interesting ones.

    Args:
        args: Multi-token lookup arguments.

    Returns:
        PriceQuotesOutput: Multiple normalized price quotes.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_prices(TokensArgs(token_ids=["1", "2"]))
    """
    return PriceQuotesOutput(quotes=await service.get_prices(args))


@mcp.tool
async def get_midpoint(args: TokenArgs) -> PriceQuoteOutput:
    """Fetch the midpoint for one token.

    Use this tool when the user specifically wants the midpoint rather than a
    full order book or generic quote.

    Prefer this tool when reasoning about fair value between best bid and best
    ask. If depth matters too, use ``get_book`` instead.

    The input should be a single CLOB token ID.

    Args:
        args: Single-token lookup arguments.

    Returns:
        PriceQuoteOutput: Quote object with midpoint populated when available.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_midpoint(TokenArgs(token_id="123"))
    """
    return PriceQuoteOutput(quote=await service.get_midpoint(args))


@mcp.tool
async def get_spread(args: TokenArgs) -> PriceQuoteOutput:
    """Fetch the spread for one token.

    Use this tool when the user specifically wants transaction tightness,
    execution quality hints, or a quick liquidity proxy.

    Prefer this tool over ``get_book`` when only the spread is needed. If the
    user wants depth and book shape too, use ``get_book``.

    The input should be a single CLOB token ID.

    Args:
        args: Single-token lookup arguments.

    Returns:
        PriceQuoteOutput: Quote object with spread populated when available.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_spread(TokenArgs(token_id="123"))
    """
    return PriceQuoteOutput(quote=await service.get_spread(args))


@mcp.tool
async def get_price_history(args: PriceHistoryArgs) -> PriceHistoryOutput:
    """Fetch historical price points for one token.

    Use this tool when the user wants trend, momentum, or time-series context
    for a known token.

    Prefer this tool over ``get_price`` when the question is about change over
    time rather than the current quote. Do not use this tool if the token ID is
    not yet known; use Gamma discovery first.

    The input should be a single CLOB token ID plus an interval and optional
    time bounds. A common next step is to summarize the trend or compare recent
    history with the current quote or spread.

    Args:
        args: Historical price query arguments.

    Returns:
        PriceHistoryOutput: Normalized historical price points.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            result = await get_price_history(
                PriceHistoryArgs(token_id="123", interval="1h"),
            )
    """
    points = await service.get_price_history(args)
    return PriceHistoryOutput(
        token_id=args.token_id,
        interval=args.interval,
        points=points,
    )


@mcp.resource("polymarket://clob/book/{token_id}")
async def book_resource(token_id: str) -> str:
    """Read the canonical order book resource for one token.

    Args:
        token_id: Single CLOB token ID.

    Returns:
        str: JSON-encoded order book payload.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            text = await book_resource("123")
    """
    payload = OrderBookOutput(book=await service.get_book(TokenArgs(token_id=token_id)))
    return json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)


@mcp.resource("polymarket://clob/price/{token_id}")
async def price_resource(token_id: str) -> str:
    """Read the canonical price resource for one token.

    Args:
        token_id: Single CLOB token ID.

    Returns:
        str: JSON-encoded price quote payload.

    Raises:
        httpx.HTTPError: If the upstream CLOB request fails.

    Examples:
        .. code-block:: python

            text = await price_resource("123")
    """
    payload = PriceQuoteOutput(quote=await service.get_price(TokenArgs(token_id=token_id)))
    return json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
