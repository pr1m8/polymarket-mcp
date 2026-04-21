Development
===========

Local workflow
--------------

.. code-block:: bash

   pdm install -G dev
   pdm install -G docs
   pdm run mcp-inspect
   pdm run test
   pdm run docs

The project targets Python ``3.13`` and is managed entirely through PDM.

Testing strategy
----------------

* Service tests mock upstream HTTP payloads and validate normalization.
* MCP tests cover real FastMCP client usage.
* Subprocess MCP tests launch the server over stdio to validate the actual transport path.

Documentation workflow
----------------------

* Sphinx configuration lives in ``docs/conf.py``.
* Read the Docs build config lives in ``.readthedocs.yaml``.
* ``pdm run docs-serve`` previews the generated HTML locally.
* ``docs/index.rst`` is the landing page and should stay short and navigable.

Release workflow
----------------

* GitHub Actions publishes on ``v*`` tags from ``.github/workflows/release.yml``.
* PyPI publishing uses GitHub trusted publishing with the ``pypi`` environment.
* The release job refreshes the lockfile, runs tests, builds distributions,
  uploads to PyPI, and creates a GitHub release from the same artifacts.
