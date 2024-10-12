from __future__ import annotations

import typing

import doiget.doi
import doiget.work


def run(
    raw_dois: typing.Sequence[str],
    only_metadata: bool,
    start_from: int = 1,
) -> None:

    dois = doiget.doi.form_dois_from_input(raw_input=raw_dois)

    n_dois = len(dois)

    for doi_num, doi in enumerate(dois, 1):

        if doi_num < start_from:
            continue

        process_doi(
            doi=doi,
            only_metadata=only_metadata,
        )


def process_doi(
    doi: doiget.doi.DOI,
    only_metadata: bool,
) -> None:

    work = doiget.work.Work(doi=doi)

    if not work.metadata.exists:
        work.metadata.acquire()

    if not only_metadata:
        work.fulltext.acquire()



