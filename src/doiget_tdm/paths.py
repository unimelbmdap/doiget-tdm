import typing

import doiget_tdm


def run_show_doi_data_path(dois: typing.Sequence[doiget_tdm.DOI]) -> None:

    for doi in dois:
        work = doiget_tdm.Work(doi=doi)
        print(f"{doi}: {work.path}")
