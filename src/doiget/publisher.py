from __future__ import annotations

import typing
import logging
import abc
import collections

import doiget.fulltext
import doiget.source


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Publisher(abc.ABC):
    """
    Abstract base class for defining publishers.
    """

    @property
    @abc.abstractmethod
    def member_id(self) -> str:
        "CrossRef member ID."
        return self.member_id

    @property
    @abc.abstractmethod
    def names(self) -> tuple[str, ...]:
        "Names used by the publisher in CrossRef metadata."
        return self.names

    @property
    @abc.abstractmethod
    def domains(self) -> tuple[str, ...]:
        "Domain names used by the publisher."
        return self.domains

    @property
    @abc.abstractmethod
    def valid_hostname(self) -> str | None:
        "Local host names that can validly acquire data for this publisher."
        return self.valid_hostname

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

    def __repr__(self) -> str:
        names = ", ".join([f"'{name}'" for name in self.names])
        return f"Publisher for names: {names}"


class GenericPublisher(Publisher):

    member_id = "-1"
    names = ()
    domains = ()
    valid_hostname = None

    def __init__(self) -> None:
        self.session = doiget.web.WebRequester()

    def __repr__(self) -> str:
        return "Generic publisher"

    def set_sources(self, fulltext: doiget.fulltext.FullText) -> None:
        pass

    def acquire(self, link: doiget.source.SourceLink) -> bytes:

        active_link = (
            link[0] if isinstance(link, typing.Sequence)
            else link
        )

        response = self.session.get(url=str(active_link))

        return response.content

generic_publisher = GenericPublisher()

registry: dict[str, collections.defaultdict[str, Publisher]] = {
    reg_name: collections.defaultdict(lambda: generic_publisher)
    for reg_name in ("member_id", "name", "domain")
}

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

    for (reg_name, reg) in registry.items():
        reg[getattr(instance, reg_name)] = instance

    return publisher
