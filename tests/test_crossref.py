
import time

import pytest

import requests
import requests.exceptions
import tenacity
import requests_ratelimiter
import pyrate_limiter

import doiget_tdm.config
import doiget_tdm.crossref


def test_rate_limit(monkeypatch) -> None:

    cr = doiget_tdm.crossref.CrossRefWebAPI()

    def mock_get_raise(*args, **kwargs) -> None:
        raise requests.exceptions.RequestException()

    monkeypatch.setattr(cr._session._session, "get", mock_get_raise)

    rate_limit = cr.get_rate_limit()

    (rates,) = rate_limit._rates
    (default_rates,) = cr.default_limit._rates

    assert rates.interval == default_rates.interval
    assert rates.limit == default_rates.limit

    mock_limit = 10
    mock_period = 30

    def mock_get_headers(*args, **kwargs) -> None:
        response = requests.Response()
        response.headers["x-ratelimit-limit"] = str(mock_limit)
        response.headers["x-ratelimit-interval"] = f"{mock_period}s"
        return response

    monkeypatch.setattr(cr._session._session, "get", mock_get_headers)

    rate_limit = cr.get_rate_limit()

    (rates,) = rate_limit._rates

    assert rates.interval == mock_period
    assert rates.limit == mock_limit

    def mock_get_headers_empty(*args, **kwargs) -> None:
        response = requests.Response()
        return response

    monkeypatch.setattr(cr._session._session, "get", mock_get_headers_empty)

    rate_limit = cr.get_rate_limit()

    (rates,) = rate_limit._rates

    assert rates.interval == default_rates.interval
    assert rates.limit == default_rates.limit


def test_call(monkeypatch) -> None:

    cr = doiget_tdm.crossref.CrossRefWebAPI()

    def mock_get_raise(*args, **kwargs) -> None:
        raise requests.exceptions.RequestException()

    monkeypatch.setattr(cr._session._session, "get", mock_get_raise)

    with pytest.raises(requests.exceptions.RequestException):
        cr.call(query="")


    def mock_get_raise_specific(*args, **kwargs) -> None:
        response = requests.Response()
        response.status_code = 404
        return response

    monkeypatch.setattr(cr._session._session, "get", mock_get_raise_specific)

    with pytest.raises(requests.exceptions.HTTPError):
        cr.call(query="")

    def mock_get_ok(*args, **kwargs) -> None:
        response = requests.Response()
        response.status_code = 200
        return response

    monkeypatch.setattr(cr._session._session, "get", mock_get_ok)

    cr.call(query="")


def test_user_agent():

    mock_email = "test@test.com"

    cr = doiget_tdm.crossref.CrossRefWebAPI()

    doiget_tdm.config.SETTINGS.email_address = None

    assert mock_email not in cr.user_agent

    doiget_tdm.config.SETTINGS.email_address = mock_email

    assert f"; mailto:{mock_email}" in cr.user_agent

