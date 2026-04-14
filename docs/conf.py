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

from polymarket_mcp import __version__

project = "polymarket-mcp"
author = "OpenAI"
release = __version__
html_title = "polymarket-mcp documentation"

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx_autodoc_typehints",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "source_repository": "https://github.com/pr1m8/polymarket-mcp/",
    "source_branch": "main",
    "source_directory": "docs/",
    "navigation_with_keys": True,
}

myst_heading_anchors = 3
myst_enable_extensions = ["colon_fence", "deflist"]
napoleon_google_docstring = True
napoleon_numpy_docstring = False
autodoc_member_order = "bysource"
autodoc_typehints = "description"
suppress_warnings = ["sphinx_autodoc_typehints.forward_reference"]
