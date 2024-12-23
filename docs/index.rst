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

.. warning::
    This package is primarily intended for use in text data mining projects where the user has subscriptions to full-text content and has organised data exchange agreements.
    Acquisition for most publishers will not work without configuration - see :doc:`/publishers/avail_publishers` for configuration details.

Features
--------

* Acquire full-text of published articles, with built-in support for multiple publishers and their acquisition methods (e.g., network or local files).
* Currently supported publishers (given appropriate access and configuration):
    * American Medical Association (AMA)
    * American Psychological Association (APA)
    * Elsevier
    * Frontiers
    * IOP
    * PeerJ
    * PLoS
    * PNAS
    * Royal Society
    * Springer-Nature
    * Taylor & Francis
    * Wiley
* Customise acquisition and add additional publishers.
* Retrieve article metadata from `Crossref <https://crossref.org>`_, optionally using a Lightning key:value (DOI:metadata) database formed from a Crossref public data export via `crossref-lmdb <https://github.com/unimelbmdap/crossref-lmdb>`_.


Installation
------------

The package can be installed using ``pip``:

.. code-block:: bash

    pip install doiget-tdm


Quickstart
----------

Show the default configuration settings:

.. code-block:: bash

    doiget-tdm show-config

Download the full-text (XML) of the journal article with DOI `10.1371/journal.pbio.1002611 <https://doi.org/10.1371/journal.pbio.1002611>`_ to the default directory:

.. code-block:: bash

    doiget-tdm acquire '10.1371/journal.pbio.1002611'

Next, you can read through the :doc:`/workflow` document to understand how to use the package in a text data mining project and the :doc:`/concepts` document to learn more about the approach taken by ``doiget-tdm``.

Documentation guide
-------------------

:doc:`/workflow`
    Describes a typical workflow for using ``doiget-tdm``.

:doc:`/configuration`
    Describes the available configuration options and how they can be specified.

:doc:`/publishers/index`
    Lists the details of publishers with built-in support and describes the process of adding additional publishers.

:doc:`/concepts`
    Outlines the conceptual approach taken by ``doiget-tdm``. 

:doc:`/reference/cmd`
    Provides a reference to the ``doiget-tdm`` command-line application and its options.

:doc:`/reference/index`
    Provides a reference to the ``doiget-tdm`` Python code.


Contact
-------

Issues can be raised via the `Github repository <https://github.com/unimelbmdap/doiget-tdm/issues>`_.


Authors
-------

Please feel free to email if you find this package to be useful or have any suggestions or feedback.

* Damien Mannion:
    * **Email:** `damien.mannion@unimelb.edu.au <mailto:damien.mannion@unimelb.edu.au>`_
    * **Organisation:** `Melbourne Data Analytics Platform <https://unimelb.edu.au/mdap>`_, `The University of Melbourne <https://www.unimelb.edu.au>`_
    * **Title:** Senior Research Data Specialist
    * **Website:** `https://www.djmannion.net <https://www.djmannion.net>`_
