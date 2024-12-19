from __future__ import annotations

import logging
import typing

import pyrate_limiter

import pydantic
import pydantic_settings

import upath

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.errors


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

    valid_hostname: str | None = None
    tdm_client_token: pydantic.SecretStr | None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="PYPUBTEXT_WILEY_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class Wiley(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="311")

    def __init__(self) -> None:

        super().__init__()

        self.settings = Settings()

        self.is_configured = self.settings.tdm_client_token is not None

        headers = (
            {
                "Wiley-TDM-Client-Token": (
                    self.settings.tdm_client_token.get_secret_value()
                )
            }
            if self.settings.tdm_client_token is not None
            else {}
        )

        # rate limits:
        # - up to 3 articles per second and
        # - up to 60 requests per 10 minutes, which entails building in a delay
        #   of 10 seconds between requests
        limiter = pyrate_limiter.Limiter(
            pyrate_limiter.RequestRate(
                limit=60,
                interval=10 * 60,
            ),
        )

        self.session = doiget_tdm.web.WebRequester(headers=headers, limiter=limiter)

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        # can't set any sources if the API is not configured
        if not self.is_configured:
            return

        # we have already narrowed from the above, but type checker doesn't know that
        assert self.settings.tdm_client_token is not None

        # the API only has PDF
        format_name = doiget_tdm.format.FormatName.PDF

        link = upath.UPath(
            f"https://api.wiley.com/onlinelibrary/tdm/v1/articles/{fulltext.doi.quoted}"
        )

        source = doiget_tdm.source.Source(
            acq_func=self.acquire,
            link=link,
            format_name=format_name,
            encrypt=False,
        )

        fulltext.formats[format_name].sources = [source]

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if isinstance(source.link, typing.Sequence):
            raise ValueError(f"Unexpected link: {source.link}")

        if (
            self.settings.valid_hostname is not None
            and self.settings.valid_hostname != doiget_tdm.config.SETTINGS.hostname
        ):
            raise doiget_tdm.errors.InvalidHostnameError()

        response = self.session.get(url=str(source.link))

        return response.content
