from __future__ import annotations

import typing
import logging
import http

import pydantic_settings

import doiget.config
import doiget.publisher
import doiget.metadata

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):
    api_key: str | None = None
    institution_token: str | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_ELSEVIER_",
        secrets_dir=doiget.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget.publisher.add_publisher
class Elsevier(doiget.publisher.Publisher):

    member_id = doiget.metadata.MemberID(id_="78")

    def __init__(self) -> None:

        self.settings = Settings()

        self.session: doiget.web.WebRequester | None = None

    def initialise(self) -> None:

        headers = {}

        for header_name, header_key in zip(
            ["X-ELS-APIKey", "X-ELS-Insttoken"],
            ["api_key", "institution_token"],
            strict=True,
        ):

            if (value := getattr(self.settings, header_key, None)) is not None:
                headers[header_name] = value
            else:
                LOGGER.warning(f"No authentication for `{header_key}`.")

        self.session = doiget.web.WebRequester(headers=headers)

    def set_sources(self, fulltext: doiget.fulltext.FullText) -> None:

        def source_check_func(source: doiget.source.Source) -> bool:
            return "api.elsevier.com" in str(source.link)

        doiget.publisher.set_sources_from_crossref(
            fulltext=fulltext,
            acq_func=self.acquire,
            encrypt=False,
            source_check_func=source_check_func,
        )

    def acquire(self, source: doiget.source.Source) -> bytes:

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
            LOGGER.warning(
                f"Received the following error from the server: {error_msg}"
            )
            response.raise_for_status()

        return response.content

    @staticmethod
    def validate_xml(data: bytes) -> bool:

        pass




