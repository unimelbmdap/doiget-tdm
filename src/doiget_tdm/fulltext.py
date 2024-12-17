from __future__ import annotations

import logging
import typing

import doiget_tdm.doi
import doiget_tdm.metadata
import doiget_tdm.format
import doiget_tdm.publisher


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class LoadedData(typing.NamedTuple):
    """
    Data and its format as loaded from a file.
    """

    data: bytes
    fmt: doiget_tdm.format.FormatName


class FullText:

    def __init__(
        self,
        doi: doiget_tdm.doi.DOI,
        metadata: doiget_tdm.metadata.Metadata,
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
        self.doi: doiget_tdm.doi.DOI = doi
        #: CrossRef metadata for the DOI.
        self.metadata: doiget_tdm.metadata.Metadata = metadata

        #: Potential full-text formats
        self.formats: dict[doiget_tdm.format.FormatName, doiget_tdm.format.Format] = {
            format_name: doiget_tdm.format.Format(
                name=format_name,
                doi=doi,
            )
            for format_name in doiget_tdm.format.FormatName
        }

        self._sources_set = False

    def set_sources(self) -> None:
        """
        Uses the publisher handler for the item to populate the full-text sources.
        """

        if not self.metadata.exists or self.metadata.member_id is None:
            return

        if self.metadata.member_id in doiget_tdm.publisher.registry:
            publisher = doiget_tdm.publisher.registry[self.metadata.member_id]
            publisher.set_sources(fulltext=self)

    def acquire(self) -> None:
        """
        Attempt to acquire the full-text content.
        """

        LOGGER.info(f"Attempting to acquire full-text for the DOI {self.doi}")

        if not self._sources_set:
            self.set_sources()
            self._sources_set = True

        any_success = False

        for fmt_name in doiget_tdm.SETTINGS.format_preference_order:

            fmt = self.formats[fmt_name]

            if fmt.exists:
                LOGGER.info(
                    f"Full-text {fmt_name.name} content already exists for {self.doi}; "
                    + "skipping"
                )

            else:

                LOGGER.info(f"Trying to acquire the {fmt_name.name} format")

                try:
                    fmt.acquire()
                except ValueError:
                    LOGGER.warning(
                        f"Could not acquire full-text content for {fmt.name}"
                    )
                    continue

                LOGGER.info(f"Successfully acquired the {fmt_name.name} format")

            any_success = True

            if doiget_tdm.SETTINGS.skip_remaining_formats:
                LOGGER.info("Skipping any remaining formats")
                break

        if not any_success:
            LOGGER.error(f"Unable to obtain any full-text content for {self.doi}")

    def load(
        self,
        fmt: doiget_tdm.format.FormatName | None = None,
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

        formats = doiget_tdm.SETTINGS.format_preference_order if fmt is None else [fmt]

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
        fmt: doiget_tdm.format.FormatName,
    ) -> bool:
        return self.formats[fmt].exists
