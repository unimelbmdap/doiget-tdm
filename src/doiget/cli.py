"""
Handles the command-line interface (CLI).
"""

from __future__ import annotations

import argparse
import pathlib
import logging
import sys

import doiget
import doiget.acquire


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def main() -> None:

    parser = setup_parser()

    parsed_args = parser.parse_args()

    try:
        run(args=parsed_args)
    except Exception as err:
        print(err)
        sys.exit(1)


def setup_parser() -> argparse.ArgumentParser:

    parser = argparse.ArgumentParser(
        description="Download metadata and full-text for articles given their DOIs.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    _ = subparsers.add_parser(
        "show-config",
        help="Show configuration settings",
    )

    get_dois_parser = subparsers.add_parser(
        "get-dois",
        help="Get the DOIs matching query and filter criteria",
    )

    get_dois_parser.add_argument(
        "--query-path",
        type=pathlib.Path,
        required=True,
        help="Path to a query specification (in JSON format)",
    )

    get_dois_parser.add_argument(
        "--output-path",
        type=pathlib.Path,
        required=True,
        help="Path to write the output",
    )

    acquire_parser = subparsers.add_parser(
        "acquire",
        help="Download the metadata and fulltext for the DOIs",
    )

    acquire_parser.add_argument(
        "--only-member_id",
        help="Only acquire from DOIs with this member ID",
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
        nargs="+",
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
        run_show_config(args=args)

    elif args.command == "get-dois":
        run_get_dois(args=args)

    elif args.command == "acquire":
        run_acquire(args=args)

    else:
        raise ValueError(f"Unexpected command: {args.command}")


def run_show_config(args: argparse.Namespace) -> None:
    doiget.SETTINGS.print()


def run_get_dois(args: argparse.Namespace) -> None:
    pass


def run_acquire(args: argparse.Namespace) -> None:

    dois = doiget.doi.form_dois_from_input(raw_input=args.dois)

    only_member_id = (
        doiget.metadata.MemberID(id_=args.only_member_id)
        if args.only_member_id is not None
        else None
    )

    doiget.acquire.run(
        dois=dois,
        only_metadata=args.only_metadata,
        start_from=args.start_from,
        only_member_id=only_member_id,
    )
