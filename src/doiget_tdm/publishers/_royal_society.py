from __future__ import annotations

import pydantic_settings

import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.errors
import doiget_tdm.config


class Settings(pydantic_settings.BaseSettings):

    valid_hostname: str | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_ROYAL_SOCIETY_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class RoyalSociety(
    doiget_tdm.publisher.GenericWebHost,
    doiget_tdm.publisher.Publisher,
):

    member_id = doiget_tdm.metadata.MemberID(id_="175")

    # the server returns an X-RateLimit-Limit header, which could
    # be used to set custom rate limits

    def __init__(self) -> None:

        super().__init__()

        self.settings = Settings()

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if (
            self.settings.valid_hostname is not None
            and self.settings.valid_hostname != doiget_tdm.config.SETTINGS.hostname
        ):
            raise doiget_tdm.errors.InvalidHostnameError()

        response = self.session.get(url=str(source.link))

        return response.content
