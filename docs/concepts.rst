.. include:: substitutions.txt

.. |---|   unicode:: U+2014 .. EM DASH
   :trim:

Concepts
========

A single item of interest is uniquely identified by its |DOI|.
To obtain information about such an item (its *metadata*), we use the `CrossRef database <https://www.crossref.org/>`_.
We query CrossRef using either its `web API <https://api.crossref.org>`_ or a local `LMDB <https://lmdb.readthedocs.io/>`_ database formed from the `CrossRef public data file <https://www.crossref.org/blog/2024-public-data-file-now-available-featuring-new-experimental-formats/>`_ (the latter is particularly useful when processing large numbers of DOIs as it does not require network calls).
The resulting metadata is stored locally in JSON format, with the JSON structure described `in the CrossRef API documentation <https://api.crossref.org/swagger-ui/index.html#/Works/get_works__doi_>`_.

The two main uses for the item metadata in ``doiget`` are to identify the publisher of the item and to gather any links to the full-text of the item for text data mining purposes.

The primary way that the publisher is identified is by the ``member`` property in the metadata.
This value is a numerical string that identifies the registrant or steward of the DOI (see `this post on the CrossRef forum <https://community.crossref.org/t/how-to-find-all-journals-currently-published-by-a-publisher/3949/2>`_).

Publishers can (optionally) `provide links to full-text content <https://www.crossref.org/documentation/retrieve-metadata/rest-api/text-and-data-mining-for-members/>`_ via the ``link`` property in the metadata.
The ``link`` property contains one or more items that specify a link to full-text content.
The items are primarily distinguished by their ``intended-application`` (e.g., ``"text-mining"``) and ``content-type`` (e.g., ``"application/xml"``).

.. note::

    A given |DOI| is immutable after it is registered.
    However, the steward of a |DOI| can change.
    For example, the publisher can change due to corporate acquisitions.
    In such cases, the responsibility for the |DOI| metadata is `with the new publisher <https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/updating-after-title-transfer/>`_.
    The |DOI| *prefix* remains with the registering publisher, given its immutability, but the new publisher is required to `update the metadata <https://www.crossref.org/documentation/register-maintain-records/maintaining-your-metadata/updating-after-title-transfer/#00623>`_, including any links provided to full-text sources.


When there is an acquisition request for the full-text of an item (e.g., via ``doiget acquire ${DOI}``), the member ID from the metadata is used to identify a *handler* that is tasked with acquiring the full-text for the item.
Each handler has three primary responsibilities:

#. **Configuration, initialisation, and maintaining state across full-text requests.** This can include tasks like reading a publisher-specific API key or passphrase, making a connection with a local database containing a full-text corpus, and keeping track of request timings to comply with rate limits.
#. **Constructing a list of full-text sources.** With access to the CrossRef metadata, the handler is responsible for generating a list of full-text sources (e.g., HTTP URLs, sFTP URLs, local file paths, etc.), each with an identified format (e.g., XML, PDF, etc.).
#. **Acquiring the full-text content.** This could involve performing a web request, or reading from a local zip file, or downloading from an sFTP server, etc. It also involves validating the received content to ensure that it is indeed in the requested format and is indeed the full-text and not an abstract or excerpt.

Because there are not many publishers from whom full-text content can be obtained *without* the use of a handler specific to the publisher, ``doiget`` only supports acquiring full-text content from supported publishers.
Functionality can be restored for unsupported publishers by :ref:`defining_a_new_publisher`.
