from __future__ import annotations

import typing
import logging
import abc
import collections

import simdjson

import upath

import doiget.fulltext
import doiget.source
import doiget.metadata


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Publisher(abc.ABC):
    """
    Abstract base class for defining publishers.
    """

    @property
    @abc.abstractmethod
    def member_id(self) -> doiget.metadata.MemberID:
        "CrossRef member ID."
        return self.member_id

    @abc.abstractmethod
    def set_sources(self, fulltext: doiget.fulltext.FullText) -> None:
        """
        Assigns information about full-text sources for this publisher.

        Parameters
        ----------
        fulltext
            Information about the full-text item.

        Notes
        -----
        * This method populates the ``sources`` attribute in the supplied
          ``fulltext`` instance.

        """
        pass

    @abc.abstractmethod
    def acquire(self, link: doiget.source.SourceLink) -> bytes:
        """
        Acquires raw full-text data from the provided source.

        Parameters
        ----------
        link
            Location of the full-text data.

        Returns
        -------
        bytes
            The raw full-text data.

        """
        pass


def set_sources_from_crossref(
    fulltext: doiget.fulltext.FullText,
    acq_method: typing.Callable[[doiget.source.SourceLink], bytes],
    encrypt: bool = False,
    link_check_func: typing.Callable[[doiget.source.SourceLink], bool] | None = None,
) -> None:
    """
    Assigns information about full-text sources from CrossRef.

    Parameters
    ----------
    fulltext
        Information about the full-text item.
    acq_func
        Function that can acquire the source.
    encrypt
        Whether to encrypt the acquired data.
    link_check_func
        Function to check the CrossRef link; if it evaluates to ``False``, then the
        source is not included.

    Notes
    -----
    * This method populates the ``sources`` attribute in the ``formats``
      attribute in the supplied ``fulltext`` instance.

    """

    if not isinstance(fulltext.metadata.raw, simdjson.Object):
        raise ValueError("Missing metadata")

    try:
        links = fulltext.metadata.raw["link"]
    except KeyError:
        return

    if not isinstance(links, simdjson.Array):
        raise ValueError("Unexpected JSON structure")

    for link in links:

        if not isinstance(link, simdjson.Object):
            raise ValueError("Unexpected JSON structure")

        if link["intended-application"] != "text-mining":
            continue

        content_type = str(link["content-type"])

        if content_type == "unspecified":
            LOGGER.warning(f"Skipping due to the content-type '{content_type}'")
            continue

        url = upath.UPath(link["URL"])

        try:
            format_name = doiget.format.FormatName.from_content_type(
                content_type=content_type
            )
        except KeyError:
            LOGGER.warning(
                f"Skipping due to unknown content-type '{content_type}'"
            )
            continue

        if link_check_func is not None:
            link_ok = link_check_func(url)

            if not link_ok:
                LOGGER.warning(
                    f"Skipping due to a failed link check on {url}"
                )
                continue

        source = doiget.source.Source(
            acq_method=acq_method,
            link=url,
            format_name=format_name,
            encrypt=encrypt,
        )

        sources = fulltext.formats[format_name].sources

        if sources is None:
            sources = []

        if source not in sources:
            sources.insert(0, source)

        fulltext.formats[format_name].sources = sources


registry: dict[doiget.metadata.MemberID, Publisher] = {}

T = typing.TypeVar("T", bound=Publisher)


def add_publisher(publisher: type[T]) -> type[T]:
    """
    Adds a publisher handler instance to the registry of known publishers.

    Parameters
    ----------
    publisher
        An instance conforming to the ``doiget.publisher.Publisher`` ABC.

    Returns
    -------
        The (unmodified) argument to the ``publisher`` parameter.

    Notes
    -----
    * This is typically used as a decorator.

    """

    instance = publisher()

    registry[instance.member_id] = instance

    return publisher
