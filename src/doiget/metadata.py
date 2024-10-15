from __future__ import annotations

import logging
import json
import typing
import collections
import time
import pathlib
import zlib

import simdjson

try:
    import lmdb  # type: ignore[import-untyped]
except ImportError:
    HAS_LMDB = False
else:
    HAS_LMDB = True

import rich

import doiget.config
import doiget.doi
import doiget.crossref

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

if not HAS_LMDB:
    LOGGER.warning(
        "The package `lmdb` was unable to be imported; disabling "
        + "access to a CrossRef database in LMDB format"
    )


class MemberID:

    __slots__ = ("_id",)

    def __init__(self, id_: object) -> None:
        """
        Represent a CrossRef member ID.

        Parameters
        ----------
        id_
            The CrossRef member ID.
        """

        self._id = str(id_)

        if not self._id.isnumeric():
            msg = f"Provided member ID ({id_}) is not a number"
            raise ValueError(msg)

    def __repr__(self) -> str:
        return f'MemberID(id_="{self._id}")'

    def __str__(self) -> str:
        return self._id

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MemberID):
            raise ValueError("Can only compare member IDs")
        return str(self) == str(other)


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
            msg = f"Unexpected status of metadata response: {json_data}"
            LOGGER.error(msg)
            raise ValueError(msg)

        metadata = json_data["message"]

        return json.dumps(metadata).encode()


class CrossRefLMDBClient:

    def __init__(self, db_path: pathlib.Path) -> None:

        self.db_path = db_path

        self.env: lmdb.Environment | None = None

    def _load(self, n_retries: int = 10) -> lmdb.Environment:

        err: lmdb.InvalidParameterError | None = None

        retry_count = 0

        while retry_count <= n_retries:

            try:
                env: lmdb.Environment = lmdb.Environment(
                    path=str(self.db_path),
                    readonly=True,
                )
            except lmdb.InvalidParameterError as curr_err:
                LOGGER.error(str(err) + "; retrying")
                retry_count += 1
                time.sleep(10)
                err = curr_err
            else:
                break

        else:
            LOGGER.error("Retry count exceeded")
            assert err is not None
            raise err

        return env

    def get_doi_metadata(self, doi: doiget.doi.DOI) -> bytes:

        if self.env is None:
            self._load()

        if self.env is None:
            raise ValueError()

        with self.env.begin() as txn:
            raw_item = txn.get(str(doi).encode(), None)

            if raw_item is None:
                msg = f"{doi} not found in database"
                raise KeyError(msg)

            item = zlib.decompress(raw_item)

        return item


MetadataSource: typing.TypeAlias = typing.Callable[[doiget.doi.DOI], bytes]

def get_metadata_sources() -> tuple[MetadataSource, ...]:

    crossref_web_api_client = CrossRefWebAPIClient()

    metadata_sources: tuple[MetadataSource, ...] = (
        crossref_web_api_client.get_doi_metadata,
    )

    if HAS_LMDB:
        db_path = doiget.config.SETTINGS.crossref_lmdb_path
        if db_path is not None:
            crossref_lmdb_client = CrossRefLMDBClient(db_path=db_path)
            metadata_sources = (
                crossref_lmdb_client.get_doi_metadata,
                *metadata_sources,
            )

    return metadata_sources


metadata_sources = get_metadata_sources()


class Metadata:

    def __init__(self, doi: doiget.doi.DOI) -> None:

        self._doi = doi

        group = self._doi.get_group(
            n_groups=doiget.config.SETTINGS.data_dir_n_groups
        )

        self.path = (
            doiget.config.SETTINGS.data_dir
            / group
            / self._doi.quoted
            / f"{self._doi.quoted}_metadata.json"
        )

        self._raw: simdjson.Object | None = None

        self._member_id: MemberID | None = None
        self._publisher_name: str | None = None

    @property
    def exists(self) -> bool:
        return self.path.exists()

    @property
    def raw(self) -> simdjson.Object | None:
        if self.exists:
            if self._raw is None:
                self.load()
        return self._raw

    @property
    def member_id(self) -> MemberID | None:
        if not self.exists or self.raw is None:
            return None
        if self._member_id is None:
            raw_member_id = self.raw["member"]
            if not isinstance(raw_member_id, str):
                raise ValueError(f"Unexpected member id {raw_member_id}")
            self._member_id = MemberID(id_=raw_member_id)
        return self._member_id

    @property
    def publisher_name(self) -> str | None:

        if (
            not self.exists
            or self.raw is None
            or "publisher" not in self.raw
        ):
            return None

        if self._publisher_name is None:
            raw_publisher_name = self.raw["publisher"]
            if not isinstance(raw_publisher_name, str):
                raise ValueError(f"Unexpected publisher: {raw_publisher_name}")
            self._publisher_name = raw_publisher_name

        return self._publisher_name

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

