from __future__ import annotations

import typing
import logging
import abc

import simdjson

import upath

import doiget_tdm.fulltext
import doiget_tdm.source
import doiget_tdm.metadata


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Publisher(abc.ABC):
    """
    Abstract base class for defining publishers.
    """

    @property
    @abc.abstractmethod
    def member_id(self) -> doiget_tdm.metadata.MemberID:
        "CrossRef member ID."
        return self.member_id

    @abc.abstractmethod
    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:
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
    def acquire(self, source: doiget_tdm.source.Source) -> bytes:
        """
        Acquires raw full-text data from the provided source.

        Parameters
        ----------
        source
            Information on the source of the full-text data.

        Returns
        -------
        bytes
            The raw full-text data.

        """
        pass


class GenericWebHost:

    def __init__(self) -> None:

        self.session = doiget_tdm.web.WebRequester()

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        def source_check_func(source: doiget_tdm.source.Source) -> bool:

            if not hasattr(self, "source_domain"):
                return True

            return self.source_domain in str(source.link)

        set_sources_from_crossref(
            fulltext=fulltext,
            acq_func=self.acquire,
            encrypt=False,
            source_check_func=source_check_func,
        )

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        response = self.session.get(url=str(source.link))

        return response.content


def set_sources_from_crossref(
    fulltext: doiget_tdm.fulltext.FullText,
    acq_func: typing.Callable[[doiget_tdm.source.Source], bytes],
    encrypt: bool = False,
    source_check_func: typing.Callable[[doiget_tdm.source.Source], bool] | None = None,
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
    source_check_func
        Function to check the CrossRef source; if it evaluates to ``False``, then the
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
            format_name = doiget_tdm.format.FormatName.from_content_type(
                content_type=content_type
            )
        except KeyError:
            LOGGER.warning(f"Skipping due to unknown content-type '{content_type}'")
            continue

        source = doiget_tdm.source.Source(
            acq_func=acq_func,
            link=url,
            format_name=format_name,
            encrypt=encrypt,
        )

        if source_check_func is not None:
            source_ok = source_check_func(source)

            if not source_ok:
                LOGGER.warning(f"Skipping due to a failed source check on {source}")
                continue

        sources = fulltext.formats[format_name].sources

        if source not in sources:
            sources.insert(0, source)

        fulltext.formats[format_name].sources = sources


registry: dict[doiget_tdm.metadata.MemberID, Publisher] = {}

T = typing.TypeVar("T", bound=Publisher)


def add_publisher(publisher: type[T]) -> type[T]:
    """
    Adds a publisher handler instance to the registry of known publishers.

    Parameters
    ----------
    publisher
        An instance conforming to the ``doiget_tdm.publisher.Publisher`` ABC.

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
