import importlib.util
import pathlib
import sys
import logging

import doiget
import doiget.publisher


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def _load_handlers() -> None:

    module_files = sorted(pathlib.Path(__file__).parent.glob("*.py"))

    extra_files = (
        sorted(doiget.SETTINGS.extra_handlers_path.glob("*.py"))
        if doiget.SETTINGS.extra_handlers_path is not None
        else []
    )

    file_types = ["base"] * len(module_files) + ["extra"] * len(extra_files)

    all_files = module_files + extra_files

    for (module_file, file_type) in zip(all_files, file_types, strict=True):

        # ignore __init__.py and any in-progress modules
        if module_file.name.startswith("__"):
            continue

        LOGGER.info(f"Loading the handler {module_file.name} ({file_type})")

        # recipe from the importlib docs
        module_name = f"doiget.publishers.{module_file.name}"

        spec = importlib.util.spec_from_file_location(
            module_name,
            module_file,
        )

        assert spec is not None

        module = importlib.util.module_from_spec(spec)

        assert hasattr(spec, "loader") and spec.loader is not None

        sys.modules[module_name] = module

        spec.loader.exec_module(module)


_load_handlers()
