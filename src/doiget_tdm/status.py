"""
Collects information on items in the data directory, or a subset thereof,
and produces a summary.
"""

from __future__ import annotations

import pathlib
import typing
import dataclasses
import functools
import warnings

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

    publishers_table = get_publisher_table(df=df)
    rich.print(publishers_table)

    formats_table = get_formats_table(df=df)
    rich.print(formats_table)

    best_format_table = get_best_format_table(df=df)
    rich.print(best_format_table)

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
            raise ValueError(msg) from None

        writer(output_path)  # type: ignore [operator]


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

    for value in counts.sort("len").iter_rows():
        table.add_row(*[str(val) for val in value])

    return table


def get_best_format_table(
    df: pl.DataFrame,
) -> rich.table.Table:

    fmt_columns = [
        f"has_fulltext_{fmt.name}"
        for fmt in doiget_tdm.SETTINGS.format_preference_order
    ]

    best_expr: pl.expr.whenthen.Then | pl.expr.whenthen.ChainedThen | None = None

    for fmt_column in fmt_columns:

        (*_, fmt) = fmt_column.split("_")

        if best_expr is None:
            best_expr = pl.when(pl.col(fmt_column)).then(pl.lit(fmt))
        else:
            best_expr = best_expr.when(pl.col(fmt_column)).then(pl.lit(fmt))

    if not isinstance(best_expr, pl.expr.whenthen.ChainedThen):
        raise ValueError()

    best = df.filter(pl.col("has_fulltext")).select(best_expr.alias("best"))

    counts = best.group_by("best").len()

    for curr_fmt in doiget_tdm.format.FormatName:
        if curr_fmt.name not in counts["best"]:
            counts = pl.concat(
                [
                    counts,
                    pl.DataFrame(
                        {"best": curr_fmt.name, "len": 0},
                        schema=counts.schema,
                    ),
                ],
                how="vertical",
            )

    table = rich.table.Table(
        title="Best available format count",
    )

    table.add_column("Format")
    table.add_column("Count")

    for value in counts.sort("len").iter_rows():
        table.add_row(*[str(val) for val in value])

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

        count = member_df.select("member_id").count().item()

        publisher_names = (
            member_df
            .select(pl.col("publisher_name"))
            .unique()
            .rows()
        )

        member_id = member_df.select(pl.first("member_id")).item()

        combined = "; ".join(
            [
                publisher_name
                for publisher_name, in publisher_names
            ]
        )

        return pl.DataFrame(
            {
                "member_id": [member_id],
                "publisher_name": [combined],
                "count": [count],
            }
        )

    names = (
        df_with_metadata
        .group_by("member_id")
        .map_groups(combine_publisher_names)
    )

    table = rich.table.Table(
        title="Publishers of DOIs with metadata",
        show_lines=True,
    )

    table.add_column("Member ID")
    table.add_column("Publisher name(s)")
    table.add_column("Count")

    for value in names.sort(
        "count",
        "publisher_name",
        descending=[True, False],
    ).iter_rows():
        table.add_row(*[str(val) for val in value])

    return table


def iter_works(
    dois: typing.Sequence[doiget_tdm.doi.DOI] | None
) -> typing.Iterable[dict[str, object]]:

    iterator = (
        iter(dois)
        if dois is not None
        else doiget_tdm.data.iter_unsorted_works()
    )

    items_are_works = dois is None

    for item in iterator:

        if items_are_works:
            if not isinstance(item, doiget_tdm.Work):
                raise ValueError()
            work = item

        else:
            if not isinstance(item, doiget_tdm.DOI):
                raise ValueError()
            work = doiget_tdm.Work(doi=item)

        status_row = convert_work_to_status_row(work=work)

        yield dataclasses.asdict(status_row)  # type: ignore[call-overload]


def get_df(dois: typing.Sequence[doiget_tdm.doi.DOI] | None) -> pl.DataFrame:

    warnings.simplefilter("ignore", pl.PerformanceWarningCategoricalRemapping)

    df = pl.DataFrame(
        data=iter_works(dois=dois),
        schema=SCHEMA,
        orient="row",
    )

    return df
