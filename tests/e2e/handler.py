"""The handler type of the web servers of the e2e tier.

CERVER_TEST_HANDLER=threads|events picks it, like in the tests of cerver: a thread of the thpool for
each connection (the default), or the event loops. The tier runs once with each one.
"""

import os

from cerver import CERVER_HANDLER_TYPE_EVENTS
from cerver import CERVER_HANDLER_TYPE_THREADS

HANDLER_VARIABLE = "CERVER_TEST_HANDLER"
HANDLER_EVENTS = "events"

def handler_type () -> int:
	"""Returns the handler type that the run of the suite asked for."""
	events = (os.environ.get (HANDLER_VARIABLE) == HANDLER_EVENTS)

	return CERVER_HANDLER_TYPE_EVENTS if (events) else CERVER_HANDLER_TYPE_THREADS
