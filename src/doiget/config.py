from __future__ import annotations

import os
import pathlib
import logging
import typing
import datetime

import pydantic
import pydantic_settings

import platformdirs

import rich


NAME = "doiget"

BASE_CONFIG_DIR = platformdirs.user_config_path(NAME, ensure_exists=True)


class Settings(pydantic_settings.BaseSettings):

    data_dir: pydantic.DirectoryPath = platformdirs.user_data_path(
        appname=NAME,
        ensure_exists=True,
    )

    data_dir_n_groups: int | None = None

    email_address: pydantic.EmailStr | None = None

    log_level: int | str = logging.WARNING
    file_log_level: int | str = logging.INFO

    # because there could potentially be multiple instances running at the same
    # time (but not initialised in the same second!), append a timestamp to the
    # log file path
    log_file: pathlib.Path = (
        platformdirs.user_log_path(
            NAME,
            ensure_exists=True,
        )
        / (NAME + "_{time}.log")
    )

    quiet: bool = False

    model_config = pydantic_settings.SettingsConfigDict(
        env_file=".env",
        env_prefix=f"{NAME.upper()}_",
        secrets_dir=BASE_CONFIG_DIR,
        extra="ignore",
    )

    def model_post_init(self, __context: typing.Any) -> None:  # noqa: ANN401

        if self.data_dir_n_groups == 0:
            self.data_dir_n_groups = None

        if isinstance(self.log_level, str):
            self.log_level = getattr(logging, self.log_level.upper())

        if isinstance(self.file_log_level, str):
            self.file_log_level = getattr(logging, self.file_log_level.upper())

        if self.email_address is not None:
            os.environ["CR_API_MAILTO"] = self.email_address

        curr_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        self.log_file = self.log_file.with_stem(
            stem=self.log_file.stem.format(time=curr_time)
        )

    def print(self) -> None:

        settings_dict = {"config_dir": BASE_CONFIG_DIR} | self.dict()

        for key, value in settings_dict.items():

            if isinstance(value, pathlib.Path):
                settings_dict[key] = str(value)

            if key in ["log_level", "file_log_level"]:
                settings_dict[key] = logging.getLevelName(value)

        rich.print(settings_dict)


SETTINGS = Settings()
