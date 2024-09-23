import logging

import doiget.config


def setup_logging() -> None:

    root_logger = logging.getLogger()
    root_logger.setLevel(
        min(
            doiget.config.SETTINGS.log_level,
            doiget.config.SETTINGS.file_log_level,
        )
    )

    fmt = "%(asctime)s :: %(levelname)s :: %(message)s :: (%(pathname)s, %(lineno)d)"
    formatter = logging.Formatter(fmt=fmt)

    # handler for the screen
    screen_handler = logging.StreamHandler()
    screen_handler.setLevel(doiget.config.SETTINGS.log_level)
    screen_handler.setFormatter(formatter)

    # handler for the file
    file_handler = logging.FileHandler(filename=doiget.config.SETTINGS.log_file)
    file_handler.setLevel(doiget.config.SETTINGS.file_log_level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(screen_handler)
    root_logger.addHandler(file_handler)
