from __future__ import annotations

import typing

import alive_progress

import doiget.doi
import doiget.work
import doiget.metadata


def run(
    dois: typing.Sequence[doiget.doi.DOI],
    only_metadata: bool,
    start_from: int = 1,
    only_member_id: doiget.metadata.MemberID | None = None,
    show_progress_bar: bool = True,
) -> None:

    n_dois = len(dois)

    progress_bar_disabled = (
        not show_progress_bar
        or n_dois == 1
    )

    with alive_progress.alive_bar(
        total=n_dois,
        disable=progress_bar_disabled,
    ) as progress_bar:

        for doi_num, doi in enumerate(dois, 1):

            if doi_num < start_from:
                progress_bar()
                continue

            process_doi(
                doi=doi,
                only_metadata=only_metadata,
                only_member_id=only_member_id,
            )

            progress_bar()


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



