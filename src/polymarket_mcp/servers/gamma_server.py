"""FastMCP Gamma server for Polymarket market discovery.

Purpose:
    Expose Polymarket Gamma discovery capabilities as MCP tools and resources.

Design:
    This module is intentionally read-only. Tool docstrings are written for
    LLM-facing tool selection and explain when each tool should be used,
    how identifiers should be supplied, and which follow-up tools are likely
    helpful.

Attributes:
    mcp:
        FastMCP server instance for Gamma discovery.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

from polymarket_mcp.models.gamma import (
    EventDetailOutput,
    ListEventsArgs,
    ListEventsOutput,
    ListMarketsArgs,
    MarketDetailOutput,
    SearchMarketsOutput,
    SearchPublicArgs,
)
from polymarket_mcp.services.gamma import GammaService
from polymarket_mcp.settings import load_settings

settings = load_settings()
service = GammaService(settings)

mcp = FastMCP(
    name="polymarket-gamma",
    instructions=(
        "Use this server for Polymarket market discovery. "
        "Prefer these tools when you need to find markets or events by topic, "
        "slug, or category. Do not use this server for live order book pricing "
        "or trading actions."
    ),
    mask_error_details=True,
    strict_input_validation=True,
)


@mcp.tool
async def search_public(args: SearchPublicArgs) -> SearchMarketsOutput:
    """Search Polymarket discovery data by free-text topic.

    Use this tool when you know a topic or phrase but do not yet know the exact
    market slug. This is the best first step for queries like "Fed decision",
    "NBA finals", or "election odds".

    Prefer this tool over ``get_market_by_slug`` when you only have a natural
    language description. Prefer ``list_markets`` when you already have a more
    structured filter such as a known tag or exact slug.

    The ``query`` should be plain human text, not a full URL. The result
    returns normalized markets that can be followed up with
    ``get_market_by_slug`` for a more precise single-market lookup. If you need
    live pricing or the order book next, use the CLOB public server after you
    obtain the market's token IDs.

    Args:
        args: Structured free-text search arguments.

    Returns:
        SearchMarketsOutput: Matching normalized markets and a count field.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            result = await search_public(
                SearchPublicArgs(query="fed decision", limit=5),
            )
    """
    markets = await service.search_public(args)
    return SearchMarketsOutput(query=args.query, markets=markets)


@mcp.tool
async def list_markets(args: ListMarketsArgs) -> SearchMarketsOutput:
    """List or filter markets when you already have structured constraints.

    Use this tool when you want market discovery with explicit filters such as
    active-only results, a tag ID, a series slug, or an exact slug. This is
    more structured than free-text search.

    Prefer this tool over ``search_public`` when you already know the filtering
    dimension. Prefer ``get_market_by_slug`` when you already know the exact
    market slug and want a single canonical result.

    A slug should be the Polymarket slug string from the URL, not the full URL
    itself. This tool returns normalized market objects that may include
    ``clob_token_ids`` for later live-price lookups in the CLOB server.

    Args:
        args: Structured market filter arguments.

    Returns:
        SearchMarketsOutput: Matching normalized markets and a count field.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            result = await list_markets(
                ListMarketsArgs(limit=10, active=True, closed=False),
            )
    """
    markets = await service.list_markets(args)
    return SearchMarketsOutput(query=args.slug or "", markets=markets)


@mcp.tool
async def get_market_by_slug(slug: str) -> MarketDetailOutput:
    """Fetch one canonical market by its slug.

    Use this tool when you already know the exact market slug and want the
    clearest single-market lookup. This is the preferred tool after a search
    step has identified the correct market.

    Do not use this tool for broad discovery across a topic; use
    ``search_public`` or ``list_markets`` first in that case. The slug should
    be the market slug string from the Polymarket URL path, not the full URL.

    This tool is often followed by CLOB book or price lookups if you want live
    market state, or by event lookup if you want the parent event context.

    Args:
        slug: Canonical market slug from a Polymarket market URL.

    Returns:
        MarketDetailOutput: Single normalized market payload.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            result = await get_market_by_slug("fed-decision-in-june")
    """
    market = await service.get_market_by_slug(slug)
    return MarketDetailOutput(market=market)


@mcp.tool
async def list_events(args: ListEventsArgs) -> ListEventsOutput:
    """List or filter event groups that contain one or more markets.

    Use this tool when you want broader event-level discovery rather than
    individual market-level discovery. Events often provide better context for
    finding clusters of related markets under one theme.

    Prefer this tool over ``list_markets`` when the user asks about a broader
    topic and you want grouped context first. Prefer ``get_event_by_slug`` when
    you already know the exact event slug.

    Event results may include nested market objects, which makes this tool a
    good starting point for collecting related market slugs and token IDs.

    Args:
        args: Structured event filter arguments.

    Returns:
        ListEventsOutput: Matching normalized events and a count field.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            result = await list_events(
                ListEventsArgs(limit=5, active=True, closed=False),
            )
    """
    events = await service.list_events(args)
    return ListEventsOutput(events=events)


@mcp.tool
async def get_event_by_slug(slug: str) -> EventDetailOutput:
    """Fetch one canonical event by its slug.

    Use this tool when you already know the event slug and want the full
    event-level context, including any nested markets returned by Gamma.

    Prefer this tool when the question is about an event grouping rather than a
    single market. If you only know the topic in natural language, use
    ``search_public`` or ``list_events`` first.

    The slug should be the event slug string from the Polymarket URL path, not
    the full URL. This tool is especially helpful for finding all related
    markets under one event before selecting a specific market for deeper
    analysis.

    Args:
        slug: Canonical event slug from a Polymarket event URL.

    Returns:
        EventDetailOutput: Single normalized event payload.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            result = await get_event_by_slug("fed-rate-decision")
    """
    event = await service.get_event_by_slug(slug)
    return EventDetailOutput(event=event)


@mcp.tool
async def list_tags() -> list[dict[str, object]]:
    """List available discovery tags for category-based exploration.

    Use this tool when you need category metadata such as politics, crypto, or
    sports-style groupings and want to drive a later structured market query.

    Prefer this tool before ``list_markets`` when the user wants markets from a
    category but you do not yet know the numeric tag identifier. Once the tag
    is known, switch to a structured market listing tool.

    Args:
        None.

    Returns:
        list[dict[str, object]]: Raw tag payloads from Gamma.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            tags = await list_tags()
    """
    return await service.list_tags()


@mcp.tool
async def list_series() -> list[dict[str, object]]:
    """List available series metadata for structured discovery.

    Use this tool when the user refers to a known series or recurring grouping
    and you need series metadata before filtering markets with a series slug.

    Prefer this tool when discovery is series-oriented rather than free-text
    topic-oriented. For general search, use ``search_public`` instead.

    Args:
        None.

    Returns:
        list[dict[str, object]]: Raw series payloads from Gamma.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            series = await list_series()
    """
    return await service.list_series()


@mcp.tool
async def list_sports() -> list[dict[str, object]]:
    """List sports metadata for sports-related discovery flows.

    Use this tool when the user is exploring sports markets and you need sport
    metadata before narrowing to teams, events, or markets.

    Prefer this tool when the question is explicitly sports-oriented. For a
    direct market/topic search, ``search_public`` is usually a faster first
    step.

    Args:
        None.

    Returns:
        list[dict[str, object]]: Raw sports payloads from Gamma.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            sports = await list_sports()
    """
    return await service.list_sports()


@mcp.tool
async def list_teams() -> list[dict[str, object]]:
    """List team metadata for sports-market exploration.

    Use this tool when a sports workflow needs team-level metadata before
    finding related events or markets.

    Prefer this tool after identifying a sport or when the user explicitly asks
    about teams. For non-sports discovery, use other Gamma tools instead.

    Args:
        None.

    Returns:
        list[dict[str, object]]: Raw team payloads from Gamma.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            teams = await list_teams()
    """
    return await service.list_teams()


@mcp.resource("polymarket://gamma/market/{slug}")
async def market_resource(slug: str) -> str:
    """Read a canonical market resource by slug.

    Args:
        slug: Canonical market slug.

    Returns:
        str: JSON-encoded normalized market payload.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            text = await market_resource("fed-decision-in-june")
    """
    payload = MarketDetailOutput(market=await service.get_market_by_slug(slug))
    return json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)


@mcp.resource("polymarket://gamma/event/{slug}")
async def event_resource(slug: str) -> str:
    """Read a canonical event resource by slug.

    Args:
        slug: Canonical event slug.

    Returns:
        str: JSON-encoded normalized event payload.

    Raises:
        httpx.HTTPError: If the upstream Gamma request fails.

    Examples:
        .. code-block:: python

            text = await event_resource("fed-rate-decision")
    """
    payload = EventDetailOutput(event=await service.get_event_by_slug(slug))
    return json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
