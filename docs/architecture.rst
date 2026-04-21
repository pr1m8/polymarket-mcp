Architecture
============

The package is built in three layers.

1. Models
---------

``src/polymarket_mcp/models/`` contains typed Pydantic models for normalized
market, wallet, trade, quote, and history data. These models are the stable
boundary between upstream APIs and MCP consumers.

2. Services
-----------

``src/polymarket_mcp/services/`` wraps the Polymarket APIs and normalizes
inconsistent payloads into the typed models. This is where upstream JSON
differences should be absorbed.

3. MCP servers
--------------

``src/polymarket_mcp/servers/`` exposes the normalized services as FastMCP tools
and resources. Each child server stays focused on one domain:

* ``gamma_server.py``
* ``data_server.py``
* ``clob_public_server.py``

The parent server in ``src/polymarket_mcp/server.py`` mounts those child servers
into one composed ``polymarket`` surface.

Namespace boundaries
--------------------

.. list-table::
   :header-rows: 1

   * - Namespace
     - Backing module
     - Upstream concern
   * - ``gamma``
     - ``servers/gamma_server.py``
     - discovery and event metadata
   * - ``data``
     - ``servers/data_server.py``
     - wallet positions and activity
   * - ``clob``
     - ``servers/clob_public_server.py``
     - public order books and quotes

Request flow
------------

.. code-block:: text

   MCP client
     -> composed FastMCP server
       -> domain server
         -> service adapter
           -> Polymarket API
         -> normalized model
       -> MCP tool/resource result
