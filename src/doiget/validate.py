from __future__ import annotations


import puremagic

import doiget.format


def validate_data(
    data: bytes,
    data_format: doiget.format.FormatName,
) -> None:

    validators = {
        doiget.format.FormatName.XML: validate_xml,
        doiget.format.FormatName.PDF: validate_pdf,
        doiget.format.FormatName.HTML: validate_html,
        doiget.format.FormatName.TXT: validate_txt,
        doiget.format.FormatName.TIFF: validate_tiff,
    }

    validator_func = validators[data_format]

    validator_func(data=data)


def validate_xml(data: bytes) -> None:
    pass


def validate_html(data: bytes) -> None:
    pass


def validate_txt(data: bytes) -> None:
    pass


def validate_pdf(data: bytes) -> None:

    extension = puremagic.from_string(string=data)

    if extension != ".pdf":
        msg = f"Expected PDF, but inferred type {extension}"
        raise ValueError(msg)


def validate_tiff(data: bytes) -> None:

    extension = puremagic.from_string(string=data)

    if extension != ".tiff":
        msg = f"Expected TIFF, but inferred type {extension}"
        raise ValueError(msg)
