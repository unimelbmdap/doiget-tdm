.. include:: substitutions.txt

Documentation
=============

.. toctree::
    :hidden:

    configuration
    workflow
    publishers/index
    concepts
    using_the_api
    reference/cmd
    reference/index

``doiget-tdm`` is a command-line application and Python library for obtaining the metadata and full-text of published journal articles.
It is primarily intended for use in text data mining projects where the user has subscriptions to full-text content and has organised data exchange agreements.

Features
--------

* Acquire full-text of published articles, with built-in support for multiple publishers and their acquisition methods (e.g., network or local files).
* Customise acquisition and add additional publishers.
* Retrieve article metadata from `Crossref <https://crossref.org>`_.
* Currently supported publishers:
    * Elsevier
    * Frontiers
    * PeerJ
    * PLoS
    * Royal Society
    * Springer-Nature

Installation
------------

The package can be installed using ``pip``:

.. code-block:: bash

    pip install git+https://github.com/unimelbmdap/doiget-tdm


Quickstart
----------

Show the default configuration settings:

.. code-block:: bash

    doiget-tdm show-config

Download the full-text (XML) of the journal article with DOI `10.1371/journal.pbio.1002611 <https://doi.org/10.1371/journal.pbio.1002611>`_ to the default directory:

.. code-block:: bash

    doiget-tdm acquire '10.1371/journal.pbio.1002611'


Documentation guide
-------------------

:doc:`/configuration`
    Describes the available configuration options and how they can be specified.

:doc:`/workflow`
    Describes a typical workflow for using ``doiget-tdm``.

:doc:`/publishers/index`
    Lists the details of publishers with built-in support and describes the process of adding additional publishers.

:doc:`/concepts`
    Outlines the conceptual approach taken by ``doiget-tdm``. 

:doc:`/using_the_api`
    Examples of using the API to interact with ``doiget-tdm`` through Python.

.. :doc:`/development`
      Describes the development process of ``doiget-tdm``, which may be useful for contributing to ``doiget-tdm``.

:doc:`/reference/cmd`
    Provides a reference to the ``doiget-tdm`` command-line application and its options.

:doc:`/reference/index`
    Provides a reference to the ``doiget-tdm`` Python code.
