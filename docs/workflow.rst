Workflow
========

Obtain DOIs of interest
-----------------------

The first step is to obtain a set of DOIs for which you would like to acquire full-text content.
Obtaining such DOIs is outside of the scope of ``doiget-tdm`` and depends on your text data mining goals.
For example, you might query the `CrossRef API <https://api.crossref.org/swagger-ui/index.html#/Works/get_works>`_ to find all the DOIs for a particular author, or institution, or journal, etc.
For input into ``doiget-tdm``, you can save these DOIs either as a text file with one DOI per line or as a CSV file with a column named "DOI".

Begin configuring ``doiget-tdm``
--------------------------------

There are a few `configuration options <configuration.html>`_ for ``doiget-tdm`` that are worth considering at this point, particularly:

``data_dir``
    This is the directory in which the full-text content and metadata for the DOIs is stored.

``data_dir_n_groups``
    If you have a large number of DOIs, it is recommended to set this option so that there are not too many directories directly within ``data_dir``.

``email_address``
    It is highly recommended to provide your email address, which is passed to CrossRef when obtaining DOI metadata so as to access their 'polite' pool in the API.

See :doc:`/configuration` for how to specify these options, and for details on the other configuration options that are available in ``doiget-tdm``.


Evaluate publishers
-------------------

Each DOI will have an associated publisher, and this publisher will affect the process used to acquire its full-text content.
Hence, the next step is to evaluate the publishers that are responsible for the DOIs in the set of interest.

Unless the publisher was defined as part of the query used to obtain the set of DOIs, it is likely that the DOIs will be distributed across multiple publishers.
Being able to accurately identify the publishers is assisted by using ``doiget-tdm`` to download the metadata (from CrossRef) for each of the DOIs.
For example, assuming you have saved a file containing the DOIs of interest in ``doi_list.txt``, you can run the following command to acquire the DOI metadata:

.. code-block:: bash

    doiget-tdm fulltext acquire --only-metadata doi_list.txt

To determine the publishers for the set of DOIs, you can then use ``doiget-tdm`` to generate a status report on the set of DOIs:

.. code-block:: bash

    doiget-tdm status doi_list.txt

This will print a summary of the status of the DOI set, including the distribution of publishers.

.. note::

    You can also provide a ``--output-path`` option to ``doiget-tdm status`` to save a file that has one row per DOI and columns that relate to aspects of the metadata like the publisher.

Make publisher agreements and update ``doiget-tdm`` configuration
-----------------------------------------------------------------

This is often facilitated by an institutional librarian, with whom the publisher subscriptions are made.

If there are publishers that are in the set of DOIs but not in the :doc:`/publishers/avail_publishers` for ``doiget-tdm``, you can investigate :doc:`/publishers/new_publisher` to add custom functionality to ``doiget-tdm``.


Acquire full-text
-----------------

You can then acquire the full-text by running:

.. code-block:: bash

    doiget-tdm acquire doi_list.txt


For each DOI in the file ``doi_list.txt``, ``doiget-tdm`` will infer the publisher that is responsible for the DOI and will then use publisher-specific logic for acquiring the full-text content --- using the publisher-specific configuration that you have provided.

.. note::

    Some publishers require requests to be made from a specific IP address, so you might need to run this command on multiple machines.
    Such publishers tend to have a ``valid_hostname`` configuration option, which only attempts to acquire the full-text content for a particular DOI if the hostname of the requesting machine matches the value of ``valid_hostname``.
    However, you can also provide one (or more) member IDs (using the ``--only-member-id`` parameter) and it will only attempt to acquire DOIs with matching member IDs.


Use full-text content
---------------------

Accessing within Python
~~~~~~~~~~~~~~~~~~~~~~~

If doing further processing using Python, ...


Accessing within the filesystem
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The retrieved files will be stored within the directory specified by the ``data_dir`` configuration option.
The specific location within ``data_dir`` depends on the value of the ``data_dir_n_groups`` configuration option:

``data_dir_n_groups`` is 0
    Files for the DOI are stored in ``${DATA_DIR}/${QUOTED_DOI}/``

``data_dir_n_groups`` is > 0
    Files for the DOI are stored in ``${DATA_DIR}/${DOI_GROUP}/${QUOTED_DOI}/``

Here, ``${DATA_DIR}`` is the value of ``data_dir``, ``${DOI_GROUP}`` is a number between 0 and ``data_dir_n_groups`` - 1, and ``${QUOTED_DOI}`` is the DOI string in 'quoted' form (see `quote <https://docs.python.org/3/library/urllib.parse.html#urllib.parse.quote>`_).

.. note::

    The use of the 'quoted' form of DOI strings is to work around the conflict between the presence of characters like ``/`` in DOI strings and the meaning of characters like ``/`` in filesystems --- as a directory separator, in this case.

For example, the data for the DOI "10.1371/journal.pbio.1002611" will be stored in:

``data_dir_n_groups`` is 0
    ``${DATA_DIR}/10.1371%2Fjournal.pbio.1002611/``

``data_dir_n_groups`` is 5,000
    ``${DATA_DIR}/1785/10.1371%2Fjournal.pbio.1002611/``




