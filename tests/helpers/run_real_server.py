"""Run the real composed Polymarket MCP server over stdio for subprocess tests."""

from polymarket_mcp.server import mcp


if __name__ == "__main__":
    mcp.run()
