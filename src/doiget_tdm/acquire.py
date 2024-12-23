from __future__ import annotations

import typing
import collections.abc

import alive_progress

import doiget_tdm.doi
import doiget_tdm.work
import doiget_tdm.metadata


def run(
    dois: typing.Sequence[doiget_tdm.doi.DOI],
    only_metadata: bool,
    start_from: int = 1,
    only_member_ids: (
        collections.abc.Container[doiget_tdm.metadata.MemberID] | None
    ) = None,
    show_progress_bar: bool = True,
) -> None:

    n_dois = len(dois)

    progress_bar_disabled = not show_progress_bar or n_dois == 1

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
                only_member_ids=only_member_ids,
            )

            progress_bar()


def process_doi(
    doi: doiget_tdm.doi.DOI,
    only_metadata: bool,
    only_member_ids: (
        collections.abc.Container[doiget_tdm.metadata.MemberID] | None
    ) = None,
) -> None:

    work = doiget_tdm.work.Work(doi=doi)

    if not work.metadata.exists:
        work.metadata.acquire()

    if only_member_ids is not None and work.metadata.member_id not in only_member_ids:
        return

    if not only_metadata:
        work.fulltext.acquire()
