import logging

import requests.exceptions

import tenacity

import doiget_tdm.config


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


def check_hostname(valid_hostname: str | None) -> None:

    if (
        valid_hostname is not None
        and valid_hostname != doiget_tdm.config.SETTINGS.hostname
    ):
        msg = (
            f"Invalid hostname ({doiget_tdm.config.SETTINGS.hostname}) for request"
            + f"; required hostname is {valid_hostname}"
        )
        raise InvalidHostnameError(msg)


def get_retry_controller(logger: logging.Logger) -> tenacity.Retrying:

    return tenacity.Retrying(
        wait=tenacity.wait.wait_fixed(wait=10),
        after=tenacity.after_log(logger=logger, log_level=logging.WARNING),
        retry=(
            tenacity.retry_if_exception_type(OSError)
            | tenacity.retry_if_exception_type(BlockingIOError)
        ),
    )
