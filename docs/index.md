# polymarket-mcp

`polymarket-mcp` is a typed FastMCP package for Polymarket discovery, wallet
analytics, and public CLOB market data.

## Included surfaces

- Gamma discovery
- Data API wallet positions, activity, and trades
- Public CLOB order books, quotes, midpoint, spread, and history

## Project goals

- typed models instead of raw JSON everywhere
- MCP tool docstrings that guide LLM tool selection
- clean separation between models, services, and MCP server modules
- a parent FastMCP server composed from focused child servers

## Contents

```{toctree}
:maxdepth: 2

usage
api
```
