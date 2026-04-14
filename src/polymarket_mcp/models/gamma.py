"""Typed Gamma domain and tool I/O models.

Purpose:
    Define normalized market-discovery models for the Polymarket Gamma API and
    the MCP tool input and output contracts built on top of them.

Design:
    The models in this module separate:
    1. tool inputs,
    2. normalized domain objects, and
    3. MCP-friendly output envelopes.

    This keeps the service layer stable and avoids leaking arbitrary upstream
    JSON across the package.

Attributes:
    SearchPublicArgs:
        Input model for free-text public search.
    ListMarketsArgs:
        Input model for market listing and filtering.
    ListEventsArgs:
        Input model for event listing and filtering.
    Market:
        Normalized Polymarket market model.
    Event:
        Normalized Polymarket event model.
    SearchMarketsOutput:
        MCP output envelope for market search.
    ListEventsOutput:
        MCP output envelope for event listing.
    MarketDetailOutput:
        MCP output envelope for a single market.
    EventDetailOutput:
        MCP output envelope for a single event.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field, computed_field


class SearchPublicArgs(BaseModel):
    """Arguments for Gamma public search.

    Args:
        query: Free-text query used to search markets, events, and related
            public entities.
        limit: Maximum number of results to request.

    Returns:
        SearchPublicArgs: Validated search arguments.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> args = SearchPublicArgs(query="fed decision", limit=5)
        >>> args.limit
        5
    """

    model_config = ConfigDict(extra="forbid")

    query: str = Field(min_length=1)
    limit: int = Field(default=10, ge=1, le=100)


class ListMarketsArgs(BaseModel):
    """Arguments for listing or filtering Gamma markets.

    Args:
        limit: Maximum number of markets to return.
        active: Whether to prefer active markets.
        closed: Whether to include closed markets.
        slug: Optional exact market slug filter.
        tag_id: Optional tag identifier filter.
        series_slug: Optional series slug filter.

    Returns:
        ListMarketsArgs: Validated market filter arguments.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> args = ListMarketsArgs(limit=10, active=True, closed=False)
        >>> args.active
        True
    """

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=10, ge=1, le=100)
    active: bool = True
    closed: bool = False
    slug: str | None = None
    tag_id: int | None = None
    series_slug: str | None = None


class ListEventsArgs(BaseModel):
    """Arguments for listing or filtering Gamma events.

    Args:
        limit: Maximum number of events to return.
        active: Whether to prefer active events.
        closed: Whether to include closed events.
        slug: Optional exact event slug filter.

    Returns:
        ListEventsArgs: Validated event filter arguments.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> args = ListEventsArgs(limit=10, active=True, closed=False)
        >>> args.closed
        False
    """

    model_config = ConfigDict(extra="forbid")

    limit: int = Field(default=10, ge=1, le=100)
    active: bool = True
    closed: bool = False
    slug: str | None = None


class Market(BaseModel):
    """Normalized Polymarket market model.

    Args:
        id: Optional upstream market identifier.
        slug: Canonical market slug from Polymarket URLs.
        question: Human-readable market question text.
        active: Whether the market is currently active.
        closed: Whether the market is closed.
        liquidity: Reported liquidity value when present.
        volume: Reported volume value when present.
        event_slug: Parent event slug when known.
        clob_token_ids: Associated CLOB token identifiers, if available.

    Returns:
        Market: Normalized market model.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> market = Market(slug="fed-decision", question="Will the Fed cut?")
        >>> market.slug
        'fed-decision'
    """

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    slug: str
    question: str | None = None
    active: bool | None = None
    closed: bool | None = None
    liquidity: float | None = None
    volume: float | None = None
    event_slug: str | None = None
    clob_token_ids: list[str] = Field(default_factory=list)


class Event(BaseModel):
    """Normalized Polymarket event model.

    Args:
        id: Optional upstream event identifier.
        slug: Canonical event slug from Polymarket URLs.
        title: Human-readable event title.
        active: Whether the event is currently active.
        closed: Whether the event is closed.
        markets: Nested normalized markets associated with the event.

    Returns:
        Event: Normalized event model.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> event = Event(slug="fed-event", title="Fed Event")
        >>> event.title
        'Fed Event'
    """

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    slug: str
    title: str | None = None
    active: bool | None = None
    closed: bool | None = None
    markets: list[Market] = Field(default_factory=list)


class SearchMarketsOutput(BaseModel):
    """Tool output for public Gamma search.

    Args:
        query: Original search query.
        markets: Matching normalized markets.

    Returns:
        SearchMarketsOutput: Search result envelope.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> output = SearchMarketsOutput(query="fed", markets=[])
        >>> output.count
        0
    """

    model_config = ConfigDict(extra="forbid")

    query: str
    markets: list[Market] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of matching markets.

        Returns:
            int: Number of returned markets.

        Raises:
            None.

        Examples:
            >>> SearchMarketsOutput(query="x", markets=[]).count
            0
        """
        return len(self.markets)


class ListEventsOutput(BaseModel):
    """Tool output for Gamma event listing.

    Args:
        events: Matching normalized events.

    Returns:
        ListEventsOutput: Event listing envelope.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> output = ListEventsOutput(events=[])
        >>> output.count
        0
    """

    model_config = ConfigDict(extra="forbid")

    events: list[Event] = Field(default_factory=list)

    @computed_field
    @property
    def count(self) -> int:
        """Return the number of returned events.

        Returns:
            int: Number of returned events.

        Raises:
            None.

        Examples:
            >>> ListEventsOutput(events=[]).count
            0
        """
        return len(self.events)


class MarketDetailOutput(BaseModel):
    """Tool output for a single market lookup.

    Args:
        market: The normalized market payload.

    Returns:
        MarketDetailOutput: Single-market envelope.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> output = MarketDetailOutput(market=Market(slug="x"))
        >>> output.market.slug
        'x'
    """

    model_config = ConfigDict(extra="forbid")

    market: Market


class EventDetailOutput(BaseModel):
    """Tool output for a single event lookup.

    Args:
        event: The normalized event payload.

    Returns:
        EventDetailOutput: Single-event envelope.

    Raises:
        ValueError: If validation fails.

    Examples:
        >>> output = EventDetailOutput(event=Event(slug="x"))
        >>> output.event.slug
        'x'
    """

    model_config = ConfigDict(extra="forbid")

    event: Event
