# polymarket-mcp

Typed FastMCP server for Polymarket:

- Gamma discovery
- Data API wallet and trade reads
- Public CLOB order books, quotes, midpoint, spread, and price history

This first version is **read-only**. It does **not** include authenticated
trading tools yet.

## What this server is for

Use this MCP package when you want an LLM or agent to:

- discover Polymarket markets and events by topic
- inspect a wallet's current and historical exposure
- read public order books, quotes, midpoint, spread, and price history

## Architecture

The package uses a layered structure:

1. `models/` defines typed domain models and MCP input/output contracts.
2. `services/` normalizes raw upstream payloads into stable Python models.
3. `servers/` exposes those services through FastMCP tools and resources.
4. `server.py` composes the child servers into one parent MCP entrypoint.

## Namespaces

The parent server mounts three child MCP servers:

- `gamma`: discovery and catalog-style lookups
- `data`: wallet positions, activity, and trade history
- `clob`: public order book and pricing reads

## Package layout

```text
polymarket_mcp/
├── README.md
├── pyproject.toml
├── src/
│   └── polymarket_mcp/
│       ├── __init__.py
│       ├── errors.py
│       ├── http.py
│       ├── server.py
│       ├── settings.py
│       ├── models/
│       ├── services/
│       └── servers/
└── tests/
    ├── conftest.py
    ├── helpers/
    └── test_*.py
```

## Install with PDM

```bash
pdm install -d
```

## Run tests

```bash
pdm run pytest
```

## Run the MCP server

```bash
pdm run polymarket-mcp
```

or:

```bash
pdm run python -m polymarket_mcp.server
```

## Configuration

Settings are environment-backed with the `POLYMARKET_MCP_` prefix.

Examples:

```bash
export POLYMARKET_MCP_REQUEST_TIMEOUT_SECONDS=10
export POLYMARKET_MCP_ENABLE_RESOURCES_AS_TOOLS=true
```

Supported settings include:

- `POLYMARKET_MCP_GAMMA_BASE_URL`
- `POLYMARKET_MCP_DATA_BASE_URL`
- `POLYMARKET_MCP_CLOB_BASE_URL`
- `POLYMARKET_MCP_REQUEST_TIMEOUT_SECONDS`
- `POLYMARKET_MCP_ENABLE_RESOURCES_AS_TOOLS`
- `POLYMARKET_MCP_USER_AGENT`

## Tool docstring philosophy

Tool docstrings are intentionally written for MCP tool selection.

Each tool should explain:

- when to use it
- when not to use it
- what kind of identifier it expects
- what the result is useful for
- which follow-up tools are commonly helpful

This improves agent behavior compared with plain developer-only docstrings.

## Resources

Canonical resources are provided for stable objects such as:

- market by slug
- event by slug
- wallet positions
- wallet activity
- book by token
- price by token

If enabled in settings, resources are also exposed as generated tools through
`ResourcesAsTools`, which is useful for tool-centric agent clients.

## Suggested first agent flow

1. Use `gamma_search_public` or `gamma_list_events` to find relevant markets.
2. Use `gamma_get_market_by_slug` for exact market detail.
3. Use `clob_get_book` or `clob_get_price` for live market state.
4. Use `data_get_positions` or `data_get_activity` for wallet analysis.

## Not included yet

This first version intentionally does not include:

- authenticated trading
- order placement or cancellation
- websocket streaming
- remote proxy gateway behavior

Those can be added later as a separate trading server or gateway layer.


## CI, releases, and docs

This project now includes:

- GitHub Actions CI in `.github/workflows/ci.yml`
- tag-based release publishing in `.github/workflows/release.yml`
- Read the Docs configuration in `.readthedocs.yaml`
- Sphinx documentation under `docs/`

### Suggested release flow

1. Push changes to a branch and open a pull request.
2. Let CI run tests and docs builds.
3. Merge to `main`.
4. Tag a version like `v0.1.0`.
5. Push the tag to trigger the publish workflow.

### Trusted publishing note

The release workflow is set up to use PyPI trusted publishing. You should wire
this repository into PyPI as a trusted publisher before relying on the publish
step.
