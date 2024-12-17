Available publishers
====================

This describes the publishers that currently have built-in support in ``doiget-tdm`` and their configuration requirements.

Elsevier
--------

``doiget_tdm_elsevier_api_key``
    The API key provided by Elsevier.
``doiget_tdm_elsevier_institution_token``
    The token used for authenticating as an institution.

Frontiers
---------

No configuration required.


PLoS
----

``doiget_tdm_plos_allofplos_path``
    The filesystem path to the PLoS corpus file (see `PLoS Text and Data Mining <https://api.plos.org/text-and-data-mining.html>`_).
    If not specified, the handler will fall back to retrieving the full-text content via web requests; however, this is discouraged for bulk acquisitions.

Sage
----

``doiget_tdm_sage_valid_hostname``
    Full-text requests can only be made from systems matching this hostname.

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
