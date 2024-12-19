from __future__ import annotations

import typing
import logging
import http

import pydantic
import pydantic_settings

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.metadata

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

    api_key: pydantic.SecretStr | None = None
    institution_token: pydantic.SecretStr | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_ELSEVIER_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class Elsevier(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="78")

    def __init__(self) -> None:

        self.settings = Settings()

        self.is_configured = all(
            (
                self.settings.api_key is not None,
                self.settings.institution_token is not None,
            ),
        )

        if not self.is_configured:
            LOGGER.warning("Handler for Elsevier is not configured")

        self.session: doiget_tdm.web.WebRequester | None = None

    def initialise(self) -> None:

        if not self.is_configured:
            return

        headers = {}

        for header_name, header_key in zip(
            ["X-ELS-APIKey", "X-ELS-Insttoken"],
            ["api_key", "institution_token"],
            strict=True,
        ):

            header_value = getattr(self.settings, header_key).get_secret_value()

            headers[header_name] = header_value

        self.session = doiget_tdm.web.WebRequester(headers=headers)

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

        response = self.session.get(url=str(source.link), raise_error=False)

        els_status = response.headers.get("X-ELS-Status")

        if els_status is not None and "warning" in els_status.lower():
            LOGGER.warning(els_status)

        if response.status_code == http.HTTPStatus.UNAUTHORIZED:
            error_info = response.json()
            error_msg = error_info["error-message"]
            LOGGER.warning(f"Received the following error from the server: {error_msg}")

        response.raise_for_status()

        return response.content
