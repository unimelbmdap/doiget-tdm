import logging

import requests.utils
import pyrate_limiter

import doiget
import doiget.web

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())

POLITE_POOL_WARNED = False

class CrossRefWebAPI:

    def __init__(self) -> None:

        self.base_url = "https://api.crossref.org/"

        self._session = doiget.web.WebRequester(
            headers={"User-Agent": self.user_agent},
        )

    @property
    def user_agent(self) -> str:

        lib_name = f"doiget/{doiget.__version__} ({doiget._project_url}"

        if (email := doiget.config.SETTINGS.email_address) is not None:
            lib_name += f"; mailto:{email}"
        else:
            global POLITE_POOL_WARNED
            if not POLITE_POOL_WARNED:
                LOGGER.warning(
                    "Email address not configured; unable to use CrossRef polite pool"
                )
                POLITE_POOL_WARNED = True

        lib_name += ")"

        requests_ua = requests.utils.default_headers()["User-Agent"]

        lib_name += f" {requests_ua}"

        return lib_name

    def get_rate_limit(self, test_url: str) -> pyrate_limiter.Limiter:

        default_limit = pyrate_limiter.Limiter(
            pyrate_limiter.RequestRate(
                limit=50,
                interval=1
            )
        )

        default_msg = "Rate limit could not be identified; using defaults"

        try:
            response = self._session.get(url=test_url)
        except Exception:
            LOGGER.warning(default_msg)
            return default_limit

        if (
            "x-ratelimit-limit" not in response.headers
            or "x-ratelimit-interval" not in response.headers
        ):
            LOGGER.warning(default_msg)
            return default_limit

        n_calls = int(response.headers["x-ratelimit-limit"])
        period_s = int(response.headers["x-ratelimit-interval"][:-1])

        limit = pyrate_limiter.Limiter(
            pyrate_limiter.RequestRate(
                limit=n_calls,
                interval=period_s
            )
        )

        LOGGER.info(
            f"Set CrossRef rate limits to {n_calls} calls per {period_s} s"
        )

        return limit
