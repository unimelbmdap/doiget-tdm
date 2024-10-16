
import requests.exceptions


class ValidationError(Exception):
    pass


class InvalidHostname(Exception):
    pass


class AcquisitionError(Exception):
    pass


CUSTOM_ERRORS = (ValidationError, InvalidHostname, AcquisitionError)

ACQ_ERRORS = (
    requests.exceptions.RequestException,
    InvalidHostname,
    AcquisitionError,
)
