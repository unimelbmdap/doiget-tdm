
import logging

import requests.exceptions

import tenacity


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


def get_retry_controller(
    logger: logging.Logger
) -> tenacity.Retrying:

    return tenacity.Retrying(
        wait=tenacity.wait.wait_fixed(wait=10),
        after=tenacity.after_log(logger=logger, log_level=logging.WARNING),
        retry=(
            tenacity.retry_if_exception_type(OSError)
            | tenacity.retry_if_exception_type(BlockingIOError)
        ),
    )
