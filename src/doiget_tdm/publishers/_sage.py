from __future__ import annotations

import datetime
import zoneinfo
import enum
import logging
import typing

import pyrate_limiter

import pydantic_settings

import doiget_tdm.config
import doiget_tdm.publisher
import doiget_tdm.metadata
import doiget_tdm.errors


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class RateLimit(enum.Enum):
    ONE_PER_SIX_S = "one_per_six_s"
    ONE_PER_TWO_S = "one_per_two_s"

    @staticmethod
    def from_current_time() -> RateLimit:

        # sage guidelines:
        # https://journals.sagepub.com/page/policies/text-and-data-mining
        # 1 request every 6 seconds - Monday to Friday between Midnight and
        # Noon in the "America/Los_Angeles" timezone;
        # 1 request every 2 seconds - Monday to Friday between Noon and
        # Midnight in the "America/Los_Angeles" timezone, and all day Saturday
        # and Sunday.

        rate_test_timezone = zoneinfo.ZoneInfo("America/Los_Angeles")

        dt = datetime.datetime.now(tz=rate_test_timezone)

        midnight = datetime.time(0, 0, 0)
        noon = datetime.time(12, 0, 0)

        # 0 is Monday, 5 and 6 are Saturday and Sunday
        is_weekday = dt.weekday() < 5

        use_slower = is_weekday and (midnight <= dt.time() <= noon)

        current_rate_limit = (
            RateLimit.ONE_PER_SIX_S if use_slower else RateLimit.ONE_PER_TWO_S
        )

        return current_rate_limit


RATE_LIMITS: dict[RateLimit, pyrate_limiter.Limiter] = {
    RateLimit.ONE_PER_SIX_S: pyrate_limiter.Limiter(
        pyrate_limiter.RequestRate(
            limit=1,
            interval=6,
        )
    ),
    RateLimit.ONE_PER_TWO_S: pyrate_limiter.Limiter(
        pyrate_limiter.RequestRate(
            limit=1,
            interval=2,
        )
    ),
}


class Settings(pydantic_settings.BaseSettings):

    valid_hostname: str | None = None

    model_config = pydantic_settings.SettingsConfigDict(
        env_prefix="DOIGET_TDM_SAGE_",
        secrets_dir=doiget_tdm.config.BASE_CONFIG_DIR,
        env_file=".env",
        extra="ignore",
    )


@doiget_tdm.publisher.add_publisher
class Sage(doiget_tdm.publisher.Publisher):

    member_id = doiget_tdm.metadata.MemberID(id_="179")

    def __init__(self) -> None:

        super().__init__()

        self.settings = Settings()

        self.sessions: dict[RateLimit, doiget_tdm.web.WebRequester] | None = None

    def initialise(self) -> None:

        self.sessions = {
            rate_limit: doiget_tdm.web.WebRequester(
                limiter=RATE_LIMITS[rate_limit],
            )
            for rate_limit in RateLimit
        }

    def set_sources(self, fulltext: doiget_tdm.fulltext.FullText) -> None:

        def source_check_func(source: doiget_tdm.source.Source) -> bool:
            return "journals.sagepub.com" in str(source.link)

        doiget_tdm.publisher.set_sources_from_crossref(
            fulltext=fulltext,
            acq_func=self.acquire,
            encrypt=False,
            source_check_func=source_check_func,
        )

    def acquire(self, source: doiget_tdm.source.Source) -> bytes:

        if isinstance(source.link, typing.Sequence):
            raise ValueError(f"Unexpected link: {source.link}")

        doiget_tdm.errors.check_hostname(valid_hostname=self.settings.valid_hostname)

        if self.sessions is None:
            self.initialise()

        if self.sessions is None:
            raise ValueError("Error initialising session")

        active_rate_limit = RateLimit.from_current_time()

        session = self.sessions[active_rate_limit]

        response = session.get(url=str(source.link))

        data: bytes = response.content

        return data
