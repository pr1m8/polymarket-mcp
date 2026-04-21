API reference
=============

This reference is organized by layer: composition and settings first, then the
domain-specific models, service adapters, and exposed MCP servers.

Package and composition
-----------------------

.. automodule:: polymarket_mcp
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.server
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.http
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.settings
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.errors
   :members:
   :show-inheritance:

Gamma discovery
---------------

.. automodule:: polymarket_mcp.models.gamma
   :members:
   :show-inheritance:
   :exclude-members: Field, computed_field

.. automodule:: polymarket_mcp.services.gamma
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.servers.gamma_server
   :members:
   :show-inheritance:

Data API
--------

.. automodule:: polymarket_mcp.models.data
   :members:
   :show-inheritance:
   :exclude-members: Field, computed_field

.. automodule:: polymarket_mcp.services.data
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.servers.data_server
   :members:
   :show-inheritance:

Public CLOB
-----------

.. automodule:: polymarket_mcp.models.clob
   :members:
   :show-inheritance:
   :exclude-members: Field, computed_field

.. automodule:: polymarket_mcp.services.clob_public
   :members:
   :show-inheritance:

.. automodule:: polymarket_mcp.servers.clob_public_server
   :members:
   :show-inheritance:
