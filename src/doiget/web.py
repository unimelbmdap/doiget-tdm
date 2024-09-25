"""
Make web requests with rate limiting and retrying.
"""

import collections.abc

import requests
import requests_ratelimiter
import pyrate_limiter
import retryhttp


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
        headers: dict[str, object] | None = None,
        max_delay_s: float | None = 60 * 60,
        per_host: bool = True,
        limit_statuses: collections.abc.Iterable[int] = (429, 500),
    ) -> None:

        self._session = requests_ratelimiter.LimiterSession(
            limiter=limiter,
            max_delay=max_delay_s,
            per_host=per_host,
            limit_statuses=limit_statuses,
            headers=headers,
        )

    @retryhttp.retry(max_attempt_number=10)  # type: ignore[misc]
    def get(self, url: str) -> requests.Response:
        return self._session.get(url=url)
