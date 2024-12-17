from __future__ import annotations

import logging
import pathlib
import typing
import zipfile

import pydantic_settings

import upath

import doiget_tdm.publisher
import doiget_tdm.web
import doiget_tdm.fulltext
import doiget_tdm.format
import doiget_tdm.source


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class Settings(pydantic_settings.BaseSettings):

    allofplos_path: pathlib.Path | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_PLOS_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class PLoS(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="340")

    def __init__(self) -> None:

        self.settings = Settings()

        self.has_allofplos = (
            self.settings.allofplos_path is not None
            and self.settings.allofplos_path.exists()
        )

        self.session = doiget_tdm.web.WebRequester()

        self.warning_printed = False
        self.n_requests = 0

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        if self.has_allofplos:

            link = upath.UPath(f"file:///{fulltext.doi.parts.suffix}.xml")

            file_source = doiget_tdm.source.Source(
                acq_func=self.acquire,
                link=link,
                format_name=doiget_tdm.format.FormatName.XML,
                encrypt=False,
            )

            fulltext.formats[doiget_tdm.format.FormatName.XML].sources = [file_source]

        for format_name in [
            doiget_tdm.format.FormatName.XML,
            doiget_tdm.format.FormatName.PDF,
        ]:

            # https://api.plos.org/text-and-data-mining.html

            param = (
                "printable"
                if format_name is doiget_tdm.format.FormatName.PDF
                else "manuscript"
            )

            web_link = upath.UPath(
                "https://journals.plos.org/plosone/article/file?id="
                + f"{fulltext.doi}&type={param}"
            )

            web_source = doiget_tdm.source.Source(
                acq_func=self.acquire,
                link=web_link,
                format_name=format_name,
                encrypt=False,
            )

            fulltext.formats[format_name].sources.append(web_source)

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if isinstance(source.link, typing.Sequence):
            raise ValueError(f"Unexpected link: {source.link}")

        if source.link.protocol == "file":

            if self.has_allofplos:

                # we know, but the type checker doesn't
                assert self.settings.allofplos_path is not None

                with zipfile.ZipFile(self.settings.allofplos_path) as handle:
                    data = handle.read(source.link.name)

                return data

            else:
                raise ValueError("Cannot acquire from the PLoS data file")

        else:

            response = self.session.get(url=str(source.link))

            self.n_requests += 1

            if self.n_requests > 10 and not self.warning_printed:
                LOGGER.warning(
                    "Bulk downloading using the PLoS website is discouraged; consider "
                    + "investigating the PLoS data file (see "
                    + "https://api.plos.org/text-and-data-mining.html)"
                )
                self.warning_printed = True

            return response.content
