# polymarket-mcp

Typed FastMCP server for Polymarket:

- Gamma discovery
- Data API wallet and trade reads
- Public CLOB order books, quotes, midpoint, spread, and price history

This version is intentionally **read-only**. It does **not** include authenticated trading tools yet.

---

## What this package is for

Use this package when you want an LLM, MCP client, or agent runtime to:

- discover Polymarket markets and events by topic
- inspect a wallet's current or historical exposure
- read public order books and market quotes
- analyze price history for known token IDs

This package is a good fit for:

- FastMCP clients
- Claude / Cursor MCP setups
- LangChain MCP adapters
- LangGraph workflows
- internal research or analytics tools

---

## Included domains

The parent server mounts three child MCP servers:

- `gamma`: market and event discovery
- `data`: wallet positions, activity, and trades
- `clob`: public order books, quotes, and history

---

## Package layout

```text
.
├── README.md
├── docs/
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
```

---

## Install

Using PDM:

```bash
pdm install -d
```

If you also want docs dependencies:

```bash
pdm install -dG docs
```

---

## Quick start

Inspect the composed MCP server:

```bash
pdm run mcp-inspect
```

Run the composed MCP server:

```bash
pdm run mcp-run
```

Run the package directly:

```bash
pdm run python -m polymarket_mcp.server
```

---

## PDM scripts

### Test and docs

```bash
pdm run test
pdm run test-cov
pdm run docs
pdm run docs-serve
pdm run docs-clean
```

### Main MCP commands

```bash
pdm run mcp-inspect
pdm run mcp-inspect-json
pdm run mcp-inspect-mcp
pdm run mcp-run
pdm run mcp-dev
```

### Child server commands

```bash
pdm run mcp-gamma-inspect
pdm run mcp-data-inspect
pdm run mcp-clob-inspect

pdm run mcp-gamma-run
pdm run mcp-data-run
pdm run mcp-clob-run
```

### Combined checks

```bash
pdm run check
pdm run all
```

---

## What the main scripts do

### `pdm run mcp-inspect`

Inspects the composed parent FastMCP server and prints a human-readable summary of:

- tools
- resources
- prompts
- namespaces

This is the best first sanity check.

### `pdm run mcp-run`

Runs the composed Polymarket MCP server.

This is the main entrypoint for local development and client integration.

### `pdm run mcp-dev`

Runs the FastMCP development flow for the composed server, if supported by your installed FastMCP version.

### `pdm run mcp-inspect-json`

Emits a FastMCP-formatted JSON description of the server.

### `pdm run mcp-inspect-mcp`

Emits MCP-format JSON to `.artifacts/polymarket-mcp.json`.

This is useful for tooling, manifests, and debugging MCP surfaces.

---

## Child servers

You can also inspect or run domain servers individually.

### Gamma

Use Gamma when you need:

- market discovery
- event discovery
- tag, series, sports, or team metadata
- exact market lookup by slug
- exact event lookup by slug

Examples:

```bash
pdm run mcp-gamma-inspect
pdm run mcp-gamma-run
```

### Data

Use Data when you need:

- wallet positions
- closed positions
- wallet activity
- trade history

Examples:

```bash
pdm run mcp-data-inspect
pdm run mcp-data-run
```

### CLOB public

Use CLOB public when you need:

- order books
- price quotes
- midpoint
- spread
- price history

Examples:

```bash
pdm run mcp-clob-inspect
pdm run mcp-clob-run
```

---

## Tool design philosophy

Tool docstrings are intentionally written for **LLM tool selection**, not only for human developers.

Each MCP tool should explain:

- when to use it
- when not to use it
- what kind of identifier it expects
- what the output is useful for
- what likely follow-up tools come next

This improves agent behavior substantially compared with minimal API-style docstrings.

---

## Resources

Canonical resources are exposed for stable objects such as:

- market by slug
- event by slug
- wallet positions
- wallet activity
- order book by token ID
- price by token ID

If enabled in settings, resources are also exposed through generated tools via `ResourcesAsTools`, which is especially useful for tool-centric clients.

---

## Suggested agent flow

A good general-purpose Polymarket agent flow is:

1. Use Gamma tools to discover relevant markets or events.
2. Use exact Gamma lookup tools once a slug is known.
3. Use CLOB public tools for live order books or quotes.
4. Use Data tools for wallet-level analysis.

Example reasoning flow:

```text
topic query
→ gamma_search_public
→ gamma_get_market_by_slug
→ clob_get_book or clob_get_price
→ final synthesis
```

Wallet analysis flow:

```text
wallet address
→ data_get_positions
→ data_get_activity
→ optional gamma or clob follow-up on referenced markets
→ final synthesis
```

---

## Testing

Run the full test suite:

```bash
pdm run test
```

Run with coverage:

```bash
pdm run test-cov
```

---

## Documentation

Build docs locally:

```bash
pdm run docs
```

Serve built docs locally:

```bash
pdm run docs-serve
```

This project also includes:

- GitHub Actions CI
- release workflow scaffolding
- Read the Docs configuration
- Sphinx docs scaffolding

---

## Release workflow

The project includes a release workflow intended for tag-based publishing.

Before using it, wire up:

- PyPI Trusted Publishing
- your repository settings
- your Read the Docs project

---

## Environment and settings

Settings are environment-backed through `pydantic-settings`.

The package currently uses public Polymarket endpoints by default, including:

- Gamma base URL
- Data API base URL
- CLOB base URL

You can extend settings later for:

- alternate environments
- custom timeouts
- tracing
- debug logging
- auth or trading support

---

## Not included yet

This first version intentionally does **not** include:

- authenticated trading
- order placement or cancellation
- websocket streaming
- remote proxy gateway composition
- persistence or caching
- advanced observability

Those are good next steps once the read-only MCP surface is stable.

---

## Next recommended improvements

Good next additions include:

- Ruff
- pre-commit
- structured logging
- richer error modeling
- authenticated trading server
- websocket ingestion layer
- FastAPI-hosted gateway wrapper

---

## License

Add your preferred license file before publishing.
