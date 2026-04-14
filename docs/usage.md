# Getting started

## Install

Install the published package:

```bash
pip install polymarket-mcp-server
```

Or run it without creating a persistent environment:

```bash
uvx --from polymarket-mcp-server polymarket-mcp
```

For local development, install the PDM groups:

```bash
pdm install -G dev
pdm install -G docs
```

## Configure an MCP client

Example stdio configuration using `uvx`:

```json
{
  "mcpServers": {
    "polymarket": {
      "command": "uvx",
      "args": ["--from", "polymarket-mcp-server", "polymarket-mcp"]
    }
  }
}
```

## Inspect the server

Use the composed MCP inspector summary as the first sanity check:

```bash
pdm run mcp-inspect
```

You should see a `polymarket` server exposing the namespaced Gamma, Data, and CLOB tools plus generated resource helpers.

## Run the server

Run the stdio server for local MCP clients:

```bash
pdm run mcp-run
```

Or run the package entrypoint directly:

```bash
pdm run python -m polymarket_mcp.server
```

## Namespaces

- `gamma` covers market and event discovery.
- `data` covers wallet positions, activity, and trades.
- `clob` covers public quotes, books, spreads, and historical pricing.

## Validate the project

```bash
pdm run test
pdm run test-mcp
pdm run check
pdm run all
```

- `test` runs the full pytest suite.
- `test-mcp` focuses on MCP client/server flows.
- `check` runs tests and inspects the server.
- `all` runs tests, docs, and MCP inspection.

## Domain-specific servers

You can inspect or run the child servers independently:

```bash
pdm run mcp-gamma-inspect
pdm run mcp-data-inspect
pdm run mcp-clob-inspect

pdm run mcp-gamma-run
pdm run mcp-data-run
pdm run mcp-clob-run
```
