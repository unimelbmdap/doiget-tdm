"""
Handles the command-line interface (CLI).
"""

from __future__ import annotations

import argparse
import pathlib
import logging
import sys

import doiget


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

    metadata_parser = subparsers.add_parser(
        "metadata",
        help="Download the metadata from CrossRef for the DOIs",
    )

    fulltext_parser = subparsers.add_parser(
        "fulltext",
        help="Download the fulltext for the DOIs",
    )

    acquire_parser = subparsers.add_parser(
        "acquire",
        help="Download the metadata and fulltext for the DOIs",
    )

    for subparser in [metadata_parser, fulltext_parser, acquire_parser]:

        subparser.add_argument(
            "--start-from",
            help="Begin processing the provided DOIs from this number",
            required=False,
            default=1,
            type=int,
        )

    for subparser in [metadata_parser, fulltext_parser, acquire_parser]:

        subparser.add_argument(
            "dois",
            nargs="*",
            help="Either a sequence of DOIs or the path to a file containing DOIs",
        )

    for subparser in [get_dois_parser]:
        subparser.add_argument(
            "--output-path",
            type=pathlib.Path,
            required=True,
            help="Path to write the output",
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

    elif args.command in [
        "metadata",
        "fulltext",
        "acquire",
    ]:
        pass

    else:
        raise ValueError(f"Unexpected command: {args.command}")
