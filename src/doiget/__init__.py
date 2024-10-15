
import sys

try:
    import doiget.config
except Exception as err:
    print(err)
    sys.exit(1)

import doiget.log

__version__ = "0.1"
_project_url = "https://github.com/djmannion/doiget"

doiget.log.setup_logging()

SETTINGS = doiget.config.SETTINGS

from doiget.doi import DOI
from doiget.work import Work
import doiget.publishers
