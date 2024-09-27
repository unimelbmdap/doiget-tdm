
import logging
import json
import typing
import collections

import simdjson

import rich

import doiget.doi
import doiget.crossref
import doiget.config

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class CrossRefWebAPIClient:

    def __init__(self) -> None:

        self._api = doiget.crossref.CrossRefWebAPI()

    def get_doi_metadata(self, doi: doiget.doi.DOI) -> bytes:

        response = self._api.call(query=f"works/{doi}")

        json_data = response.json()

        if (
            "status" not in json_data
            or json_data["status"] != "ok"
            or "message" not in json_data
            or len(json_data["message"]) == 0
        ):
            msg = f"Unexpected status of metadata response: {json}"
            LOGGER.error(msg)
            raise ValueError(msg)

        metadata = json_data["message"]

        return json.dumps(metadata).encode()


MetadataSource: typing.TypeAlias = typing.Callable[[doiget.doi.DOI], bytes]

crossref_web_api_client = CrossRefWebAPIClient()

metadata_sources = (
    crossref_web_api_client.get_doi_metadata,
)


class Metadata:

    def __init__(self, doi: doiget.doi.DOI) -> None:

        self._doi = doi

        self.path = (
            doiget.config.SETTINGS.data_dir
            / self._doi.group
            / self._doi.quoted
            / f"{self._doi.quoted}_metadata.json"
        )

        self._raw: simdjson.Object | None = None

    @property
    def has_metadata(self) -> bool:
        return self.path.exists()

    @property
    def raw(self) -> simdjson.Object | None:
        if self.has_metadata:
            if self._raw is None:
                self.load()
        return self._raw

    def load(self) -> None:
        raw = simdjson.Parser().load(path=self.path)

        if not isinstance(raw, simdjson.Object):
            raise TypeError("Unexpected type")

        self._raw = raw

    def acquire(
        self,
        metadata_sources: collections.abc.Iterable[MetadataSource] = metadata_sources,
    ) -> bool:

        raw: bytes | None = None

        for metadata_source in metadata_sources:
            try:
                raw = metadata_source(self._doi)
            except Exception:
                continue
            else:
                break

        if raw is None:
            return False

        self.path.parent.mkdir(exist_ok=True, parents=True)

        self.path.write_bytes(raw)

        if not doiget.config.SETTINGS.quiet:
            print(f"Wrote metadata to {self.path}")

        return True

    def show(self, exclude_references: bool = True) -> None:

        metadata = self.raw.as_dict() if self.raw is not None else "No metadata"

        if (
            exclude_references
            and isinstance(metadata, dict)
            and "reference" in metadata
        ):
            del metadata["reference"]

        rich.print(metadata)

