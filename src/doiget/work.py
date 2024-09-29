import doiget.metadata
import doiget.doi
import doiget.fulltext

class Work:

    def __init__(self, doi: doiget.doi.DOI) -> None:

        self.doi = doi
        self.metadata = doiget.metadata.Metadata(doi=doi)
        self.fulltext = doiget.fulltext.FullText(doi=doi, metadata=self.metadata)
