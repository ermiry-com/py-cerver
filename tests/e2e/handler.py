"""The handler type of the web servers of the e2e tier, and whether they keep their connections.

CERVER_TEST_HANDLER=threads|events picks it, like in the tests of cerver: a thread of the thpool for
each connection (the default), or the event loops. The tier runs once with each one.

The servers of the tier close each connection after its response, also with event loops (that keep
them by default): their clients read each response until the server closes the connection.
CERVER_TEST_KEEP_ALIVE=1 makes a server keep its connections, for the tests of the kept ones.
"""

import os

from cerver import CERVER_HANDLER_TYPE_EVENTS
from cerver import CERVER_HANDLER_TYPE_THREADS
from cerver.http import http_cerver_set_keep_alive

HANDLER_VARIABLE = "CERVER_TEST_HANDLER"
HANDLER_EVENTS = "events"

KEEP_ALIVE_VARIABLE = "CERVER_TEST_KEEP_ALIVE"
KEEP_ALIVE_ENABLED = "1"

# CERVER_TEST_POOLS=1 gives a server a named pool of threads with its routes, and the health and ready routes
POOLS_VARIABLE = "CERVER_TEST_POOLS"
POOLS_ENABLED = "1"

def handler_type () -> int:
	"""Returns the handler type that the run of the suite asked for."""
	events = (os.environ.get (HANDLER_VARIABLE) == HANDLER_EVENTS)

	return CERVER_HANDLER_TYPE_EVENTS if (events) else CERVER_HANDLER_TYPE_THREADS

def keep_alive () -> bool:
	"""Returns whether the server keeps its connections between requests."""
	return os.environ.get (KEEP_ALIVE_VARIABLE) == KEEP_ALIVE_ENABLED

def keep_alive_configure (http_cerver) -> None:
	"""Sets what the HttpCerver of a server of the tier does with its connections."""
	http_cerver_set_keep_alive (http_cerver, keep_alive ())

def pools () -> bool:
	"""Returns whether the server has a named pool of threads and the routes that cerver answers."""
	return os.environ.get (POOLS_VARIABLE) == POOLS_ENABLED
