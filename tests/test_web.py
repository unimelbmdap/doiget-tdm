
import time

import pytest

import requests
import requests.exceptions
import tenacity
import requests_ratelimiter
import pyrate_limiter

import doiget.web


def test_init() -> None:
    requester = doiget.web.WebRequester()


def test_get(monkeypatch) -> None:

    requester = doiget.web.WebRequester()

    def mock_get(*args, **kwargs) -> requests.Response:
        return requests.Response()

    monkeypatch.setattr(requester._session, "get", mock_get)

    response = requester.get("https://www.google.com")

    assert isinstance(response, requests.Response)


def test_retry_timeout(monkeypatch) -> None:

    requester = doiget.web.WebRequester(max_retry_attempts=0)

    def mock_get_timeout(*args, **kwargs) -> None:
        raise requests.exceptions.Timeout()

    monkeypatch.setattr(requester._session, "get", mock_get_timeout)

    with pytest.raises(tenacity.RetryError):
        requester.get("https://www.google.com")


def _test_retry_after_timeout(monkeypatch) -> None:

    requester = doiget.web.WebRequester()

    n_attempts = 0

    def mock_get_ok_after_timeout(*args, **kwargs) -> requests.Response:

        nonlocal n_attempts

        n_attempts += 1

        if n_attempts == 1:
            raise requests.exceptions.Timeout()

        return requests.Response()

    monkeypatch.setattr(requester._session, "get", mock_get_ok_after_timeout)

    requester.get("https://www.google.com")

    assert n_attempts == 2
