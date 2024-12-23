Configuration
=============

In addition to runtime options when executing ``doiget-tdm``, as documented in :doc:`/reference/cmd`, there are configuration options for ``doiget-tdm``.

.. note::

    There are also per-publisher configuration options that are described in :doc:`/publishers/avail_publishers`.

The active configuration settings can be shown by running ``doiget-tdm show-config``.

Options
-------

``data_dir``
    The directory to store the acquired metadata and full-text content.

    The default is platform-dependent and is determined using the ``platformdirs`` `package <https://github.com/tox-dev/platformdirs>`_.
    Typical directories are:

    Linux
        ``~/.local/share/doiget_tdm/``

    Mac
        ``~/Library/Application Support/doiget_tdm/data/``

    Windows
        ``~\AppData\Local\doiget_tdm\data``

``cache_dir``
    The directory to store temporary but persistent files, such as full-text data archives that span multiple items.

    The default is platform-dependent and is determined using the ``platformdirs`` `package <https://github.com/tox-dev/platformdirs>`_.
    Typical directories are:

    Linux
        ``~/.cache/doiget_tdm/``

    Mac
        ``~/Library/Caches/doiget_tdm/``

    Windows
        ``~\AppData\Local\doiget-tdm\doiget-tdm\Cache``

``data_dir_n_groups``
    The acquired data is stored on the filesystem (within ``data_dir``) with one directory per DOI.
    This results in a large number of directories, which can become prohibitively large for particular collections or storage systems.
    This option inserts an additional layer of directories, with each DOI pseudorandomly allocated to one of ``data_dir_n_groups`` subdirectories in ``data_dir``.

    The default is to not have this intermediate grouping layer.

``email_address``
    The DOI metadata is typically acquired from the Crossref web API, which asks that users provide their email address as part of the request header.

    The default is to not specify an email address.

``encryption_passphrase``
    The full-text content acquired from publishers can optionally be encrypted in ``data_dir``, using this passphrase.

    The default is to store the full-text data unencrypted.

``log_level``
    This sets the level at which messages are printed to the console.
    The accepted values are, in increasing degrees of verbosity, ``DEBUG``, ``INFO``, ``WARNING``, ``ERROR``, ``CRITICAL`` (see `logging levels <https://docs.python.org/3/library/logging.html#logging-levels>`_).

    The default is ``WARNING``.

``file_log_level``
    As per the ``log_level`` option, but for the messages written to the log file.

    The default is ``INFO``.

``crossref_lmdb_path``
    The path to a directory containing a local LMDB version of the Crossref public data.
    If present, it will be used to obtain the DOI metadata in preference to a web API call.

    The default is to not have a LMDB available.

``format_preference_order``
    Full-text content can be provided in multiple formats, and this option allows the search order for formats to be set.
    Additionally, formats can be excluded from acquisition by not including them in this list.

    The default is ``["xml", "pdf", "html", "txt", "tiff"]``.

``skip_remaining_formats``
    This option sets the approach when a particular format for a DOI has been successfully acquired.
    If ``False``, the remaining formats in ``format_preference_order`` are attempted to be acquired; if ``True``, the attempted acquisition of the remaining formats is skipped.

    The default is ``True``.

``extra_handlers_path``
    A directory from which to import additional publisher handlers.
    This directory needs to contain one or more ``.py`` files, which are imported after the built-in publisher handlers have been imported.

    The default is to not have any additional publisher handlers.

``metadata_compression_level``
    Level to compress the JSON metadata when storing.
    Set it to ``-1`` to use the default compression level, ``0`` for no compression, or a number between ``1`` (least compression) to ``9`` (most compression).

    The default is ``-1``.

Setting the configuration
-------------------------

The configuration for ``doiget-tdm`` can be set via three ways:

Files in a configuration directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The directory in which ``doiget-tdm`` will search for configuration settings varies by platform.
Typical directories are:

Linux
    ``~/.config/doiget_tdm/``

Mac
    ``~/Library/Application Support/doiget_tdm/config/``

Windows
    ``~\AppData\Local\doiget-tdm\doiget_tdm\config``

A configuration option can be set by creating a file inside the config directory with a name that has the form ``doiget_tdm_${OPTION}`` and the contents are the option setting.
For example, the ``log_level`` option can be set to ``WARNING`` by creating a file called ``doiget_tdm_log_level`` that contains the text ``WARNING``.

Within a ``.env`` file
~~~~~~~~~~~~~~~~~~~~~~

Configuration settings can be read from a file named ``.env`` that is contained in the directory in which ``doiget-tdm`` is executed.
This file contains one option per line, in the form ``DOIGET_TDM_${OPTION}=${VALUE}``.
For example, the ``log_level`` option can be set to ``WARNING`` by having a line in ``.env`` that is ``DOIGET_TDM_LOG_LEVEL=INFO``.

Using environment variables
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Configuration options can be set by using system environment variables.
These follow the same convention as options set using the ``.env`` file approach.
