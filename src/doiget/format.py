
import enum

import doiget.config
import doiget.doi
import doiget.source


class FormatName(enum.Enum):
    XML = "xml"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    TIFF = "tiff"


class Format:

    def __init__(self, name: FormatName, doi: doiget.doi.DOI) -> None:

        self.name = name
        self.doi = doi

        self.sources: list[doiget.source.Source] | None = None

        self.local_path = (
            doiget.config.SETTINGS.data_dir
            / self.doi.group
            / self.doi.quoted
            / f"{self.doi.quoted}.{self.name.value}"
        )

    @property
    def exists(self) -> bool:
        return self.local_path.exists()

    def read(self) -> bytes:
        return self.local_path.read_bytes()

