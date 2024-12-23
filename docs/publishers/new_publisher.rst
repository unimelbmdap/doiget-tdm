Defining a new publisher
========================

Additional publishers can be added to ``doiget-tdm`` by those with knowledge of the Python programming language.
A new publisher is created by describing a class that inherits from the :py:class:`doiget_tdm.publisher.Publisher` abstract base class (ABC).
A directory containing the Python source file(s) is passed to ``doiget-tdm`` via the ``extra_handlers_path`` option described in :doc:`/configuration`.

The best way to begin developing code for a new publisher is to read through the code for the built-in publishers.
This code is contained within the ``src/doiget_tdm/publishers`` directory in the source code (`browseable on Github <https://github.com/unimelbmdap/doiget-tdm/tree/main/src/doiget_tdm/publishers>`_).
