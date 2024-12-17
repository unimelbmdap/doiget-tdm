
import sys

try:
    import doiget_tdm.config
except Exception as err:
    print(err)
    sys.exit(1)

import doiget_tdm.log

__version__ = "0.1"
_project_url = "https://github.com/unimelbmdap/doiget-tdm"

doiget_tdm.log.setup_logging()

SETTINGS = doiget_tdm.config.SETTINGS

from doiget_tdm.doi import DOI  # noqa: E402
from doiget_tdm.work import Work  # noqa: E402
from doiget_tdm.data import iter_unsorted_works  # noqa: E402
import doiget_tdm.publishers  # noqa: E402

__all__ = (
    "DOI",
    "SETTINGS",
    "Work",
    "iter_unsorted_works",
)
