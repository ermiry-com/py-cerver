"""A worker without HTTP: a loop that takes events from a queue (here in memory, in a service
a list of a store like Redis) and gives them to a worker of cerver, until SIGINT or SIGTERM.

	python3 examples/workers/worker.py
"""

import queue
import signal
import sys
import threading

from cerver import cerver_init, cerver_end
from cerver.threads import Worker
from cerver.utils import cerver_log_success, cerver_log_debug, cerver_log_warning

WORKER_NAME = "events"

# how long the loop waits for an event before it checks if it must stop, in seconds
EVENT_WAIT_SECONDS = 1

EXAMPLE_EVENTS = 8

stopped = threading.Event ()

events = queue.Queue ()

def event_handle (event: dict) -> None:
	"""Runs in the thread of the worker."""
	cerver_log_success (f"Handled event {event['index']} of type {event['type']}")

def stop (signum, frame) -> None:
	stopped.set ()

def main () -> int:
	cerver_init ()

	signal.signal (signal.SIGINT, stop)
	signal.signal (signal.SIGTERM, stop)

	worker = Worker (WORKER_NAME, event_handle)
	worker.start ()

	for index in range (EXAMPLE_EVENTS):
		events.put ({"index": index, "type": "example"})

	while (not stopped.is_set ()):
		try:
			event = events.get (timeout=EVENT_WAIT_SECONDS)
			if (worker.push (event)):
				cerver_log_warning (f"Failed to push event {event['index']}")

		except queue.Empty:
			cerver_log_debug ("Waiting for events...")

	# the job that is running ends before the worker is released
	worker.delete ()

	cerver_end ()

	return 0

if __name__ == "__main__":
	sys.exit (main ())
