from __future__ import annotations

import pathlib
import enum
import logging

import pyrage

import doiget_tdm.config
import doiget_tdm.doi
import doiget_tdm.source


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class FormatName(enum.Enum):
    """
    Possible full-text content formats.
    """

    XML = "xml"
    PDF = "pdf"
    HTML = "html"
    TXT = "txt"
    TIFF = "tiff"

    @classmethod
    def from_content_type(
        cls: type[FormatName],
        content_type: str,
    ) -> FormatName:
        """
        Return the format name from a content type.

        Parameters
        ----------
        content_type
            The MIME type of the content.

        """

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
        doi: doiget_tdm.doi.DOI,
    ) -> None:
        """
        Represents the full-text content data for a particular format.

        Parameters
        ----------
        name
            The type of format.
        doi
            The item DOI.
        """

        #: Format name.
        self.name: FormatName = name
        #: Item DOI.
        self.doi: doiget_tdm.doi.DOI = doi

        #: The sources from which the full-text content for this format can be acquired.
        self.sources: list[doiget_tdm.source.Source] = []

        group = self.doi.get_group(
            n_groups=doiget_tdm.config.SETTINGS.data_dir_n_groups
        )

        #: Path to the full-text file for this format in the data directory.
        self.local_path: pathlib.Path = (
            doiget_tdm.config.SETTINGS.data_dir
            / group
            / self.doi.quoted
            / f"{self.doi.quoted}.{self.name.value}"
        )

    @property
    def exists(self) -> bool:
        """
        Whether a file exists in the data directory for the format.
        """
        return self.local_path.exists()

    @property
    def is_encrypted_sentinel_path(self) -> pathlib.Path:
        """
        The path to a sentinel (empty) file that marks that the content
        is encrypted.
        """
        return self.local_path.with_suffix(self.local_path.suffix + ".encrypted")

    @property
    def is_encrypted(self) -> bool:
        """
        Whether the full-text content for the format is encrypted.
        """
        return self.is_encrypted_sentinel_path.exists()

    def acquire(self) -> None:
        """
        Attempt to acquire the full-text content for the format.
        """

        if len(self.sources) == 0:
            LOGGER.warning(f"No sources for {self.name}")

        for source in self.sources:

            try:
                data = source.acquire()
            except doiget_tdm.errors.ACQ_ERRORS as err:
                LOGGER.warning(f"Error when acquiring source {source} ({err})")
                continue
            except Exception as err:
                LOGGER.warning(
                    f"Unexpected error when acquiring source {source} ({err})"
                )
                continue

            try:
                source.validate(data=data)
            except doiget_tdm.errors.ValidationError as err:
                LOGGER.warning(
                    f"Error when validating data from source {source} ({err})"
                )
                continue
            except Exception as err:
                LOGGER.warning(
                    f"Unexpected error when validating source {source} ({err})"
                )
                continue

            if source.encrypt:
                if doiget_tdm.config.SETTINGS.encryption_passphrase is None:
                    raise ValueError(
                        "Source is specified as requiring encryption but "
                        + "encryption passphrase configuration setting is missing"
                    )

                data = pyrage.passphrase.encrypt(
                    plaintext=data,
                    passphrase=(
                        doiget_tdm.config.SETTINGS.encryption_passphrase.get_secret_value()
                    ),
                )

                LOGGER.info(
                    "Writing encryption sentinel file to "
                    + f"{self.is_encrypted_sentinel_path}"
                )
                # keep retrying if the write failed
                for attempt in doiget_tdm.errors.get_retry_controller(logger=LOGGER):
                    with attempt:
                        self.is_encrypted_sentinel_path.touch()

            LOGGER.info(f"Writing full-text content to {self.local_path}")
            # keep retrying if the write failed
            for attempt in doiget_tdm.errors.get_retry_controller(logger=LOGGER):
                with attempt:
                    self.local_path.write_bytes(data)

            break

        else:
            raise ValueError(f"Could not acquire from any sources for {self}")

    def load(self) -> bytes:
        """
        Loads the full-text content from a file in the data directory, performing
        decryption where necessary.
        """

        data = self.local_path.read_bytes()

        if not self.is_encrypted:
            return data

        if doiget_tdm.config.SETTINGS.encryption_passphrase is None:
            raise ValueError(
                "Source is specified as requiring encryption but "
                + "encryption passphrase configuration setting is missing"
            )

        decrypted_data: bytes = pyrage.passphrase.decrypt(
            ciphertext=data,
            passphrase=(
                doiget_tdm.config.SETTINGS.encryption_passphrase.get_secret_value()
            ),
        )

        return decrypted_data
