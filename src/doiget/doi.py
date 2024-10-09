from __future__ import annotations

import urllib.parse
import re
import hashlib
import typing


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
    def from_url(url: str) -> DOI:
        """
        Create a DOI object from a URL containing a DOI.

        Parameters
        ----------
        url
            The URL containing the DOI.

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

        return DOI(doi=match)

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
