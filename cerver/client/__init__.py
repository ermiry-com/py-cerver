"""A client that connects to a cerver: the client, its connections, its events, its errors and its files.

The connections and the packets are shared with the cerver, they are in cerver.core.
"""

from . import client, connections, errors, events, files

from .client import *
from .connections import *
from .errors import *
from .events import *
from .files import *

__all__ = client.__all__ + connections.__all__ + errors.__all__ + events.__all__ + files.__all__
