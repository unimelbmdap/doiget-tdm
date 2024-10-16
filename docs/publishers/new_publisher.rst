Defining a new publisher
========================

Additional publishers can be added to ``doiget`` by those with knowledge of the Python programming language.
A new publisher is created by describing a class that inherits from the :py:class:`doiget.publisher.Publisher` abstract base class (ABC).
A directory containing the Python source file(s) is passed to ``doiget`` via the ``extra_handlers_path`` option described in :doc:`/configuration`.

Overview of the full-text acquisition process
---------------------------------------------

When a request is initiated to acquire the full-text for a given DOI, the first check is whether the metadata (from CrossRef) for the DOI is present in the ``doiget`` data directory.
If it is not present, the metadata is acquired from CrossRef and stored in the ``doiget`` data directory.
Because the metadata is necessary for the acquisition of full-text content by ``doiget``, the full-text acquisition request fails if the metadata cannot be acquired.

Using the metadata, ``doiget`` then identifies the publisher of the DOI based on its ``member`` property.
This member ID is then used to index into ``doiget``'s registry of *handlers*, which are Python classes that specify how full-text content is acquired for a given publisher.
If there is no handler for the member ID, the full-text acquisition for the DOI fails.

The handler is then tasked with specifying the *source(s)* of full-text content for each applicable *format* (XML, PDF, HTML, TXT, and TIFF).
When specifying a source, the handler needs to describe a method for its acquisition, its location in a form that the handler can interpret (e.g., a URL), whether it needs to be encrypted, its format, and a method for validating that the acquisition proceeded correctly.

With the sources having been defined, ``doiget`` then iterates through each full-text format (in the configured format preference order).
If the format already exists as a file in the ``doiget`` data directory, then it is not re-acquired and the format is skipped.
If it does not exist, ``doiget`` iterates through each full-text source for the format.
For each source, ``doiget`` attempts to use its specification to acquire the full-text content.
If the acquisition or the validation of the acquired full-text content fails, ``doiget`` proceeds to the next source; otherwise, ``doiget`` skips any remaining sources.
If the full-text content was unable to be acquired for the format or if ``doiget`` is configured to attempt to acquire all possible formats, ``doiget`` then proceeds to the next format.



Overview of a new publisher implementation
------------------------------------------

The first item of information that is required for a new publisher its its CrossRef member ID.
Perhaps the simplest way to obtain this information is to find a DOI that is associated with the publisher and view its CrossRef metadata via the `CrossRef web API <https://api.crossref.org/swagger-ui/index.html#/Works/get_works__doi_>`_.
The member ID is the ``member`` attribute in the metadata, and is represented in ``doiget`` in the :py:class:`doiget.metadata.MemberID` class.

The next task is to implement the :py:class:`doiget.publisher.Publisher.set_sources` method.
This method receives an instance of :py:class:`doiget.fulltext.FullText` (as ``fulltext``), which has a ``formats`` property that is a dictionary that maps a :py:class:`doiget.format.FormatName` to a :py:class:`doiget.format.Format` instance.
Here, a 'format' refers to a specific form of full-text content for a DOI, such as XML, PDF, and HTML.
Each :py:class:`doiget.format.Format` instance has a ``sources`` property, which is a list of zero or more instances of :py:class:`doiget.source.Source`.

The responsibility of the ``set_sources`` method is to populate the list of sources with instances of ``Source`` for each applicable format for a particular DOI.
The first piece of information required for a ``Source`` is a ``link``.
This ``link`` is typically an instance of ``upath.UPath`` (see `upathlib <https://upathlib.readthedocs.io/en/latest/>`_), though sequences of ``upath.UPath`` instances are also allowed (e.g., to support nested zip file structures), and it identifies the location from which the full-text content can be acquired.
The second piece of information required is the ``format_name``, which describes the format of the full-text content at ``link``.
The third piece of information, which is optional, is to specify whether the contents are to be encrypted via the ``encrypt`` property.
The fourth and final piece of information is the method that can be used to acquire the ``link``.
This is specified via a method that receives a single ``link`` parameter and returns the associated full-text content as ``bytes``.


Example of a new publisher implementation
-----------------------------------------

Here, we will walk through the process of creating a new publisher.
