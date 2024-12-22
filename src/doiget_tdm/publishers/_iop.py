from __future__ import annotations

import typing
import logging
import http

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

    @staticmethod
    def get_filenames_from_work(
        work: doiget_tdm.work.Work,
        format_name: doiget_tdm.format.FormatName,
    ) -> str:

        # 1_0957-4484_30_40_405602_10__1088_1361-6528_ab2d69.zip

        # where:
        # 1 is a prefix meaning 'JATS+PDF metadata'
        # 0957-4484 is the journal ISSN
        # 30 is the volume
        # 40 is the issue number
        # 405602 is the article number (or page number)

        # 10__1088_1361-6528_ab2d69 is the escaped DOI 10.1088/1361-6528/ab2d69

        # In the XMLdata directory the naming scheme is identical except that the prefix is 2 rather than 1.

        prefix: str

        if format_name is doiget_tdm.format.FormatName.PDF:
            prefix = "1"
        elif format_name is doiget_tdm.format.FormatName.XML:
            prefix = "2"
        else:
            msg = f"Unexpected format type ({format_name})"
            raise ValueError(msg)

        volume = work.metadata.volume
        issue = work.metadata.issue
        page = work.metadata.page

        doi = str(work.doi)

        doi_encoded = (
            doi
            .replace(".", "__")
            .replace("/", "_")
        )

        issns = work.metadata.issns

        filenames = [
            "_".join(
                [
                    prefix,
                    issn,
                    volume,
                    issue,
                    page,
                    doi_encoded,
                ]
            )
            + ".zip"
            for issn in issns
        ]

        return filenames
