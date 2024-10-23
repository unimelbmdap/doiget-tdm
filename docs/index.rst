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
It is primarily intended for use in text data mining projects where the user has subscriptions to full-text content and data exchange agreements where necessary.

Features
--------

* Acquire full-text of published articles, with built-in support for multiple publishers and their acquisition methods (e.g., network or local files).
* Customise acquisition and add additional publishers.
* Obtain sets of article identifiers (DOIs) from `CrossRef <https://crossref.org>`_.
* Retrieve article metadata from `CrossRef <https://crossref.org>`_.


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
    Outlines the conceptual approach taken by ``doiget``. 

:doc:`/publishers/index`
    Lists the details of publishers with built-in support and describes the process of adding additional publishers.

:doc:`/workflow`
    Describes a typical workflow for using ``doiget``.

:doc:`/using_the_api`
    Examples of using the API to interact with ``doiget`` through Python.

:doc:`/development`
    Describes the development process of ``doiget``, which may be useful for contributing to ``doiget``.

:doc:`/reference/cmd`
    Provides a reference to the ``doiget`` command-line application and its options.

:doc:`/reference/index`
    Provides a reference to the ``doiget`` Python code.
