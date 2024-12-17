"""
Handler for PLoS.

This currently only makes web requests and does not use their public data
file (allofplos.zip).
"""

from __future__ import annotations

import logging

import upath

import doiget_tdm.publisher
import doiget_tdm.web
import doiget_tdm.fulltext
import doiget_tdm.format
import doiget_tdm.source


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


@doiget_tdm.publisher.add_publisher
class PLoS(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="340")

    def __init__(self) -> None:

        self.session = doiget_tdm.web.WebRequester()

        self.warning_printed = False
        self.n_requests = 0

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

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

            link = upath.UPath(
                "https://journals.plos.org/plosone/article/file?id="
                + f"{fulltext.doi}&type={param}"
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

        self.n_requests += 1

        if self.n_requests > 10 and not self.warning_printed:
            LOGGER.warning(
                "Bulk downloading using the PLoS website is discouraged; consider "
                + "investigating the PLoS data file (see "
                + "https://api.plos.org/text-and-data-mining.html)"
            )
            self.warning_printed = True

        return response.content
