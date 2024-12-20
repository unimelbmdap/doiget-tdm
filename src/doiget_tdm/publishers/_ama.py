from __future__ import annotations

import logging
import typing
import json

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
    api_key: pydantic.SecretStr | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_AMA_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class AMA(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="10")

    def __init__(self) -> None:

        super().__init__()

        self.settings = Settings()

        self.is_configured = self.settings.api_key is not None

        if not self.is_configured:
            LOGGER.warning("Handler for AMA is not configured")

        # requests seem to be filtered by user agent
        headers = {"User-Agent": "Wget/1.21.2"}

        self.session = doiget_tdm.web.WebRequester(headers=headers)

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        # can't set any sources if the API is not configured
        if not self.is_configured:
            return

        # we have already narrowed from the above, but type checker doesn't know that
        assert self.settings.api_key is not None

        # the API only has TXT format
        format_name = doiget_tdm.format.FormatName.TXT

        link = upath.UPath(
            "https://jamanetwork.com/api/contentservices/fulltext/apikey/"
            + f"{self.settings.api_key.get_secret_value()}?doi={fulltext.doi}"
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

        doiget_tdm.errors.check_hostname(valid_hostname=self.settings.valid_hostname)

        web_response = self.session.get(url=str(source.link))

        data = json.loads(web_response.content)

        bad_json_msg = f"Unexpected JSON structure: {data}"

        if "response" not in data:
            raise ValueError(bad_json_msg)

        response = data["response"]

        if response.get("numFound", 0) == 0:
            raise ValueError("No matching data found for DOI")

        if "docs" not in response:
            raise ValueError(bad_json_msg)

        (doc,) = response["docs"]

        if "ArticleText" not in doc:
            raise ValueError(bad_json_msg)

        text = str(doc["ArticleText"])

        return text.encode()
