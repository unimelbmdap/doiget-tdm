from __future__ import annotations

import upath

import pydantic_settings

import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.errors
import doiget_tdm.config


class Settings(pydantic_settings.BaseSettings):

    valid_hostname: str | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_TAYLOR_AND_FRANCIS_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class TaylorAndFrancis(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="301")

    def __init__(self) -> None:

        self.settings = Settings()

        self.session = doiget_tdm.web.WebRequester()

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        for format_name in [
            doiget_tdm.format.FormatName.XML,
            doiget_tdm.format.FormatName.PDF,
        ]:

            link = upath.UPath(
                f"https://www.tandfonline.com/doi/{format_name.value}/{fulltext.doi}"
            )

            source = doiget_tdm.source.Source(
                acq_func=self.acquire,
                link=link,
                format_name=format_name,
                encrypt=False,
            )

            fulltext.formats[format_name].sources = [source]

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if (
            self.settings.valid_hostname is not None
            and self.settings.valid_hostname != doiget_tdm.config.SETTINGS.hostname
        ):
            raise doiget_tdm.errors.InvalidHostnameError()

        response = self.session.get(url=str(source.link))

        return response.content