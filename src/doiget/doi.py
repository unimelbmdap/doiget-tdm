"""
Represent Digital Object Identifiers (DOIs) and their creation from input.
"""


from __future__ import annotations

import urllib.parse
import re
import hashlib
import typing
import logging
import pathlib
import csv

import more_itertools

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
DOI_MATCHER = re.compile(r"(?i)10.\d{4,9}/[-._;()/:A-Z0-9]+$")


class Stringable(typing.Protocol):
    """
    A protocol for an object with a `__str__` method.
    """
    def __str__(self) -> str:
        ...

class DOIParts(typing.NamedTuple):
    """
    Parts (prefix and suffix) of a DOI.
    """
    prefix: str
    suffix: str


class DOI:

    __slots__ = ("_doi",)

    def __init__(
        self,
        doi: Stringable,
        unquote: bool = True,
    ) -> None:
        """
        A representation of a Digital Object Identifier (DOI).

        Parameters
        ----------
        doi
            The DOI, as anything that can be converted to a string (via ``str``).
        unquote
            Converts special characters in ``doi`` from 'quoted' form (e.g., where the
            '/' character is represented by '%2F') into 'unquoted'.
        """

        self._doi = str(doi)

        if self._doi.startswith("http"):
            raise ValueError(
                f"The string {self._doi} looks to be a URL; "
                + "use the `.from_url` constructor."
            )

        if not self._doi.startswith("10."):
            raise ValueError(
                f"The string {self._doi} does not appear to be a DOI."
            )

        if unquote:
            self._doi = urllib.parse.unquote(string=self._doi)

    def __str__(self) -> str:
        return self._doi

    def __repr__(self) -> str:
        return f"DOI(doi='{self}')"

    def __hash__(self) -> int:
        return hash(self._doi)

    def __eq__(self, other: object) -> bool:
        return hash(self) == hash(other)

    def __lt__(self, other: object) -> bool:
        "Useful for sorting"
        return str(self) < str(other)

    @property
    def parts(self) -> DOIParts:
        """
        Decompose a DOI into its prefix and suffix.

        Returns
        -------
            A namedtuple with prefix and suffix attributes.
        """

        (prefix, *suffixes) = tuple(self._doi.split("/"))
        suffix = "/".join(suffixes)
        return DOIParts(prefix=prefix, suffix=suffix)

    @property
    def quoted(self) -> str:
        """
        A 'quoted' version of the DOI in which special characters are replaced.
        """
        return urllib.parse.quote(
            string=self._doi,
            safe="",
        )

    @staticmethod
    def from_url(url: str, unquote: bool = True) -> DOI:
        """
        Create a DOI object from a URL containing a DOI.

        Parameters
        ----------
        url
            The URL containing the DOI.
        unquote
            Converts special characters in ``doi`` from 'quoted' form (e.g., where the
            '/' character is represented by '%2F') into 'unquoted'.

        Returns
        -------
            A DOI object from the extracted DOI.

        Notes
        -----
        * This uses a regular expression to find the DOI in the URL. This
          is successful for most but not all DOIs.
        """

        try:
            (match,) = DOI_MATCHER.findall(url)
        except ValueError as err:
            raise ValueError(f"No suitable DOI found in {url}") from err

        return DOI(doi=match, unquote=unquote)

    def get_group(
        self,
        n_groups: int | None,
    ) -> str:
        """
        Determine the 'group' to which a DOI belongs.

        This assigns a given DOI to a group between 0 and ``n_groups - 1`` based
        on a hash of its characters.

        Parameters
        ----------
        n_groups
            The total number of groups that can be assigned.

        Returns
        -------
            The group as a string of numbers or an empty string
            if ``n_groups`` is ``None``.
        """

        if n_groups in [None, 0]:
            return ""

        if typing.TYPE_CHECKING:
            assert n_groups is not None

        hashed = hashlib.sha256(self._doi.encode())
        hash_value = int.from_bytes(hashed.digest(), "big")
        group = str(hash_value % n_groups)

        return group


def form_dois_from_input(
    raw_input: typing.Sequence[str],
    unquote: bool = True,
) -> list[DOI]:
    """
    Form a list of DOI objects from a sequence of strings or a path
    to a file containing DOIs as strings.

    Parameters
    ----------
    raw_input
        Sequence of either strings containing DOIs or a path to a file
        containing DOIs as strings.
    unquote
        Converts special characters in ``doi`` from 'quoted' form (e.g., where the
        '/' character is represented by '%2F') into 'unquoted'.

    Returns
    -------
        A list of DOI objects, with any duplicate entries removed.
    """

    LOGGER.debug(f"Creating DOIs from the input: {raw_input}")

    raw_dois: list[str] = []

    is_single_input = len(raw_input) == 1

    if is_single_input:

        (raw_item,) = raw_input

        # try it as a path
        raw_path = pathlib.Path(raw_item)

        is_path = raw_path.exists() and raw_path.is_file()

        if is_path:
            raw_dois_from_file = form_raw_dois_from_path(path=raw_path)
            raw_dois.extend(raw_dois_from_file)
        else:
            raw_dois.append(raw_item)

    else:
        raw_dois.extend(raw_input)

    dois: list[DOI] = []

    for raw_item in raw_dois:

        constructor = DOI.from_url if raw_item.startswith("http") else DOI

        try:
            doi = constructor(raw_item, unquote=unquote)
        except ValueError:
            LOGGER.error(f"No valid DOI could be interpreted from {raw_item}")
            continue
        else:
            dois.append(doi)

    # remove duplicates
    dois = list(more_itertools.unique_everseen(dois))

    return dois


def form_raw_dois_from_path(path: pathlib.Path) -> list[str]:
    """
    Reads DOI strings from a file.

    Parameters
    ----------
    path
        Path to the file containing the DOIs. The DOIs can either be each on a
        single line in the file or they can be in a column named 'DOI' or 'doi'
        in a CSV format.

    Returns
    -------
        A list of raw DOI strings.
    """

    raw_dois: list[str] = []

    with path.open(newline="") as handle:

        reader = csv.DictReader(handle)

        doi_key = (
            None
            if reader.fieldnames is None
            else (
                "doi"
                if "doi" in reader.fieldnames
                else "DOI" if "DOI" in reader.fieldnames else None
            )
        )

        if doi_key is not None:
            raw_dois.extend([row[doi_key] for row in reader])
        else:
            handle.seek(0)
            raw_dois.extend(handle.read().splitlines())

    return raw_dois
