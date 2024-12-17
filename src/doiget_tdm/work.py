from __future__ import annotations

import doiget_tdm.metadata
import doiget_tdm.doi
import doiget_tdm.fulltext


class Work:

    def __init__(self, doi: doiget_tdm.doi.DOI) -> None:
        """
        Representation of a single item of work.

        Parameters
        ----------
        doi
            Item DOI.
        """

        #: Item DOI
        self.doi: doiget_tdm.doi.DOI = doi
        #: Item metadata
        self.metadata: doiget_tdm.metadata.Metadata = doiget_tdm.metadata.Metadata(
            doi=doi
        )
        #: Item full-text
        self.fulltext: doiget_tdm.fulltext.FullText = doiget_tdm.fulltext.FullText(
            doi=doi,
            metadata=self.metadata,
        )

        #: Item path in data directory
        self.path = (
            doiget_tdm.SETTINGS.data_dir
            / self.doi.get_group(n_groups=doiget_tdm.SETTINGS.data_dir_n_groups)
            / self.doi.quoted
        )
