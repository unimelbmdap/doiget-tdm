from __future__ import annotations

import typing
import logging
import abc
import collections

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

    @property
    def valid_hostname(self) -> str | None:
        "Local host names that can validly acquire data for this publisher."
        return None

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
