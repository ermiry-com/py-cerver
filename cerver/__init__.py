"""pycerver: a Python wrapper of the cerver framework.

The top level has the cerver itself (cerver.core) and the versions; the other parts are
subpackages: cerver.http, cerver.client, cerver.games, cerver.network, cerver.threads,
cerver.utils and cerver.types.
"""

from . import callbacks, core, lib
from . import client, games, http, network, threads, types, utils

from .version import __all__ as version_names
from .version import PYCERVER_VERSION

from .core import *
from .version import *

__version__ = PYCERVER_VERSION

__all__ = core.__all__ + version_names + ["__version__"]
