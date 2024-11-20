from __future__ import annotations

import xml.dom.minidom
import xml.parsers.expat

import puremagic

import html5lib

import doiget_tdm.format
import doiget_tdm.errors


def validate_data(
    data: bytes,
    data_format: doiget_tdm.format.FormatName,
) -> bool:
    """
    Use heuristics to validate that data is in an expected format.

    Parameters
    ----------
    data
        The raw data to validate.
    data_format
        The expected data format.

    Returns
    -------
        Whether the validation was successful.

    Raises
    ------
    doiget_tdm.errors.ValidationError
        On a validation error.
    """

    validators = {
        doiget_tdm.format.FormatName.XML: validate_xml,
        doiget_tdm.format.FormatName.PDF: validate_pdf,
        doiget_tdm.format.FormatName.HTML: validate_html,
        doiget_tdm.format.FormatName.TXT: validate_txt,
        doiget_tdm.format.FormatName.TIFF: validate_tiff,
    }

    validator_func = validators[data_format]

    validator_func(data=data)

    return True


def validate_xml(data: bytes) -> None:
    """
    Validates an XML by checking that it has a non-empty `body` tag.

    Parameters
    ----------
    data
        Raw XML data.
    """

    try:
        doc = xml.dom.minidom.parseString(string=data)
    except xml.parsers.expat.ExpatError:
        raise doiget_tdm.errors.ValidationError(
            "Cannot parse into XML"
        ) from None

    _check_for_body(doc=doc)


def validate_html(data: bytes) -> None:
    """
    Validates a HTML by checking that it has a non-empty `body` tag.

    Parameters
    ----------
    data
        Raw HTML data.
    """

    parser = html5lib.HTMLParser(
        strict=True,
        tree=html5lib.getTreeBuilder("dom"),
    )

    try:
        doc = parser.parse(stream=data)
    except html5lib.html5parser.ParseError:
        raise doiget_tdm.errors.ValidationError(
            "Cannot parse into HTML"
        ) from None

    _check_for_body(doc=doc)


def _check_for_body(doc: xml.dom.minidom.Document) -> None:

    bodies = doc.getElementsByTagName(name="body")

    if len(bodies) == 0:
        raise doiget_tdm.errors.ValidationError(
            "No `body` tag found in XML"
        )

    for body in bodies:

        if body.hasChildNodes():
            break

    else:
        raise doiget_tdm.errors.ValidationError(
            "XML `body` has no content"
        )


def validate_txt(data: bytes) -> None:
    """
    Validates a TXT file by checking that it does not successfully
    validate against other file types.

    Parameters
    ----------
    data
        Raw TXT data.
    """

    # validate by testing whether it is any of the others
    for other_func in (
        validate_xml,
        validate_html,
        validate_pdf,
        validate_tiff,
    ):
        try:
            other_func(data=data)
        except doiget_tdm.errors.ValidationError:
            pass
        else:
            msg = f"Data passes validation for {other_func} rather than text"
            raise doiget_tdm.errors.ValidationError(msg)


def validate_pdf(data: bytes) -> None:
    """
    Validates a PDF file by checking for 'magic numbers'.

    Parameters
    ----------
    data
        Raw PDF data.
    """

    try:
        extension = puremagic.from_string(string=data)
    except puremagic.PureError as err:
        msg = f"Data validation error: {err}"
        raise doiget_tdm.errors.ValidationError(msg) from None

    if extension != ".pdf":
        msg = f"Expected PDF, but inferred type {extension}"
        raise doiget_tdm.errors.ValidationError(msg)


def validate_tiff(data: bytes) -> None:
    """
    Validates a TIFF file by checking for 'magic numbers'.

    Parameters
    ----------
    data
        Raw TIFF data.
    """

    try:
        extension = puremagic.from_string(string=data)
    except puremagic.PureError as err:
        msg = f"Data validation error: {err}"
        raise doiget_tdm.errors.ValidationError(msg) from None

    if extension != ".tiff":
        msg = f"Expected TIFF, but inferred type {extension}"
        raise doiget_tdm.errors.ValidationError(msg)
