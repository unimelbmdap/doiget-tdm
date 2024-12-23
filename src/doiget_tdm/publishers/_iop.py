from __future__ import annotations

import typing
import logging
import json
import tempfile
import zipfile
import pathlib

import pydantic
import pydantic_settings

import pysftp
import paramiko

import upath

import simdjson

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.work
import doiget_tdm.format


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

    valid_hostname: str | None = None
    username: pydantic.SecretStr | None = None
    password: pydantic.SecretStr | None = None
    server_address: str = "iopp-public-transfer-server.cld.iop.org"
    server_port: int = 22

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_IOP_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class IOP(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="266")

    def __init__(self) -> None:

        self.settings = Settings()

        self.is_configured = all(
            (
                self.settings.username is not None,
                self.settings.password is not None,
            )
        )

        if not self.is_configured:
            LOGGER.warning("Handler for IOP is not configured")

        self.cache_dir = doiget_tdm.config.SETTINGS.cache_dir / "iop"
        self.cache_dir.mkdir(exist_ok=True)

        self.server_file_list_path = self.cache_dir / "iop_server_file_list.json"

        self._file_list: simdjson.Object | None = None

        self._connection: pysftp.Connection | None = None

    def initialise(self) -> None:

        if not self.is_configured:
            return

        assert self.settings.username is not None
        assert self.settings.password is not None

        if self._connection is None or (
            hasattr(self._connection, "_sftp_live") and not self._connection._sftp_live
        ):

            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None

            LOGGER.info("Connecting to the IOP sFTP server")

            self._connection = pysftp.Connection(
                host=self.settings.server_address,
                username=self.settings.username.get_secret_value(),
                password=self.settings.password.get_secret_value(),
                port=self.settings.server_port,
                cnopts=cnopts,
            )

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        if self._file_list is None:
            self.load_server_file_list()

        assert self._file_list is not None

        for format_name in [
            doiget_tdm.format.FormatName.XML,
            doiget_tdm.format.FormatName.PDF,
        ]:

            format_list = self._file_list[format_name.name]

            if not isinstance(format_list, simdjson.Object):
                raise ValueError()

            try:
                filename = format_list[str(fulltext.doi)]
            except KeyError:
                try:
                    filename = format_list[str(fulltext.doi).upper()]
                except KeyError:
                    msg = f"No entry in the server file list for {fulltext.doi}"
                    LOGGER.error(msg)
                    break

            link = f"{format_name.name}data/{filename}"

            source = doiget_tdm.source.Source(
                acq_func=self.acquire,
                link=upath.UPath(link),
                format_name=format_name,
                encrypt=False,
            )

            fulltext.formats[format_name].sources = [source]

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if isinstance(source.link, typing.Sequence):
            raise ValueError(f"Unexpected link: {source.link}")

        doiget_tdm.errors.check_hostname(valid_hostname=self.settings.valid_hostname)

        self.initialise()

        assert self._connection is not None

        tmp_file = tempfile.NamedTemporaryFile(delete=False)
        tmp_file.close()

        tmp_path = pathlib.Path(tmp_file.name)

        try:

            if not self._connection.exists(remotepath=str(source.link)):
                msg = f"Remote path {source.link} not on server"
                LOGGER.error(msg)
                raise doiget_tdm.errors.AcquisitionError(msg)

            self._connection.get(
                remotepath=str(source.link),
                localpath=str(tmp_path),
            )

        except paramiko.ssh_exception.SSHException as err:
            tmp_path.unlink()
            msg = "Received download error ({err})"
            LOGGER.error(msg)
            raise doiget_tdm.errors.AcquisitionError(msg) from err

        except Exception as err:
            tmp_path.unlink()
            msg = "Received download error ({err})"
            LOGGER.error(msg)
            raise doiget_tdm.errors.AcquisitionError(msg) from err

        data: bytes | None

        try:
            with zipfile.ZipFile(tmp_path) as zip_handle:

                filenames = zip_handle.namelist()

                within_zip_filenames = [
                    filename
                    for filename in filenames
                    if filename.endswith(f".{str(source.link)[:3].lower()}")
                ]

                if len(within_zip_filenames) != 1:
                    raise ValueError(f"More filenames than expected: {filenames}")

                (within_zip_filename,) = within_zip_filenames

                data = zip_handle.read(within_zip_filename)

        except Exception as err:
            msg = f"Receieved zip file error {err}"
            LOGGER.error(msg)
            raise doiget_tdm.errors.AcquisitionError(msg) from err

        finally:
            tmp_path.unlink()

        return data

    def form_server_file_list(self) -> None:

        self.initialise()

        if self._connection is None:
            raise ValueError()

        LOGGER.info("Forming server file list for IOP")

        file_list: dict[str, dict[str, str]] = {
            "XML": {},
            "PDF": {},
        }

        for file_type in ["XML", "PDF"]:

            dir_name = f"{file_type}data"

            with self._connection.cd(dir_name):

                dir_contents = self._connection.listdir()

                for filename in dir_contents:

                    doi = self.get_doi_from_filename(filename=filename)

                    file_list[file_type][doi] = filename

        self.save_server_file_list(file_list=file_list)

        LOGGER.info(f"Saved IOP server file list to {self.server_file_list_path}")

    @staticmethod
    def get_doi_from_filename(filename: str) -> str:

        name = filename.strip(".zip")

        try:
            i_doi_start = name.index("10__")
        except ValueError:

            underscores = [i_char for (i_char, char) in enumerate(name) if char == "_"]

            name = "10__" + name[underscores[4] + 1 :]

            i_doi_start = 0

        doi_encoded = name[i_doi_start:]

        doi = doi_encoded.replace("__", ".").replace("_", "/")

        return doi

    def save_server_file_list(self, file_list: dict[str, dict[str, str]]) -> None:

        with self.server_file_list_path.open("w") as handle:
            json.dump(file_list, handle)

    def load_server_file_list(self) -> simdjson.Object:

        raw_file_data = self.server_file_list_path.read_bytes()

        file_list = simdjson.Parser().parse(raw_file_data)

        if not isinstance(file_list, simdjson.Object):
            raise ValueError()

        self._file_list = file_list

        return file_list
