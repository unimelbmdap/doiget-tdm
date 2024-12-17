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

No configuration required.

.. note::
    This uses simple web requests to acquire content from PLoS.
    This method is discouraged for bulk article acquisitions; consider using the PLoS corpus file instead (see `PLoS Text and Data Mining <https://api.plos.org/text-and-data-mining.html>`_).

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
