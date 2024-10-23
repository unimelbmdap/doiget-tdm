from __future__ import annotations

import doiget.metadata
import doiget.doi
import doiget.fulltext


class Work:

    def __init__(self, doi: doiget.doi.DOI) -> None:
        """
        Representation of a single item of work.

        Parameters
        ----------
        doi
            Item DOI.
        """

        #: Item DOI
        self.doi: doiget.doi.DOI = doi
        #: Item metadata
        self.metadata: doiget.metadata.Metadata = doiget.metadata.Metadata(doi=doi)
        #: Item full-text
        self.fulltext: doiget.fulltext.FullText = doiget.fulltext.FullText(
            doi=doi,
            metadata=self.metadata,
        )

        #: Item path in data directory
        self.path = (
            doiget.SETTINGS.data_dir
            / self.doi.get_group(
                n_groups=doiget.SETTINGS.data_dir_n_groups
            )
            / self.doi.quoted
        )
