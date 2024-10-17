.. include:: substitutions.txt

Documentation
=============

.. toctree::
    :hidden:

    configuration
    concepts
    publishers/index
    workflow
    using_the_api
    development
    reference/cmd
    reference/index

``doiget`` is a command-line application and Python library for obtaining the metadata and full-text of published journal articles.

Features
--------

* Acquire full-text of published articles, with built-in support for multiple publishers and their acquisition methods (e.g., network or local files).
* Customise acquisition and add additional publishers.
* Retrieve article metadata from `CrossRef <https://crossref.org>`_.
* Obtain set of article identifiers (DOIs) from `CrossRef <https://crossref.org>`_.


Installation
------------

The package can be installed using ``pip``:

.. code-block:: bash

    pip install git+https://github.com/unimelbmdap/pypubtext


Quickstart
----------

Show the default configuration settings:

.. code-block:: bash

    doiget show-config

Download the full-text (XML) of the journal article with DOI `10.1371/journal.pbio.1002611 <https://doi.org/10.1371/journal.pbio.1002611>`_ to the default directory:

.. code-block:: bash

    doiget acquire '10.1371/journal.pbio.1002611'


Documentation guide
-------------------

:doc:`/configuration`
    Describes the available configuration options and how they can be specified.

:doc:`/concepts`
    Describes the conceptual approach taken by ``doiget``. 
