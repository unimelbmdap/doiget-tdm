from __future__ import annotations

import logging
import typing
import zipfile
import io
import pathlib

import pydantic
import pydantic_settings

import upath

import pyrage

import py7zr

import simdjson

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.errors


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

    data_path: pathlib.Path | None = None
    passphrase: pydantic.SecretStr | None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="PYPUBTEXT_WILEY_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class APA(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="15")

    def __init__(self) -> None:

        super().__init__()

        self.settings = Settings()

        self.is_configured = (
            self.settings.data_path is not None
            and self.settings.data_path.exists()
            and self.settings.passphrase is not None
            and doiget_tdm.config.SETTINGS.encryption_passphrase is not None
        )

        if not self.is_configured:
            LOGGER.warning("Handler for APA is not configured")

        if doiget_tdm.config.SETTINGS.encryption_passphrase is None:
            LOGGER.warning(
                "No `encryption_passphase` setting is provided, "
                + "which is required for APA"
            )

        self.file_lut: dict[str, tuple[str, str]] | None = None
        self.raw_data: bytes | None = None

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        # can't set any sources if the API is not configured
        if not self.is_configured:
            return

        # we have already narrowed from the above, but type checker doesn't know that
        assert self.settings.data_path is not None

        format_name = doiget_tdm.format.FormatName.XML

        if "alternative-id" not in fulltext.metadata.raw:
            LOGGER.warning(f"No alternative IDs found for APA work {fulltext.doi}")
            return

        if not isinstance(fulltext.metadata.raw["alternative-id"], simdjson.Array):
            raise ValueError("Unexpected JSON structure")

        # raw files are saved under an APA ID, rather than the DOI
        alternative_ids = [
            str(alt_id)
            for alt_id in fulltext.metadata.raw["alternative-id"].as_list()
            if "-" in str(alt_id)
        ]

        if len(alternative_ids) == 0:
            LOGGER.warning(f"No alternative IDs found for APA work {fulltext.doi}")
            return

        for alternative_id in alternative_ids:

            link = upath.UPath(f"{alternative_id}.xml")

            source = doiget_tdm.source.Source(
                acq_func=self.acquire,
                link=link,
                format_name=format_name,
                encrypt=True,
            )

            fulltext.formats[format_name].sources.append(source)

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if isinstance(source.link, typing.Sequence):
            raise ValueError(f"Unexpected link: {source.link}")

        if self.file_lut is None:
            LOGGER.info("Initialising APA data archive")
            self.form_file_lut()

        assert self.file_lut is not None

        if str(source.link) not in self.file_lut:
            msg = f"Path {source.link} not found in the APA data archive"
            LOGGER.error(msg)
            raise doiget_tdm.errors.AcquisitionError(msg)

        return self.read_from_archive(alternative_id=str(source.link))


    def form_file_lut(self) -> None:

        assert self.settings.data_path is not None
        assert self.settings.passphrase is not None

        # the APA data is assumed to be encrypted using age

        # load all the encrypted raw data
        apa_raw_data = self.settings.data_path.read_bytes()

        # decrypt and store for future access
        self.raw_data = pyrage.passphrase.decrypt(
            ciphertext=apa_raw_data,
            passphrase=self.settings.passphrase.get_secret_value(),
        )

        with zipfile.ZipFile(io.BytesIO(self.raw_data)) as apa_zip_handle:

            apa_zip_namelist = apa_zip_handle.namelist()

            for apa_zip_name in apa_zip_namelist:

                apa_zip_name_suffix = pathlib.Path(apa_zip_name).suffix

                if apa_zip_name_suffix not in [".zip", ".7z"]:
                    msg = f"Unexpected suffix in {apa_zip_name}"
                    LOGGER.error(msg)
                    raise ValueError(msg)

                is_7z = apa_zip_name_suffix == ".7z"

                # read the bytes of the file within the APA zip
                inner_data = apa_zip_handle.read(name=apa_zip_name)

                # this file is itself a compressed archive
                inner_handle_func = py7zr.SevenZipFile if is_7z else zipfile.ZipFile

                inner_handle = inner_handle_func(io.BytesIO(inner_data))

                inner_namelist = inner_handle.namelist()

                for inner_name in inner_namelist:

                    inner_path = pathlib.Path(inner_name)

                    if not inner_path.suffix == ".xml":
                        continue

                    if self.file_lut is None:
                        self.file_lut = {}

                    self.file_lut[inner_path.name] = (
                        apa_zip_name,
                        inner_name,
                    )

    def read_from_archive(self, alternative_id: str) -> bytes:

        assert self.file_lut is not None

        (outer_path, inner_path) = self.file_lut[alternative_id]

        assert self.raw_data is not None

        is_7z = outer_path.endswith(".7z")

        with zipfile.ZipFile(io.BytesIO(self.raw_data)) as apa_zip_handle:

            # read the bytes of the file within the APA zip
            outer_data = apa_zip_handle.read(name=outer_path)

            data: bytes

            if is_7z:
                with py7zr.SevenZipFile(io.BytesIO(outer_data)) as inner_handle:
                    data = inner_handle.read([inner_path])[inner_path].read()
            else:
                with zipfile.ZipFile(io.BytesIO(outer_data)) as inner_handle:
                    data = inner_handle.read(inner_path)

        return data
