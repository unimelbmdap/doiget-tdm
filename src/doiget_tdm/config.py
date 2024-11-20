from __future__ import annotations

import os
import pathlib
import logging
import typing
import datetime
import sys
import enum
import socket

import pydantic
import pydantic_settings

import platformdirs

import rich

import doiget_tdm.format

NAME = "doiget-tdm"


class Platform(enum.Enum):
    WINDOWS = "windows"
    MAC = "mac"
    LINUX = "linux"


PLATFORM = (
    Platform.WINDOWS
    if sys.platform == "win32"
    else Platform.MAC
    if sys.platform == "darwin"
    else Platform.LINUX
)

# because Windows and Mac have the config directory the same as the
# data directory, we need to add an extra subdirectory on those platforms
BASE_CONFIG_DIR_SUFFIX = (
    "config"
    if PLATFORM in (Platform.WINDOWS, Platform.MAC)
    else ""
)

BASE_CONFIG_DIR = (
    platformdirs.user_config_path(appname=NAME, ensure_exists=True)
    / BASE_CONFIG_DIR_SUFFIX
)

BASE_CONFIG_DIR.mkdir(exist_ok=True, parents=True)

DEFAULT_DATA_DIR_SUFFIX = (
    "data"
    if PLATFORM in (Platform.WINDOWS, Platform.MAC)
    else ""
)

DEFAULT_DATA_DIR = (
    platformdirs.user_data_path(
        appname=NAME,
        ensure_exists=True,
    )
    / DEFAULT_DATA_DIR_SUFFIX
)

DEFAULT_DATA_DIR.mkdir(exist_ok=True, parents=True)


class Settings(pydantic_settings.BaseSettings):

    data_dir: pydantic.DirectoryPath = DEFAULT_DATA_DIR

    cache_dir: pydantic.DirectoryPath = platformdirs.user_cache_path(
        NAME,
        ensure_exists=True,
    )

    data_dir_n_groups: int | None = None

    email_address: pydantic.EmailStr | None = None

    encryption_passphrase: pydantic.SecretStr | None = None

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

    crossref_lmdb_path: pathlib.Path | None = None

    format_preference_order: tuple[doiget_tdm.format.FormatName, ...] = (
        tuple(doiget_tdm.format.FormatName)
    )

    skip_remaining_formats: bool = True

    extra_handlers_path: pydantic.DirectoryPath | None = None

    hostname: str = socket.gethostname()

    # level of metadata compression; -1 is default, 0 is no compression,
    # 9 is highest compression (slowest)
    metadata_compression_level: int = -1

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
