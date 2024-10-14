Configuration
=============

Options
-------

``data_dir``
    The directory to store the acquired metadata and full-text content.

    The default is platform-dependent and is determined using the ``platformdirs`` `package <https://github.com/tox-dev/platformdirs>`_.
    Typical directories are:

    Linux
        ``~/.local/share/doiget/``

    Mac
        ``~/Library/Application Support/doiget/data/``

    Windows
        ``~\AppData\Local\doiget\data``


``data_dir_n_groups``
    The acquired data is stored on the filesystem (within ``data_dir``) with one directory per DOI.
    This results in a large number of directories, which can become prohibitively large for particular collections or storage systems.
    This option inserts an additional layer of directories, with each DOI randomly allocated to one of ``data_dir_n_groups`` subdirectories in ``data_dir``.

    The default is to not have this intermediate grouping layer.

``email_address``
    The DOI metadata is typically acquired from the CrossRef web API, which asks that users provide their email address as part of the request header.

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
    The path to a directory containing a local LMDB version of the CrossRef public data.
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


Setting the configuration
-------------------------

The configuration for ``doiget`` can be set via three ways:

Files in a configuration directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The directory in which ``doiget`` will search for configuration settings varies by platform.
Typical directories are:

Linux
    ``~/.config/doiget/``

Mac
    ``~/Library/Application Support/doiget/config/``

Windows
    ``~\AppData\Local\doiget\doiget\config``
