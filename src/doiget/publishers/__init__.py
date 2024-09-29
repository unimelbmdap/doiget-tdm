import importlib.util
import pathlib
import sys
import logging

import doiget.publisher  # noqa: F401


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def _load_handlers() -> None:

    module_files = sorted(pathlib.Path(__file__).parent.glob("*.py"))

    for module_file in module_files:

        # ignore __init__.py and any in-progress modules
        if module_file.name.startswith("__"):
            continue

        LOGGER.debug(f"Loading the handler {module_file.name}")

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
