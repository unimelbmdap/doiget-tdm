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

import rich
import rich.table

import doiget.doi
import doiget.format
import doiget.data


StatusRow = dataclasses.make_dataclass(
    "StatusRow",
    [
        ("doi", str),
        ("has_metadata", bool),
        ("member_id", str),
        ("publisher_name", str),
        ("has_fulltext", bool),
    ]
    + [
        (f"has_fulltext_{fmt.name}", bool)
        for fmt in doiget.SETTINGS.format_preference_order
    ]
    + [
        ("local_dir", str),
    ]
    + [
        (f"fulltext_src_{fmt.name}", bool)
        for fmt in doiget.SETTINGS.format_preference_order
    ],
)


def convert_work_to_status_row(
    work: doiget.Work
) -> object:  # can't type hint dynamically-created dataclasses

    doi = str(work.doi)
    has_metadata = work.metadata.exists

    try:
        member_id = str(work.metadata.member_id)
    except ValueError:
        member_id = ""

    try:
        publisher_name = work.metadata.publisher_name
    except ValueError:
        publisher_name = ""

    has_fulltext = False

    has_fulltext_fmt = {
        f"has_fulltext_{fmt_name.name}": fmt.exists
        for (fmt_name, fmt) in work.fulltext.formats.items()
    }

    has_fulltext = any(
        fulltext_fmt_exists for fulltext_fmt_exists in has_fulltext_fmt.values()
    )

    local_dir = str(work.path)

    fulltext_src = {
        f"fulltext_src_{fmt_name.name}": convert_fmt_to_sources(fmt=fmt)
        for (fmt_name, fmt) in work.fulltext.formats.items()
    }

    return StatusRow(
        doi=doi,
        has_metadata=has_metadata,
        member_id=member_id,
        publisher_name=publisher_name,
        has_fulltext=has_fulltext,
        local_dir=local_dir,
        **has_fulltext_fmt,
        **fulltext_src,
    )


def convert_fmt_to_sources(
    fmt: doiget.format.Format
) -> str:

    if fmt.sources is None:
        return ""

    src = "; ".join(str(src.link) for src in fmt.sources)

    return src


def run(
    dois: typing.Sequence[doiget.doi.DOI] | None,
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

    n = 0
    n_with_metadata = 0
    n_with_fulltext = 0

    n_with_format: collections.Counter[tuple[doiget.format.FormatName, ...]] = (
        collections.Counter()
    )

    n_with_best_format: collections.Counter[doiget.format.FormatName | None] = (
        collections.Counter()
    )

    n_per_member: collections.Counter[doiget.metadata.MemberID] = (
        collections.Counter()
    )

    member_names: collections.defaultdict[doiget.metadata.MemberID, set[str]] = (
        collections.defaultdict(set)
    )

    handle = (
        output_path.open("w", newline="")
        if output_path is not None
        else None
    )

    try:

        for work in doiget.data.iter_unsorted_works():

            n_with_metadata += int(work.metadata.exists)

            if work.metadata.exists:

                member_id = work.metadata.member_id

                n_per_member[member_id] += 1

                member_names[member_id] |= {work.metadata.publisher_name}

            n += 1

            work.fulltext.set_sources()

            has_formats = {
                fmt: work.fulltext.formats[fmt].exists
                for fmt in doiget.SETTINGS.format_preference_order
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


def format_formats(
    n_with_format: collections.Counter[tuple[doiget.format.FormatName, ...]],
) -> rich.table.Table:

    table = rich.table.Table(
        title="DOIs with full-text formats",
    )

    table.add_column("Format(s)")
    table.add_column("Count")

    for (fmts, count) in n_with_format.items():
        table.add_row(
            " + ".join([fmt.name for fmt in fmts]),
            str(count),
        )

    return table


def format_best_format(
    n_with_best_format: collections.Counter[doiget.format.FormatName | None],
) -> rich.table.Table:

    table = rich.table.Table(
        title="Best available format count",
    )

    for fmt in doiget.format.FormatName:
        table.add_column(fmt.name)

    table.add_column("-")

    row = [
        str(n_with_best_format[fmt])
        for fmt in doiget.format.FormatName
    ] + [str(n_with_best_format[None])]

    table.add_row(*row)

    return table


def format_publisher_info(
    n_per_member: collections.Counter[doiget.metadata.MemberID],
    member_names: collections.defaultdict[doiget.metadata.MemberID, set[str]],
) -> rich.table.Table:

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




