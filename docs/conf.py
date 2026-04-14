"""Sphinx configuration for polymarket-mcp.

Purpose:
    Configure Sphinx for local and Read the Docs builds.

Design:
    The docs emphasize API discoverability for the typed models, service
    adapters, and FastMCP server modules.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
sys.path.insert(0, os.fspath(SRC_DIR))

project = "polymarket-mcp"
author = "OpenAI"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
autodoc_member_order = "bysource"
autodoc_typehints = "description"

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pydantic": ("https://docs.pydantic.dev/latest/", None),
}
