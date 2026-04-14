"""FastMCP Data API server for Polymarket wallet and trade reads.

Purpose:
    Expose Polymarket wallet, activity, and trade reads as MCP tools and
    resources.

Design:
    This module is read-only. Tool docstrings are written to help an LLM choose
    the correct wallet or trade tool and understand the expected identifiers and
    likely next steps.
"""

from __future__ import annotations

import json

from fastmcp import FastMCP

from polymarket_mcp.models.data import (
    TradesArgs,
    TradesOutput,
    WalletActivityOutput,
    WalletArgs,
    WalletPositionsOutput,
)
from polymarket_mcp.services.data import DataApiService
from polymarket_mcp.settings import load_settings

settings = load_settings()
service = DataApiService(settings)

mcp = FastMCP(
    name="polymarket-data",
    instructions=(
        "Use this server for wallet exposure, historical activity, and trade "
        "reads. Do not use it for market discovery or live order book reads."
    ),
)


@mcp.tool
async def get_positions(args: WalletArgs) -> WalletPositionsOutput:
    """Fetch current positions for one wallet.

    Use this tool when the user wants to know what a wallet currently holds,
    which markets it is exposed to, or its current directional footprint.

    Prefer this tool over ``get_activity`` when the question is about present
    state rather than historical actions. Do not use this tool if you still
    need to discover which market exists; that belongs to Gamma tools.

    The input should be a wallet address, typically in ``0x...`` format. A
    common next step is ``get_activity`` for recent changes or CLOB/Gamma tools
    for deeper inspection of the markets referenced by the positions.

    Args:
        args: Wallet query arguments.

    Returns:
        WalletPositionsOutput: Current normalized positions for the wallet.

    Raises:
        httpx.HTTPError: If the upstream Data API request fails.

    Examples:
        .. code-block:: python

            result = await get_positions(WalletArgs(user="0xabc"))
    """
    positions = await service.get_positions(args)
    return WalletPositionsOutput(user=args.user, positions=positions)


@mcp.tool
async def get_closed_positions(args: WalletArgs) -> WalletPositionsOutput:
    """Fetch closed positions for one wallet.

    Use this tool when the user wants completed or no-longer-open positions,
    such as reviewing realized exposure or prior bets.

    Prefer this tool over ``get_positions`` when historical closed exposure is
    specifically requested. A common next step is ``get_activity`` or
    ``get_trades`` to explain how the wallet entered and exited those markets.

    The input should be a wallet address, typically in ``0x...`` format.

    Args:
        args: Wallet query arguments.

    Returns:
        WalletPositionsOutput: Closed normalized positions for the wallet.

    Raises:
        httpx.HTTPError: If the upstream Data API request fails.

    Examples:
        .. code-block:: python

            result = await get_closed_positions(WalletArgs(user="0xabc"))
    """
    positions = await service.get_closed_positions(args)
    return WalletPositionsOutput(user=args.user, positions=positions)


@mcp.tool
async def get_activity(args: WalletArgs) -> WalletActivityOutput:
    """Fetch recent activity for one wallet.

    Use this tool when the user wants to know what a wallet has been doing
    recently, including buying, selling, or other account-level actions.

    Prefer this tool over ``get_positions`` when the question is about recent
    behavior rather than current holdings. Prefer ``get_trades`` when the user
    specifically wants trade rows rather than broader account activity.

    The input should be a wallet address, typically in ``0x...`` format. A
    common next step is to inspect affected markets through Gamma or CLOB tools.

    Args:
        args: Wallet query arguments.

    Returns:
        WalletActivityOutput: Normalized activity rows for the wallet.

    Raises:
        httpx.HTTPError: If the upstream Data API request fails.

    Examples:
        .. code-block:: python

            result = await get_activity(WalletArgs(user="0xabc"))
    """
    activity = await service.get_activity(args)
    return WalletActivityOutput(user=args.user, activity=activity)


@mcp.tool
async def get_trades(args: TradesArgs) -> TradesOutput:
    """Fetch trade rows for a wallet or market filter.

    Use this tool when the user wants trade-level records rather than current
    holdings or general wallet activity. This is useful for detailed flow
    analysis and execution history.

    Prefer this tool over ``get_activity`` when exact trade rows matter. Prefer
    Gamma tools when you still need to discover the right market first.

    The input can include a wallet address, a market filter, or both, depending
    on what the user already knows. A common next step is to summarize the
    trade flow or compare it with current positions.

    Args:
        args: Trade query arguments.

    Returns:
        TradesOutput: Normalized trade rows.

    Raises:
        httpx.HTTPError: If the upstream Data API request fails.

    Examples:
        .. code-block:: python

            result = await get_trades(TradesArgs(user="0xabc", limit=20))
    """
    trades = await service.get_trades(args)
    return TradesOutput(trades=trades)


@mcp.resource("polymarket://data/user/{address}/positions")
async def positions_resource(address: str) -> str:
    """Read canonical current positions for a wallet.

    Args:
        address: Wallet address, usually in ``0x...`` format.

    Returns:
        str: JSON-encoded current positions payload.

    Raises:
        httpx.HTTPError: If the upstream Data API request fails.

    Examples:
        .. code-block:: python

            text = await positions_resource("0xabc")
    """
    payload = WalletPositionsOutput(
        user=address,
        positions=await service.get_positions(WalletArgs(user=address)),
    )
    return json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)


@mcp.resource("polymarket://data/user/{address}/activity")
async def activity_resource(address: str) -> str:
    """Read canonical recent activity for a wallet.

    Args:
        address: Wallet address, usually in ``0x...`` format.

    Returns:
        str: JSON-encoded wallet activity payload.

    Raises:
        httpx.HTTPError: If the upstream Data API request fails.

    Examples:
        .. code-block:: python

            text = await activity_resource("0xabc")
    """
    payload = WalletActivityOutput(
        user=address,
        activity=await service.get_activity(WalletArgs(user=address)),
    )
    return json.dumps(payload.model_dump(mode="json"), indent=2, sort_keys=True)
