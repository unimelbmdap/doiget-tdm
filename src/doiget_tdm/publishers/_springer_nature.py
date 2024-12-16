from __future__ import annotations

import xml.dom.minidom
import logging

import pydantic
import pydantic_settings

import pyrate_limiter

import upath

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.errors
import doiget_tdm.metadata


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

    api_base_url: str | None = None
    api_key: pydantic.SecretStr | None = None
    api_suffix: pydantic.SecretStr | None = None

    n_requests_per_day: int = 500

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_SPRINGER_NATURE_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class SpringerNature(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="297")

    def __init__(self) -> None:

        self.settings = Settings()

        self.is_configured = all(
            (
                self.settings.api_base_url is not None,
                self.settings.api_key is not None,
                self.settings.api_suffix is not None,
            )
        )

        if not self.is_configured:
            LOGGER.warning("Handler for Springer-Nature is not configured")

        limiter = pyrate_limiter.Limiter(
            pyrate_limiter.RequestRate(
                limit=self.settings.n_requests_per_day,
                interval=60 * 60 * 24,
            ),
        )

        self.session = doiget_tdm.web.WebRequester(
            limiter=limiter
        )

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        # can't set any sources if the API is not configured
        if not self.is_configured:
            return

        # we have already narrowed from the above, but type checker doesn't know that
        assert self.settings.api_key is not None
        assert self.settings.api_suffix is not None

        format_name = doiget_tdm.format.FormatName.XML

        link = upath.UPath(
            f"{self.settings.api_base_url}?q=doi:{fulltext.doi}&"
            + f"api_key={self.settings.api_key.get_secret_value()}/"
            + self.settings.api_suffix.get_secret_value()
        )

        source = doiget_tdm.source.Source(
            acq_func=self.acquire,
            link=link,
            format_name=format_name,
            encrypt=False,
        )

        fulltext.formats[format_name].sources = [source]

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        response = self.session.get(url=str(source.link))

        dom = xml.dom.minidom.parseString(response.content.decode())

        # the response includes stuff about the query, potential for
        # multiple articles, etc.
        articles = dom.getElementsByTagName("article")

        if len(articles) == 0:
            raise doiget_tdm.errors.ValidationError()

        (article,) = articles

        bodies = article.getElementsByTagName("body")

        if len(bodies) == 0:
            raise doiget_tdm.errors.ValidationError()

        (body,) = bodies

        if len(body.childNodes) == 0:
            raise doiget_tdm.errors.ValidationError()

        return article.toxml(encoding="utf-8")
