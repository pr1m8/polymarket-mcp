"""Run the composed MCP server with mocked services for subprocess E2E tests."""

from polymarket_mcp.models.gamma import Event, Market
from polymarket_mcp.server import create_server
from polymarket_mcp.servers import gamma_server
from polymarket_mcp.settings import AppSettings


async def fake_search(args) -> list[Market]:
    """Return stable search results for subprocess E2E tests."""
    return [
        Market(
            slug="fed-cut",
            question="Will the Fed cut?",
            clob_token_ids=["101", "202"],
        )
    ]


async def fake_event_lookup(slug: str) -> Event:
    """Return a stable event payload for subprocess E2E tests."""
    return Event(slug=slug, title="Fed Event")


gamma_server.service.search_public = fake_search
gamma_server.service.get_event_by_slug = fake_event_lookup

mcp = create_server(AppSettings(enable_resources_as_tools=True))


if __name__ == "__main__":
    mcp.run()
