

import doiget.doi
import doiget.metadata
import doiget.format


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

    def set_sources(self) -> None:

        if not self.metadata.has_metadata or self.metadata.member_id is None:
            return


