import logging

import requests.utils
import pyrate_limiter

import doiget_tdm
import doiget_tdm.web

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class CrossRefWebAPI:

    def __init__(self) -> None:
        """
        Interface to the CrossRef web API.
        """

        self.polite_pool_warned = False

        self.base_url = "https://api.crossref.org/"

        self._session = doiget_tdm.web.WebRequester(
            headers={"User-Agent": self.user_agent},
        )

        self.default_limit = pyrate_limiter.Limiter(
            pyrate_limiter.RequestRate(limit=50, interval=1)
        )

    @property
    def user_agent(self) -> str:
        """
        Value to send as the "User-Agent" header.
        """

        lib_name = f"doiget-tdm/{doiget_tdm.__version__} ({doiget_tdm._project_url}"

        if (email := doiget_tdm.config.SETTINGS.email_address) is not None:
            lib_name += f"; mailto:{email}"
        else:
            if not self.polite_pool_warned:
                LOGGER.warning(
                    "Email address not configured; unable to use CrossRef polite pool"
                )
                self.polite_pool_warned = True

        lib_name += ")"

        requests_ua = requests.utils.default_headers()["User-Agent"]

        lib_name += f" {requests_ua}"

        return lib_name

    def get_rate_limit(self) -> pyrate_limiter.Limiter:
        """
        Determine the API rate limits by sending a test request and inspecting
        the response headers.

        Returns
        -------
            A limiter with the settings applied.
        """

        default_msg = "Rate limit could not be identified; using defaults"

        try:
            response = self._session.get(url=self.base_url)
        except Exception:
            LOGGER.warning(default_msg)
            return self.default_limit

        if (
            "x-ratelimit-limit" not in response.headers
            or "x-ratelimit-interval" not in response.headers
        ):
            LOGGER.warning(default_msg)
            return self.default_limit

        n_calls = int(response.headers["x-ratelimit-limit"])
        period_s = int(response.headers["x-ratelimit-interval"][:-1])

        limit = pyrate_limiter.Limiter(
            pyrate_limiter.RequestRate(limit=n_calls, interval=period_s)
        )

        LOGGER.info(f"Set CrossRef rate limits to {n_calls} calls per {period_s} s")

        return limit

    def call(
        self,
        query: str,
    ) -> requests.Response:
        """
        Make a call to the API.

        Parameters
        ----------
        query
            Query string, which is used to form the URL; no leading slash.

        Returns
        -------
            The API response.
        """

        url = f"{self.base_url}{query}"

        response = self._session.get(url=url)

        response.raise_for_status()

        return response
