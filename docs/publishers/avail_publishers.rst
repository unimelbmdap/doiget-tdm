Available publishers
====================

This describes the publishers that currently have built-in support in ``doiget-tdm`` and their configuration requirements.

American Medical Association (AMA)
----------------------------------

``doiget_tdm_ama_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.
``doiget_tdm_ama_api_key``
    The API key provided by AMA.

.. note::
    Access must be granted by the AMA; see `Text and Data Mining <https://tdm.jamanetwork.com/>`_.

.. note::
    The AMA API only returns full-text content in plain text format.

American Psychological Association (APA)
----------------------------------------

The APA provides full-text content by sending files directly to the requester.
For use with ``doiget-tdm``, these files must be placed into a single zip file.
This zip file then must be encrypted using `age <https://github.com/FiloSottile/age>`_.

``doiget_tdm_apa_data_path``
    The filesystem location of the encrypted zip file referred to above.
``doiget_tdm_apa_passphrase``
    The passphrase to decrypt ``doiget_tdm_apa_data_path``.

.. note::
    Each XML retrieved from the data archive is encrypted when saving in ``data_dir``.
    Hence, the ``encryption_passphrase`` configuration option for ``doiget-tdm`` must be set to use the APA publisher.

Elsevier
--------

``doiget_tdm_elsevier_api_key``
    The API key provided by Elsevier.
``doiget_tdm_elsevier_institution_token``
    The token used for authenticating as an institution.

.. note::
    Access must be granted by Elsevier; see `Text and data mining <https://www.elsevier.com/about/open-science/research-data/text-and-data-mining>`__.

Frontiers
---------

No configuration required.


PeerJ
-----

No configuration required.

PLoS
----

``doiget_tdm_plos_allofplos_path``
    The filesystem path to the PLoS corpus file (see `PLoS Text and Data Mining <https://api.plos.org/text-and-data-mining.html>`_).
    If not specified, the handler will fall back to retrieving the full-text content via web requests; however, this is discouraged for bulk acquisitions.

PNAS
----

``doiget_tdm_pnas_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.

Royal Society
-------------

``doiget_tdm_royal_society_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.

.. note::
    Access must be granted by the Royal Society; see `Data sharing and mining <https://royalsociety.org/journals/ethics-policies/data-sharing-mining/#data-mining>`_.

Sage
----

``doiget_tdm_sage_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.

.. note::
    See `Text and Data Mining on Sage Journals  <https://journals.sagepub.com/page/policies/text-and-data-mining>`_.


Taylor & Francis (Informa)
--------------------------

``doiget_tdm_taylor_and_francis_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.

.. note::
    Access must be granted by Taylor & Francis; see `Text and Data Mining <https://taylorandfrancis.com/our-policies/textanddatamining/>`__.

Springer-Nature
---------------

``doiget_tdm_springer_nature_api_base_url``
    The start of the URL to the Springer-Nature API; typically starts with ``https://`` and ends just before a ``?`` character.
``doiget_tdm_springer_nature_api_key``
    The API key provided by Springer-Nature.
``doiget_tdm_springer_nature_api_suffix``
    The final component of the API path, without the leading ``/``.
``doiget_tdm_springer_nature_n_requests_per_day``
    The limit on the number of requests per day; defaults to 500.

.. note::
    Access must be granted by Springer-Nature; see `Text and data mining at Springer Nature <https://www.springernature.com/gp/researchers/text-and-data-mining>`_.

Wiley
-----

``doiget_tdm_wiley_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.
``doiget_tdm_wiley_tdm_client_key``
    The API key provided by Wiley.

.. note::
    Access must be granted by Wiley; see `Text and Data Mining <https://onlinelibrary.wiley.com/library-info/resources/text-and-datamining>`__.

