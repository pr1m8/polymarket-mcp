# Repository Guidelines

## Project Structure & Module Organization
Core package code lives in `src/polymarket_mcp/`. Keep transport logic in `http.py`, shared settings/errors in `settings.py` and `errors.py`, typed schemas in `models/`, upstream API adapters in `services/`, and MCP-facing tool/resource servers in `servers/`. The composed entrypoint is `src/polymarket_mcp/server.py`. Tests live in `tests/`, with `tests/helpers/` reserved for local test doubles. Sphinx docs live in `docs/`.

## Build, Test, and Development Commands
This repo uses PDM.

- `pdm install -d` installs runtime and dev dependencies.
- `pdm run test` runs the full pytest suite.
- `pdm run test-mcp` runs MCP end-to-end tests against a real FastMCP client session.
- `pdm run test-cov` runs tests with coverage for `src/polymarket_mcp`.
- `pdm run check` runs tests plus `mcp-inspect`.
- `pdm run all` runs tests, builds docs, and inspects the composed server.
- `pdm run mcp-run` starts the composed MCP server.
- `pdm run mcp-inspect` prints the current tool/template surface.
- `pdm run mcp-dev` runs the FastMCP development flow for the composed server.

## Coding Style & Naming Conventions
Target Python 3.13, use explicit type hints, and keep modules narrowly scoped. Follow the existing pattern: Pydantic models for normalized output, service classes for upstream normalization, and thin FastMCP wrappers in `servers/`. Use `snake_case` for functions and modules, `PascalCase` for models/settings classes, and concise docstrings that explain tool-selection intent for MCP consumers.

## Testing Guidelines
Pytest is the test runner. Name files `test_*.py` and keep tests close to the behavior they validate: normalization in service tests, mounted surface and dispatch in MCP tests. Mock upstream HTTP or service methods; do not hit live Polymarket endpoints in CI-style tests. Before opening a PR, run `pdm run test` and `pdm run test-mcp`.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commit style with scopes, e.g. `feat(tests): Added Tests` and `chore(repo): Added gitignore`. Keep using `<type>(<scope>): <summary>`. PRs should describe the behavior change, list validation commands you ran, and call out any MCP surface changes such as added/renamed tools, resources, or templates. Update docs when user-facing commands or server capabilities change.
