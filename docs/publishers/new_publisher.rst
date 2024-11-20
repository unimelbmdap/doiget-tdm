Defining a new publisher
========================

Additional publishers can be added to ``doiget-tdm`` by those with knowledge of the Python programming language.
A new publisher is created by describing a class that inherits from the :py:class:`doiget_tdm.publisher.Publisher` abstract base class (ABC).
A directory containing the Python source file(s) is passed to ``doiget-tdm`` via the ``extra_handlers_path`` option described in :doc:`/configuration`.


Overview of a new publisher implementation
------------------------------------------

The first item of information that is required for a new publisher its its CrossRef member ID.
Perhaps the simplest way to obtain this information is to find a DOI that is associated with the publisher and view its CrossRef metadata via the `CrossRef web API <https://api.crossref.org/swagger-ui/index.html#/Works/get_works__doi_>`_.
The member ID is the ``member`` attribute in the metadata, and is represented in ``doiget-tdm`` in the :py:class:`doiget_tdm.metadata.MemberID` class.

The next task is to implement the :py:class:`doiget_tdm.publisher.Publisher.set_sources` method.
This method receives an instance of :py:class:`doiget_tdm.fulltext.FullText` (as ``fulltext``), which has a ``formats`` property that is a dictionary that maps a :py:class:`doiget_tdm.format.FormatName` to a :py:class:`doiget_tdm.format.Format` instance.
Here, a 'format' refers to a specific form of full-text content for a DOI, such as XML, PDF, and HTML.
Each :py:class:`doiget_tdm.format.Format` instance has a ``sources`` property, which is a list of zero or more instances of :py:class:`doiget_tdm.source.Source`.

The responsibility of the ``set_sources`` method is to populate the list of sources with instances of ``Source`` for each applicable format for a particular DOI.
The first piece of information required for a ``Source`` is a ``link``.
This ``link`` is typically an instance of ``upath.UPath`` (see `upathlib <https://upathlib.readthedocs.io/en/latest/>`_), though sequences of ``upath.UPath`` instances are also allowed (e.g., to support nested zip file structures), and it identifies the location from which the full-text content can be acquired.
The second piece of information required is the ``format_name``, which describes the format of the full-text content at ``link``.
The third piece of information, which is optional, is to specify whether the contents are to be encrypted via the ``encrypt`` property.
The fourth and final piece of information is the method that can be used to acquire the ``link``.
This is specified via a method that receives a single ``link`` parameter and returns the associated full-text content as ``bytes``.

.. note::

    Publishers can (optionally) `provide links to full-text content <https://www.crossref.org/documentation/retrieve-metadata/rest-api/text-and-data-mining-for-members/>`_ via the ``link`` property in the metadata.
    The ``link`` property contains one or more items that specify a link to full-text content.
    The items are primarily distinguished by their ``intended-application`` (e.g., ``"text-mining"``) and ``content-type`` (e.g., ``"application/xml"``).


Example of a new publisher implementation
-----------------------------------------

Here, we will walk through the process of creating a new publisher.
