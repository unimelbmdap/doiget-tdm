.. include:: substitutions.txt

.. |---|   unicode:: U+2014 .. EM DASH
   :trim:

Concepts
========

This section provides a conceptual overview of the full-text acquisition process.

When a request is initiated to acquire the full-text for a given Digital Object Identifier (DOI; see `this post <https://community.crossref.org/t/eli5-what-s-a-doi-membership-ticket-of-the-month-october-2024/12442>`_ for a primer on DOIs), the first check is whether the metadata (from crossref) for the DOI is present in the ``doiget-tdm`` data directory.
If it is not present, the metadata is acquired from crossref and stored in the ``doiget-tdm`` data directory.
Because the metadata is necessary for the acquisition of full-text content by ``doiget-tdm``, the full-text acquisition request fails if the metadata cannot be acquired.

.. note::

    To obtain the metadata for an item, we use `crossref <https://www.crossref.org/>`_.
    We query crossref using either its `web API <https://api.crossref.org>`_ or a local `LMDB <https://lmdb.readthedocs.io/>`_ database formed from the `crossref public data file <https://www.crossref.org/blog/2024-public-data-file-now-available-featuring-new-experimental-formats/>`_ (the latter is particularly useful when processing large numbers of DOIs as it does not require network calls).
    The resulting metadata is stored locally in its native JSON format (potentially compressed), with the JSON structure described `in the crossref API documentation <https://api.crossref.org/swagger-ui/index.html#/Works/get_works__doi_>`_.


Using the metadata, ``doiget-tdm`` then identifies the publisher of the DOI based on its ``member`` property.
This value is a numerical string that identifies the registrant or steward of the DOI (see `this post on the crossref forum <https://community.crossref.org/t/how-to-find-all-journals-currently-published-by-a-publisher/3949/2>`_).

The member ID is then used to index into ``doiget-tdm``'s registry of *handlers*, which are Python classes that specify how full-text content is acquired for a given publisher.
If there is no handler for the member ID, the full-text acquisition for the DOI fails; because there are not many publishers from whom full-text content can be obtained *without* the use of a handler specific to the publisher, ``doiget-tdm`` only supports acquiring full-text content from supported publishers (functionality can be added for unsupported publishers by :doc:`publishers/new_publisher`).

.. note::

    A given DOI is immutable after it is registered.
    However, the steward of a DOI can change.
    For example, the publisher can change due to corporate acquisitions.
    In such cases, the responsibility for the DOI metadata is `with the new publisher <https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/updating-after-title-transfer/>`_.
    The DOI *prefix* remains with the registering publisher, given its immutability, but the new publisher is required to `update the metadata <https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/updating-after-title-transfer/#00623>`_, including any links provided to full-text sources.

Each handler has three primary responsibilities:

#. **Configuration, initialisation, and maintaining state across full-text requests.** This can include tasks like reading a publisher-specific API key or passphrase, making a connection with a local database containing a full-text corpus, and keeping track of request timings to comply with rate limits.
#. **Constructing a list of full-text sources.** With access to the crossref metadata, the handler is responsible for generating a list of full-text sources (e.g., HTTP URLs, sFTP URLs, local file paths, etc.), each with an identified format (e.g., XML, PDF, etc.) and validation method (used to ensure that it is indeed in the requested format and is indeed the full-text and not an abstract or excerpt).
#. **Acquiring the full-text content.** This could involve performing a web request, or reading from a local zip file, or downloading from an sFTP server, etc.

The handler is first tasked with specifying the source(s) of full-text content for each applicable *format* (XML, PDF, HTML, TXT, and TIFF).
``doiget-tdm`` then iterates through each full-text format, in the configured format preference order.
If the format already exists as a file in the ``doiget-tdm`` data directory, then it is not re-acquired and the format is skipped.
If it does not exist, ``doiget-tdm`` iterates through each full-text source for the format.
For each source, ``doiget-tdm`` attempts to use its specification to acquire the full-text content.
If the acquisition or the validation of the acquired full-text content fails, ``doiget-tdm`` proceeds to the next source; otherwise, ``doiget-tdm`` skips any remaining sources.
If the full-text content was unable to be acquired for the format or if ``doiget-tdm`` is configured to attempt to acquire all possible formats, ``doiget-tdm`` then proceeds to the next format; otherwise, the full-text acquisition is complete.

