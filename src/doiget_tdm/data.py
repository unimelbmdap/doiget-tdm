"""
Interface to the items in the data directory.
"""

import typing
import os
import posix
import logging

import doiget_tdm


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def iter_unsorted_works(
    test_if_valid_work: typing.Callable[[doiget_tdm.Work], bool] | None = None,
) -> typing.Iterable[doiget_tdm.Work]:
    """
    Iterator through the works in the data directory, in unsorted order.

    Parameters
    ----------
    test_if_valid_work
        Function to test whether work is skipped (if returns `False`).

    Returns
    -------
        An iterable that yields works within the data directory.
    """

    for item in _iter_paths():

        doi = doiget_tdm.DOI(doi=item.name, unquote=True)

        work = doiget_tdm.Work(doi=doi)

        if test_if_valid_work is not None:
            if not test_if_valid_work(work):
                continue

        yield work


def _iter_paths() -> typing.Iterable[posix.DirEntry[str]]:

    # using scandir because it is faster than listdir, glob, etc.

    for path in os.scandir(path=doiget_tdm.SETTINGS.data_dir):

        if not path.is_dir():
            continue

        if doiget_tdm.SETTINGS.data_dir_n_groups is None:

            if path.name.isdigit():
                LOGGER.warning(
                    f"Path with digits ({path}) found; skipping"
                )
                continue

            yield path

        else:

            if not path.name.isdigit():
                LOGGER.warning(
                    f"Path without digits ({path}) found; skipping"
                )
                continue

            for inner_path in os.scandir(path=path.path):

                if not inner_path.is_dir():
                    continue

            yield inner_path
