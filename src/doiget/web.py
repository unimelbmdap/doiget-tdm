"""
Make web requests with rate limiting and retrying.
"""

import collections.abc

import requests
import requests_ratelimiter
import pyrate_limiter
import retryhttp  # type: ignore[import-untyped]


DEFAULT_LIMITER = pyrate_limiter.Limiter(
    pyrate_limiter.RequestRate(
        limit=60,
        interval=60,
    ),
)


class WebRequester:

    def __init__(
        self,
        limiter: pyrate_limiter.Limiter = DEFAULT_LIMITER,
        headers: dict[str, str] | None = None,
        max_delay_s: float | None = 60 * 60,
        per_host: bool = False,
        limit_statuses: collections.abc.Iterable[int] = (429, 500),
        max_retry_attempts: int = 10,
    ) -> None:

        self._session = requests_ratelimiter.LimiterSession(
            limiter=limiter,
            max_delay=max_delay_s,
            per_host=per_host,
            limit_statuses=limit_statuses,
        )

        self.max_retry_attempts = max_retry_attempts

        self.retry_wrapper = retryhttp.retry(
            max_attempt_number=self.max_retry_attempts
        )

        if headers is not None:
            self._session.headers = {**self._session.headers, **headers}

    def get(self, url: str) -> requests.Response:

        retry_get = self.retry_wrapper(self._session.get)
        response: requests.Response = retry_get(url=url)

        return response
