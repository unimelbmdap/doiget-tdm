"""
Collects information on items in the data directory, or a subset thereof,
and produces a summary.
"""

from __future__ import annotations

import pathlib
import typing
import collections
import contextlib
import functools
import io
import dataclasses
import enum

import polars as pl

import rich
import rich.table

import doiget_tdm.doi
import doiget_tdm.format
import doiget_tdm.data


SCHEMA: pl.Schema = pl.Schema(
    schema=(
        {
            "doi": pl.String(),
            "doi_quoted": pl.String(),
            "has_metadata": pl.Boolean(),
            "member_id": pl.Categorical(),
            "publisher_name": pl.Categorical(),
            "has_fulltext": pl.Boolean(),
            "journal_name": pl.Categorical(),
            "title": pl.String(),
            "published_date": pl.Date(),
        }
        | {
            f"has_fulltext_{fmt.name}": pl.Boolean()
            for fmt in doiget_tdm.format.FormatName
        }
    ),
)


StatusRow = dataclasses.make_dataclass(
    cls_name="StatusRow",
    fields=SCHEMA.to_python().items(),
    repr=False,
    eq=False,
    frozen=True,
    slots=True,
)


def convert_work_to_status_row(
    work: doiget_tdm.Work
) -> object:  # can't type hint dynamically-created dataclasses

    doi = str(work.doi)
    doi_quoted = work.doi.quoted

    has_metadata = work.metadata.exists

    member_id = (
        str(work.metadata.member_id)
        if has_metadata
        else None
    )

    publisher_name = (
        work.metadata.publisher_name
        if has_metadata
        else None
    )

    title = (
        work.metadata.title
        if has_metadata
        else None
    )

    journal_name = (
        work.metadata.journal_name
        if has_metadata
        else None
    )

    published_date = (
        work.metadata.published_date
        if has_metadata
        else None
    )

    has_fulltext_fmt = {
        f"has_fulltext_{fmt_name.name}": fmt.exists
        for (fmt_name, fmt) in work.fulltext.formats.items()
    }

    has_fulltext = any(
        fulltext_fmt_exists for fulltext_fmt_exists in has_fulltext_fmt.values()
    )

    return StatusRow(
        doi=doi,
        doi_quoted=doi_quoted,
        has_metadata=has_metadata,
        member_id=member_id,
        publisher_name=publisher_name,
        journal_name=journal_name,
        title=title,
        has_fulltext=has_fulltext,
        published_date=published_date,
        **has_fulltext_fmt,
    )


def run(
    dois: typing.Sequence[doiget_tdm.doi.DOI] | None,
    output_path: pathlib.Path | None,
) -> None:
    """
    Produce a status summary for the data directory.

    Parameters
    ----------
    dois
        Set of DOIs to constrain the summary.
    output_path
        File to write a detailed summary (in CSV format).

    """

    df = get_df(dois=dois)

    formats_table = get_formats_table(df=df)

    rich.print(formats_table)

    if output_path is not None:

        writers = {
            ".csv": df.write_csv,
            ".json": df.write_json,
            ".xlsx": df.write_excel,
            ".parquet": df.write_parquet,
            ".pqt": df.write_parquet,
        }

        try:
            writer = writers[output_path.suffix]
        except KeyError:
            msg = f"Invalid output path suffix '{output_path.suffix}'"
            raise ValueError(msg)

        writer(output_path)  # type: ignore [operator]


