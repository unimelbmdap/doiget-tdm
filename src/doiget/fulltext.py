

import doiget.doi
import doiget.metadata
import doiget.format
import doiget.publisher


class FullText:

    def __init__(
        self,
        doi: doiget.doi.DOI,
        metadata: doiget.metadata.Metadata,
    ) -> None:

        self.doi = doi
        self.metadata = metadata

        self.formats = {
            format_name: doiget.format.Format(
                name=format_name,
                doi=doi,
            )
            for format_name in doiget.format.FormatName
        }

        self._sources_set = False

    def set_sources(self) -> None:

        if not self.metadata.exists or self.metadata.member_id is None:
            return

        publisher = doiget.publisher.registry[self.metadata.member_id]

        publisher.set_sources(fulltext=self)

    def acquire(self) -> None:

        if not self._sources_set:
            self.set_sources()
            self._sources_set = True

        for fmt_name in doiget.SETTINGS.format_preference_order:

            fmt = self.formats[fmt_name]

            fmt.acquire()

    def load(
        self,
        fmt: doiget.format.FormatName | None = None,
    ) -> tuple[bytes, doiget.format.FormatName]:

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

            return (data, curr_fmt)

        msg = f"No loadable data found for {self}"
        raise ValueError(msg)
