from __future__ import annotations

import logging

import upath

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.errors
import doiget_tdm.metadata


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


@doiget_tdm.publisher.add_publisher
class Frontiers(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="1965")

    def __init__(self) -> None:

        self.session = doiget_tdm.web.WebRequester()

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        for format_name in [
            doiget_tdm.format.FormatName.XML,
            doiget_tdm.format.FormatName.PDF,
        ]:

            # https://helpcenter.frontiersin.org/s/article/Article-URLs-and-File-Formats
            link = upath.UPath(
                f"https://journal.frontiersin.org/article/{fulltext.doi}/{format_name.value}"
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

        return response.content
