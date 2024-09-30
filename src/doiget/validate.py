
import doiget.format


def validate_data(
    data_format: doiget.format.FormatName,
    data: bytes,
) -> None:

    pass


def validate_xml(data: bytes) -> None:
    pass


def validate_pdf(data: bytes) -> None:

    extension = puremagic.from_string(string=data)

    if extension != ".pdf":
        msg = f"Expected PDF, but inferred type {extension}"
        raise ValueError(msg)
