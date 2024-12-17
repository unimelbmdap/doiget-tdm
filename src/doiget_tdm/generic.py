from __future__ import annotations

import doiget_tdm.web
import doiget_tdm.fulltext
import doiget_tdm.source
import doiget_tdm.publisher


class GenericWebHost:

    def __init__(self) -> None:

        self.session = doiget_tdm.web.WebRequester()

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        def source_check_func(source: doiget_tdm.source.Source) -> bool:

            if not hasattr(self, "source_domain"):
                return True

            return self.source_domain in str(source.link)

        doiget_tdm.publisher.set_sources_from_crossref(
            fulltext=fulltext,
            acq_func=self.acquire,
            encrypt=False,
            source_check_func=source_check_func,
        )

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        response = self.session.get(url=str(source.link))

        return response.content
