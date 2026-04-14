# Development

## Local workflow

```bash
pdm install -G dev
pdm install -G docs
pdm run test
pdm run docs
```

The project targets Python `3.13` and is managed entirely through PDM.

## Testing strategy

- Service tests mock upstream HTTP payloads and validate normalization.
- MCP tests cover real FastMCP client usage.
- Subprocess MCP tests launch the server over stdio to validate the actual transport path.

## Documentation workflow

- Sphinx configuration lives in `docs/conf.py`.
- Read the Docs build config lives in `.readthedocs.yaml`.
- `pdm run docs-serve` previews the generated HTML locally.

## Release workflow

GitHub Actions builds distributions on tag pushes and publishes to PyPI using the `PYPI_API_TOKEN` repository secret. A matching GitHub release is created from the same artifacts.
