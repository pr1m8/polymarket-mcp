Release and publishing
======================

Published package
-----------------

* PyPI distribution: ``polymarket-mcp-server``
* Repository: ``pr1m8/polymarket-mcp``
* CLI entrypoint: ``polymarket-mcp``

Release flow
------------

Create and publish a release from a Git tag:

.. code-block:: bash

   git push origin main
   git tag -a v0.1.2 -m "Release v0.1.2"
   git push origin refs/tags/v0.1.2

The GitHub Actions release workflow then:

#. sets up Python and PDM
#. refreshes the PDM lockfile
#. installs the dev dependencies
#. runs ``pdm run test``
#. builds the wheel and sdist
#. publishes to PyPI through GitHub trusted publishing
#. creates a matching GitHub release with the built artifacts attached

Trusted publishing
------------------

PyPI trusted publishing is configured against:

* owner: ``pr1m8``
* repository: ``polymarket-mcp``
* workflow: ``release.yml``
* environment: ``pypi``

No long-lived PyPI API token is required once the trusted publisher is attached
on PyPI.
