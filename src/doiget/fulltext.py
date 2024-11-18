from __future__ import annotations

import logging
import typing

import doiget.doi
import doiget.metadata
import doiget.format
import doiget.publisher


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class LoadedData(typing.NamedTuple):
    """
    Data and its format as loaded from a file.
    """
    data: bytes
    fmt: doiget.format.FormatName


class FullText:

    def __init__(
        self,
        doi: doiget.doi.DOI,
        metadata: doiget.metadata.Metadata,
    ) -> None:
        """
        Full-text content.

        Parameters
        ----------
        doi
            Item DOI.
        metadata
            Item metadata.

        """

        #: Item DOI.
        self.doi: doiget.doi.DOI = doi
        #: CrossRef metadata for the DOI.
        self.metadata: doiget.metadata.Metadata = metadata

        #: Potential full-text formats 
        self.formats: dict[doiget.format.FormatName, doiget.format.Format] = {
            format_name: doiget.format.Format(
                name=format_name,
                doi=doi,
            )
            for format_name in doiget.format.FormatName
        }

        self._sources_set = False

    def set_sources(self) -> None:
        """
        Uses the publisher handler for the item to populate the full-text sources.
        """

        if not self.metadata.exists or self.metadata.member_id is None:
            return

        if self.metadata.member_id in doiget.publisher.registry:
            publisher = doiget.publisher.registry[self.metadata.member_id]
            publisher.set_sources(fulltext=self)

    def acquire(self) -> None:
        """
        Attempt to acquire the full-text content.
        """

        if not self._sources_set:
            self.set_sources()
            self._sources_set = True

        any_success = False

        for fmt_name in doiget.SETTINGS.format_preference_order:

            fmt = self.formats[fmt_name]

            if fmt.exists:
                LOGGER.warning(
                    f"Full-text {fmt_name.name} content already exists for {self.doi}; "
                    + "skipping"
                )

            else:

                try:
                    fmt.acquire()
                except ValueError:
                    LOGGER.warning(
                        f"Could not acquire full-text content for {fmt.name}"
                    )
                    continue

            any_success = True

            if doiget.SETTINGS.skip_remaining_formats:
                break

        if not any_success:
            LOGGER.warning(
                f"Unable to obtain any full-text content for {self.doi}"
            )

    def load(
        self,
        fmt: doiget.format.FormatName | None = None,
    ) -> LoadedData:
        """
        Load the full-text content from the data directory.

        Parameters
        ----------
        fmt
            The desired full-text format. If not specified, the data from the first
            format in the format preference order with full-text content is returned.

        Returns
        -------
            A namedtuple with ``data`` and ``fmt`` attributes.
        """

        formats = (
            doiget.SETTINGS.format_preference_order
            if fmt is None
            else [fmt]
        )

        for curr_fmt in formats:
            fmt_data = self.formats[curr_fmt]

            if not fmt_data.exists:
                continue

            data = fmt_data.load()

            return LoadedData(data=data, fmt=curr_fmt)

        msg = f"No loadable data found for {self}"
        raise ValueError(msg)

    def has_format(
        self,
        fmt: doiget.format.FormatName,
    ) -> bool:
        return self.formats[fmt].exists
