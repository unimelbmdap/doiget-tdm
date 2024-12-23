from __future__ import annotations

import typing
import logging
import http
import json

import pydantic
import pydantic_settings

import pysftp

import simdjson

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.work
import doiget_tdm.format


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

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


# @doiget_tdm.publisher.add_publisher
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

        def source_check_func(source: doiget_tdm.source.Source) -> bool:
            return "api.elsevier.com" in str(source.link)

        doiget_tdm.publisher.set_sources_from_crossref(
            fulltext=fulltext,
            acq_func=self.acquire,
            encrypt=False,
            source_check_func=source_check_func,
        )

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if isinstance(source.link, typing.Sequence):
            raise ValueError(f"Unexpected link: {source.link}")

        if self.session is None:
            self.initialise()

        if self.session is None:
            raise ValueError("Error initialising session")

        response = self.session.get(url=str(source.link))

        els_status = response.headers.get("X-ELS-Status")

        if els_status is not None and "warning" in els_status.lower():
            LOGGER.warning(els_status)

        if response.status_code == http.HTTPStatus.UNAUTHORIZED:
            error_info = response.json()
            error_msg = error_info["error-message"]
            LOGGER.warning(f"Received the following error from the server: {error_msg}")
            response.raise_for_status()

        return response.content

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

    @staticmethod
    def get_doi_from_filename(filename: str) -> str:

        name = filename.strip(".zip")

        try:
            i_doi_start = name.index("10__")
        except ValueError:

            underscores = [
                i_char
                for (i_char, char) in enumerate(name)
                if char == "_"
            ]

            name = "10__" + name[underscores[4] + 1:]

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
