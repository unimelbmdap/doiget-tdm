from __future__ import annotations

import typing

import doiget.doi
import doiget.work
import doiget.metadata


def run(
    dois: typing.Sequence[doiget.doi.DOI],
    only_metadata: bool,
    start_from: int = 1,
    only_member_id: doiget.metadata.MemberID | None = None,
) -> None:

    n_dois = len(dois)

    for doi_num, doi in enumerate(dois, 1):

        if doi_num < start_from:
            continue

        process_doi(
            doi=doi,
            only_metadata=only_metadata,
            only_member_id=only_member_id,
        )


def process_doi(
    doi: doiget.doi.DOI,
    only_metadata: bool,
    only_member_id: doiget.metadata.MemberID | None = None,
) -> None:

    work = doiget.work.Work(doi=doi)

    if not work.metadata.exists:
        work.metadata.acquire()

    if only_member_id is not None and work.metadata.member_id != only_member_id:
        return

    if not only_metadata:
        work.fulltext.acquire()