def old():


    n = 0
    n_with_metadata = 0
    n_with_fulltext = 0

    n_with_format: collections.Counter[tuple[doiget_tdm.format.FormatName, ...]] = (
        collections.Counter()
    )

    n_with_best_format: collections.Counter[doiget_tdm.format.FormatName | None] = (
        collections.Counter()
    )

    n_per_member: collections.Counter[doiget_tdm.metadata.MemberID] = (
        collections.Counter()
    )

    member_names: collections.defaultdict[doiget_tdm.metadata.MemberID, set[str]] = (
        collections.defaultdict(set)
    )

    handle = (
        output_path.open("w", newline="")
        if output_path is not None
        else None
    )

    try:

        for work in doiget_tdm.data.iter_unsorted_works():

            n_with_metadata += int(work.metadata.exists)

            if work.metadata.exists:

                member_id = work.metadata.member_id

                n_per_member[member_id] += 1

                member_names[member_id] |= {work.metadata.publisher_name}

            n += 1

            work.fulltext.set_sources()

            has_formats = {
                fmt: work.fulltext.formats[fmt].exists
                for fmt in doiget_tdm.SETTINGS.format_preference_order
            }

            has_fulltext = any([has_format for has_format in has_formats.values()])

            n_with_fulltext += int(has_fulltext)

            for (fmt, has_fmt) in has_formats.items():

                if has_fmt:
                    n_with_best_format[fmt] += 1
                    break

            else:
                n_with_best_format[None] += 1

            fulltext_fmts = tuple(
                fmt
                for (fmt, has_format) in has_formats.items()
                if has_format and fmt is not None
            )

            if fulltext_fmts:
                n_with_format[fulltext_fmts] += 1

            row = convert_work_to_status_row(work=work)

            row_dict = dataclasses.asdict(row)  # type: ignore[call-overload]

    except Exception as err:

        # if there has been an exception, don't leave a half-written file
        # hanging around

        if handle is not None:
            handle.close()
        if output_path is not None:
            output_path.unlink()

        raise err

    else:
        if handle is not None:
            handle.close()

    

    print(n)
    print(n_with_metadata)
    print(n_with_format)

    pub_info = format_publisher_info(
        n_per_member=n_per_member,
        member_names=member_names,
    )

    rich.print(pub_info)

    best_format_info = format_best_format(
        n_with_best_format=n_with_best_format,
    )

    rich.print(best_format_info)

    format_info = format_formats(
        n_with_format=n_with_format,
    )

    rich.print(format_info)

    print(n)
    print(n_with_metadata)
    print(n_with_fulltext)


def get_formats_table(
    df: pl.DataFrame,
) -> rich.table.Table:

    with_fulltext = df.filter(pl.col("has_fulltext"))

    cols = [
        f"has_fulltext_{fmt.name}"
        for fmt in doiget_tdm.SETTINGS.format_preference_order
    ]

    def row_func(row: tuple[bool, ...]) -> str:
        return " + ".join(
            sorted(
                {
                    fmt.name
                    for (fmt, has_fmt) in zip(
                        doiget_tdm.SETTINGS.format_preference_order,
                        row,
                        strict=True,
                    )
                    if has_fmt
                }
            )
        )

    fmt_types = with_fulltext.select(pl.col(*cols)).map_rows(
        function=row_func,
        return_dtype=pl.Categorical(),
    ).rename({"map": "fmt_types"})

    counts = fmt_types.group_by(pl.col("fmt_types")).len()

    table = rich.table.Table(
        title="DOIs with full-text formats",
    )

    table.add_column("Format(s)")
    table.add_column("Count")

    for value in counts.iter_rows():
        table.add_row(*[str(val) for val in value])

    return table


def format_best_format(
    n_with_best_format: collections.Counter[doiget_tdm.format.FormatName | None],
) -> rich.table.Table:

    table = rich.table.Table(
        title="Best available format count",
    )

    for fmt in doiget_tdm.format.FormatName:
        table.add_column(fmt.name)

    table.add_column("-")

    row = [
        str(n_with_best_format[fmt])
        for fmt in doiget_tdm.format.FormatName
    ] + [str(n_with_best_format[None])]

    table.add_row(*row)

    return table


def get_publisher_table(
    df: pl.DataFrame,
) -> rich.table.Table:

    df_with_metadata = (
        df
        .filter(pl.col("has_metadata"))
        .select(pl.col("member_id", "publisher_name"))
    )

    def combine_publisher_names(member_df: pl.DataFrame) -> pl.DataFrame:
        publisher_names (
            member_df
            .select(pl.col("publisher_name"))
            .unique()
            .rows()
        )

    # TODO

    return df_with_metadata



    table = rich.table.Table(
        title="Publishers of DOIs with metadata",
        show_lines=True,
    )

    table.add_column("Member ID")
    table.add_column("Publisher name(s)")
    table.add_column("Count")

    member_ids = sorted(n_per_member)

    for member_id in member_ids:

        names = "\n".join([name for name in sorted(member_names[member_id])])

        table.add_row(str(member_id), names, str(n_per_member[member_id]))

    return table


def iter_work_status(
    dois: typing.Sequence[doiget_tdm.doi.DOI] | None,
) -> typing.Iterable[dict[str, object]]:

    def is_valid(work: doiget_tdm.work.Work) -> bool:
        return dois is None or work.doi in dois

    for work in doiget_tdm.data.iter_unsorted_works(test_if_valid_work=is_valid):

        status_row = convert_work_to_status_row(work=work)

        yield dataclasses.asdict(status_row)  # type: ignore[call-overload]


def get_df(dois: typing.Sequence[doiget_tdm.doi.DOI] | None) -> pl.DataFrame:

    return pl.DataFrame(
        data=iter_work_status(dois=dois),
        schema=SCHEMA,
        orient="row",
    )