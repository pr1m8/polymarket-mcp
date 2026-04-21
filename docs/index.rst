polymarket-mcp documentation
============================

``polymarket-mcp`` exposes a typed FastMCP surface over Polymarket discovery,
wallet reads, and public CLOB market data.

At a glance
-----------

* Normalize volatile upstream JSON into stable typed models.
* Present Polymarket as clear MCP tools and resources.
* Keep discovery, wallet, and order book concerns separated but composable.
* Make tool descriptions useful for LLM routing, not just humans.

Included surfaces
-----------------

.. list-table::
   :header-rows: 1

   * - Namespace
     - Focus
     - Typical follow-up
   * - ``gamma``
     - find markets and events
     - inspect one market or event
   * - ``data``
     - inspect wallet state and history
     - summarize positions or trades
   * - ``clob``
     - read live books, quotes, and history
     - compare pricing and liquidity

Package identities
------------------

* Distribution: ``polymarket-mcp-server``
* Import package: ``polymarket_mcp``
* CLI entrypoint: ``polymarket-mcp``

.. toctree::
   :maxdepth: 2
   :caption: Guides

   usage
   architecture
   development
   release
   api
