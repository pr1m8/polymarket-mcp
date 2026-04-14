"""End-to-end MCP tests using a real FastMCP client session."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest
from fastmcp import Client
from fastmcp.client.transports.stdio import PythonStdioTransport

from polymarket_mcp.models.gamma import Event, Market
from polymarket_mcp.server import create_server
from polymarket_mcp.servers import gamma_server
from polymarket_mcp.settings import AppSettings

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
HELPERS = ROOT / "tests" / "helpers"


def _build_subprocess_env() -> dict[str, str]:
    """Create a subprocess environment that can import the local package."""
    env = os.environ.copy()
    pythonpath = env.get("PYTHONPATH")
    env["PYTHONPATH"] = (
        f"{SRC}{os.pathsep}{pythonpath}" if pythonpath else str(SRC)
    )
    return env


def _make_stdio_client(script_path: Path, log_path: Path) -> Client:
    """Create a real stdio MCP client backed by a Python subprocess."""
    transport = PythonStdioTransport(
        script_path=script_path,
        env=_build_subprocess_env(),
        cwd=str(ROOT),
        keep_alive=False,
        log_file=log_path,
    )
    return Client(transport)


@pytest.mark.asyncio
async def test_client_lists_expected_mcp_surface() -> None:
    """The composed server should expose namespaced tools and templates over MCP."""
    server = create_server(AppSettings(enable_resources_as_tools=True))

    async with Client(server) as client:
        tools = await client.list_tools()
        templates = await client.list_resource_templates()

    tool_names = {tool.name for tool in tools}
    template_uris = {
        template.uriTemplate
        for template in templates
    }

    assert len(tools) == 22
    assert {
        "gamma_search_public",
        "data_get_positions",
        "clob_get_book",
        "list_resources",
        "read_resource",
    } <= tool_names
    assert template_uris == {
        "polymarket://gamma/gamma/market/{slug}",
        "polymarket://gamma/gamma/event/{slug}",
        "polymarket://data/data/user/{address}/positions",
        "polymarket://data/data/user/{address}/activity",
        "polymarket://clob/clob/book/{token_id}",
        "polymarket://clob/clob/price/{token_id}",
    }


@pytest.mark.asyncio
async def test_client_hides_resource_tools_when_transform_is_disabled() -> None:
    """Disabling resource transforms should hide generic resource tools to clients."""
    server = create_server(AppSettings(enable_resources_as_tools=False))

    async with Client(server) as client:
        tool_names = {tool.name for tool in await client.list_tools()}

    assert len(tool_names) == 20
    assert "list_resources" not in tool_names
    assert "read_resource" not in tool_names


@pytest.mark.asyncio
async def test_client_dispatches_namespaced_tool_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Client tool calls should flow through the mounted FastMCP server surface."""

    async def fake_search(args) -> list[Market]:
        return [
            Market(
                slug="fed-cut",
                question="Will the Fed cut?",
                clob_token_ids=["101", "202"],
            )
        ]

    monkeypatch.setattr(gamma_server.service, "search_public", fake_search)
    server = create_server(AppSettings(enable_resources_as_tools=True))

    async with Client(server) as client:
        result = await client.call_tool(
            "gamma_search_public",
            {"args": {"query": "fed", "limit": 1}},
        )

    assert result.structured_content["count"] == 1
    assert result.structured_content["markets"][0]["slug"] == "fed-cut"
    assert result.structured_content["markets"][0]["clob_token_ids"] == [
        "101",
        "202",
    ]


@pytest.mark.asyncio
async def test_client_reads_resources_over_mcp_and_generated_resource_tool(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Clients should be able to read resources both natively and via toolification."""

    async def fake_event_lookup(slug: str) -> Event:
        return Event(slug=slug, title="Fed Event")

    monkeypatch.setattr(gamma_server.service, "get_event_by_slug", fake_event_lookup)
    server = create_server(AppSettings(enable_resources_as_tools=True))
    resource_uri = "polymarket://gamma/gamma/event/fed-event"

    async with Client(server) as client:
        contents = await client.read_resource(resource_uri)
        tool_result = await client.call_tool(
            "read_resource",
            {"uri": resource_uri},
        )

    resource_payload = json.loads(contents[0].text)
    tool_payload = json.loads(tool_result.structured_content["result"])

    assert resource_payload["event"]["slug"] == "fed-event"
    assert resource_payload["event"]["title"] == "Fed Event"
    assert tool_payload["event"]["slug"] == "fed-event"
    assert tool_payload["event"]["title"] == "Fed Event"


@pytest.mark.asyncio
async def test_subprocess_server_lists_expected_mcp_surface(tmp_path: Path) -> None:
    """The actual server process should expose the expected MCP surface."""
    client = _make_stdio_client(
        HELPERS / "run_real_server.py",
        tmp_path / "run-real-server.log",
    )

    async with client:
        tools = await client.list_tools()
        templates = await client.list_resource_templates()

    tool_names = {tool.name for tool in tools}
    template_uris = {template.uriTemplate for template in templates}

    assert len(tools) == 22
    assert {
        "gamma_search_public",
        "data_get_positions",
        "clob_get_book",
        "list_resources",
        "read_resource",
    } <= tool_names
    assert "polymarket://gamma/gamma/market/{slug}" in template_uris
    assert "polymarket://clob/clob/price/{token_id}" in template_uris


@pytest.mark.asyncio
async def test_subprocess_server_handles_tool_calls_and_resource_reads(
    tmp_path: Path,
) -> None:
    """A real subprocess server should handle tool calls and resource reads."""
    client = _make_stdio_client(
        HELPERS / "run_mocked_server.py",
        tmp_path / "run-mocked-server.log",
    )
    resource_uri = "polymarket://gamma/gamma/event/fed-event"

    async with client:
        tool_result = await client.call_tool(
            "gamma_search_public",
            {"args": {"query": "fed", "limit": 1}},
        )
        contents = await client.read_resource(resource_uri)
        resource_tool_result = await client.call_tool(
            "read_resource",
            {"uri": resource_uri},
        )

    search_payload = tool_result.structured_content
    resource_payload = json.loads(contents[0].text)
    resource_tool_payload = json.loads(resource_tool_result.structured_content["result"])

    assert search_payload["count"] == 1
    assert search_payload["markets"][0]["slug"] == "fed-cut"
    assert search_payload["markets"][0]["clob_token_ids"] == ["101", "202"]
    assert resource_payload["event"]["slug"] == "fed-event"
    assert resource_payload["event"]["title"] == "Fed Event"
    assert resource_tool_payload["event"]["slug"] == "fed-event"
    assert resource_tool_payload["event"]["title"] == "Fed Event"
