from __future__ import annotations

import urllib.parse
import re


# https://www.crossref.org/blog/dois-and-matching-regular-expressions/
DOI_MATCHER = re.compile(r"(?i)10.\d{4,9}/[-._;()/:A-Z0-9]+$")

class DOI:

    __slots__ = ("_doi",)

    def __init__(self, doi: str) -> None:
        self._doi = urllib.parse.unquote(string=doi)

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
    def parts(self) -> tuple[str, str]:
        (prefix, *suffixes) = tuple(self._doi.split("/"))
        suffix = "/".join(suffixes)
        return (prefix, suffix)

    @property
    def prefix(self) -> str:
        return self.parts[0]

    @property
    def suffix(self) -> str:
        return self.parts[1]

    @property
    def quoted(self) -> str:
        return urllib.parse.quote(
            string=self._doi,
            safe="",
        )

    @staticmethod
    def from_url(url: str) -> DOI:

        try:
            (match,) = DOI_MATCHER.findall(url)
        except ValueError as err:
            raise ValueError(f"No suitable DOI found in {url}") from err

        return DOI(doi=match)
