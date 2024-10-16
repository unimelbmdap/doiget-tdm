from __future__ import annotations

import pathlib
import enum
import logging

import pyrage

import typing_extensions

import doiget.config
import doiget.doi
import doiget.source


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class FormatName(enum.Enum):
    XML = "xml"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    TIFF = "tiff"

    @classmethod
    def from_content_type(cls, content_type: str) -> typing_extensions.Self:

        lut = {
            "application/pdf": "pdf",
            "text/html": "html",
            "text/plain": "txt",
            "application/xml": "xml",
            "text/xml": "xml",
            "image/tiff": "tiff",
        }

        return cls(lut[content_type])


class Format:

    def __init__(
        self,
        name: FormatName,
        doi: doiget.doi.DOI,
    ) -> None:

        self.name = name
        self.doi = doi

        self.sources: list[doiget.source.Source] | None = None

        group = self.doi.get_group(
            n_groups=doiget.config.SETTINGS.data_dir_n_groups
        )

        self.local_path = (
            doiget.config.SETTINGS.data_dir
            / group
            / self.doi.quoted
            / f"{self.doi.quoted}.{self.name.value}"
        )

    @property
    def exists(self) -> bool:
        return self.local_path.exists()

    @property
    def is_encrypted_sentinel_path(self) -> pathlib.Path:
        return self.local_path.with_suffix(
            self.local_path.suffix + ".encrypted"
        )

    @property
    def is_encrypted(self) -> bool:
        return self.is_encrypted_sentinel_path.exists()

    def acquire(self) -> None:

        sources = (
            self.sources
            if self.sources is not None
            else []
        )

        if len(sources) == 0:
            LOGGER.warning(f"No sources for {self}")

        for source in sources:

            try:
                data = source.acquire()
            except doiget.errors.ACQ_ERRORS as err:
                LOGGER.warning(
                    f"Error when acquiring source {source} ({err})"
                )
                continue

            try:
                source.validate(data=data)
            except doiget.errors.ValidationError as err:
                LOGGER.warning(
                    f"Error when validating data from source {source} ({err})"
                )
                continue

            if source.encrypt:
                if doiget.config.SETTINGS.encryption_passphrase is None:
                    raise ValueError(
                        "Source is specified as requiring encryption but "
                        + "encryption passphrase configuration setting is missing"
                    )

                data = pyrage.passphrase.encrypt(
                    plaintext=data,
                    passphrase=(
                        doiget.config.SETTINGS.encryption_passphrase.get_secret_value()
                    ),
                )

                LOGGER.info(
                    "Writing encryption sentinel file to "
                    + f"{self.is_encrypted_sentinel_path}"
                )
                self.is_encrypted_sentinel_path.touch()

            LOGGER.info(
                f"Writing full-text content to {self.local_path}"
            )
            self.local_path.write_bytes(data)

            break

        else:
            raise ValueError(f"Could not acquire from any sources for {self}")

    def load(self) -> bytes:

        data = self.local_path.read_bytes()

        if not self.is_encrypted:
            return data

        if doiget.config.SETTINGS.encryption_passphrase is None:
            raise ValueError(
                "Source is specified as requiring encryption but "
                + "encryption passphrase configuration setting is missing"
            )

        decrypted_data: bytes = pyrage.passphrase.decrypt(
            ciphertext=data,
            passphrase=(
                doiget.config.SETTINGS.encryption_passphrase.get_secret_value()
            ),
        )

        return decrypted_data

