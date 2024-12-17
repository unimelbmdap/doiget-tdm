"""
Handles the command-line interface (CLI).
"""

from __future__ import annotations

import argparse
import pathlib
import logging
import sys

import doiget_tdm
import doiget_tdm.acquire
import doiget_tdm.status
import doiget_tdm.paths


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def main() -> None:

    parser = setup_parser()

    parsed_args = parser.parse_args()

    try:
        run(args=parsed_args)
    except Exception as err:
        print(err)
        if parsed_args.debug:
            raise err
        sys.exit(1)


def setup_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="Download metadata and full-text for articles given their DOIs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Print error tracebacks",
    )

    subparsers = parser.add_subparsers(dest="command")

    _ = subparsers.add_parser(
        "show-config",
        help="Show configuration settings",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Show the status of the data directory.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    status_parser.add_argument(
        "--output-path",
        type=pathlib.Path,
        required=False,
        help="Path to write output, in CSV format.",
    )

    status_parser.add_argument(
        "dois",
        nargs="*",  # zero or more
        help="Either a sequence of DOIs or the path to a file containing DOIs",
    )

    acquire_parser = subparsers.add_parser(
        "acquire",
        help="Download the metadata and fulltext for the DOIs",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    acquire_parser.add_argument(
        "--only-member-id",
        help="Only acquire from DOIs with this member ID",
        action="append",
        type=int,
        required=False,
        default=None,
    )

    acquire_parser.add_argument(
        "--only-metadata",
        help="Only acquire the metadata and not the fulltext",
        default=False,
        action=argparse.BooleanOptionalAction,
    )

    acquire_parser.add_argument(
        "--start-from",
        help="Begin processing the provided DOIs from this number",
        required=False,
        default=1,
        type=int,
    )

    acquire_parser.add_argument(
        "dois",
        nargs="+",  # one or more
        help="Either a sequence of DOIs or the path to a file containing DOIs",
    )

    path_parser = subparsers.add_parser(
        "show-doi-data-path",
        help="Show the data path for DOI(s)",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    path_parser.add_argument(
        "dois",
        nargs="+",  # one or more
        help="Either a sequence of DOIs or the path to a file containing DOIs",
    )

    return parser


def run(args: argparse.Namespace) -> None:

    if args.command is None:
        parser = setup_parser()
        parser.print_help()
        return

    LOGGER.debug(f"Running command with arguments: {args}")

    if args.command == "show-config":
        run_show_config()

    elif args.command == "acquire":
        run_acquire(args=args)

    elif args.command == "status":
        run_status(args=args)

    elif args.command == "show-doi-data-path":
        run_show_doi_data_path(args=args)

    else:
        raise ValueError(f"Unexpected command: {args.command}")


def run_show_config() -> None:
    doiget_tdm.SETTINGS.print()


def run_status(args: argparse.Namespace) -> None:

    dois = (
        None
        if len(args.dois) == 0
        else doiget_tdm.doi.form_dois_from_input(raw_input=args.dois)
    )

    doiget_tdm.status.run(
        dois=dois,
        output_path=args.output_path,
    )


def run_acquire(args: argparse.Namespace) -> None:

    dois = doiget_tdm.doi.form_dois_from_input(raw_input=args.dois)

    only_member_ids: list[doiget_tdm.metadata.MemberID] | None

    if args.only_member_id is None:
        only_member_ids = None
    else:
        only_member_ids = [
            doiget_tdm.metadata.MemberID(id_=only_member_id)
            for only_member_id in args.only_member_id
        ]

    doiget_tdm.acquire.run(
        dois=dois,
        only_metadata=args.only_metadata,
        start_from=args.start_from,
        only_member_ids=only_member_ids,
    )

def run_show_doi_data_path(args: argparse.Namespace) -> None:

    dois = doiget_tdm.doi.form_dois_from_input(raw_input=args.dois)

    doiget_tdm.paths.run_show_doi_data_path(dois=dois)
