
import requests.exceptions


class ValidationError(Exception):
    pass


class InvalidHostnameError(Exception):
    pass


class AcquisitionError(Exception):
    pass


CUSTOM_ERRORS = (ValidationError, InvalidHostnameError, AcquisitionError)

ACQ_ERRORS = (
    requests.exceptions.RequestException,
    InvalidHostnameError,
    AcquisitionError,
)
