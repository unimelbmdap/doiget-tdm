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
        nargs="*",
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
        doiget.SETTINGS.print()

    elif args.command == "get-dois":
        pass

    elif args.command == "acquire":
        doiget.acquire.run(
            raw_dois=args.dois,
            only_metadata=args.only_metadata,
            start_from=args.start_from,
        )

    else:
        raise ValueError(f"Unexpected command: {args.command}")
