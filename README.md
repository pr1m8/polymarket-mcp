# polymarket-mcp

[![CI](https://github.com/pr1m8/polymarket-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/pr1m8/polymarket-mcp/actions/workflows/ci.yml)
[![Release](https://github.com/pr1m8/polymarket-mcp/actions/workflows/release.yml/badge.svg)](https://github.com/pr1m8/polymarket-mcp/actions/workflows/release.yml)
[![PyPI](https://img.shields.io/pypi/v/polymarket-mcp-server.svg)](https://pypi.org/project/polymarket-mcp-server/)
[![Python](https://img.shields.io/pypi/pyversions/polymarket-mcp-server.svg)](https://pypi.org/project/polymarket-mcp-server/)
[![Docs](https://readthedocs.org/projects/polymarket-mcp/badge/?version=latest)](https://polymarket-mcp.readthedocs.io/en/latest/)

Typed FastMCP server for Polymarket discovery, wallet analytics, and public CLOB market data.

This package is intentionally read-only in `0.1.x`. It helps agents and MCP clients inspect markets, wallets, books, quotes, and history without exposing authenticated trading actions.

PyPI distribution: `polymarket-mcp-server`  
Python package: `polymarket_mcp`  
CLI command: `polymarket-mcp`

## Why use it

- Stable typed models over inconsistent upstream JSON.
- A single composed MCP server with clear `gamma`, `data`, and `clob` namespaces.
- Real MCP transport coverage in pytest, including subprocess stdio tests.
- Local PDM workflow plus trusted publishing to PyPI and Read the Docs support.

## Surfaces

| Surface | Purpose | Examples |
| --- | --- | --- |
| `gamma` | market and event discovery | topic search, event lookup, metadata |
| `data` | wallet reads | positions, activity, trades |
| `clob` | live public market state | books, quotes, midpoint, spread, history |

```mermaid
flowchart LR
    Client["MCP client / agent"] --> Server["polymarket_mcp.server"]
    Server --> Gamma["gamma server"]
    Server --> Data["data server"]
    Server --> Clob["clob server"]
    Gamma --> GAPI["Gamma API"]
    Data --> DAPI["Data API"]
    Clob --> CLOB["Public CLOB API"]
```

## Install and run

```bash
pip install polymarket-mcp-server
polymarket-mcp
```

Or run it ephemerally with `uvx`:

```bash
uvx --from polymarket-mcp-server polymarket-mcp
```

For local development with PDM:

```bash
pdm install -G dev
pdm install -G docs
```

## MCP client config

Example stdio client entry using `uvx`:

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

## Quick start

```bash
pdm run mcp-inspect      # inspect the composed server surface
pdm run mcp-run          # run the stdio MCP server
pdm run test             # run the full pytest suite
pdm run test-mcp         # run MCP client/server end-to-end tests
pdm run all              # tests + docs + MCP inspect
```

Run the package directly:

```bash
pdm run python -m polymarket_mcp.server
```

## Useful commands

```bash
pdm run mcp-gamma-inspect
pdm run mcp-data-inspect
pdm run mcp-clob-inspect
pdm run docs
```

## Project layout

```text
src/polymarket_mcp/
  models/     typed domain and tool I/O models
  services/   upstream normalization layers
  servers/    FastMCP tool/resource surfaces
  server.py   composed parent MCP server
tests/        unit and MCP end-to-end coverage
docs/         Sphinx documentation
```

## Documentation

- Docs site: <https://polymarket-mcp.readthedocs.io/en/latest/>
- Docs source: `docs/` (Sphinx with native reStructuredText pages)
- Local build: `pdm run docs`
- Local preview: `pdm run docs-serve`

## Development notes

- Tool docstrings are written for LLM tool selection, not just human API reference.
- `tests/test_mcp_e2e.py` now covers both in-process and subprocess MCP usage.
- Releases publish from Git tags through GitHub Actions trusted publishing.
- `pdm run mcp-dev` uses the FastMCP inspector flow; if the inspector package is not cached locally, the first run may need external package access.
