"""Runs a cerver from the main thread of Python until SIGINT or SIGTERM."""

import signal
import threading

from .cerver import cerver_start, cerver_shutdown, cerver_teardown

__all__ = [
	"CERVER_RUN_STOP_SIGNALS", "CERVER_RUN_POLL_SECONDS",
	"cerver_run"
]

CERVER_RUN_STOP_SIGNALS = (signal.SIGINT, signal.SIGTERM)

# how often the waiting thread checks that cerver_start () is still running
CERVER_RUN_POLL_SECONDS = 1

def cerver_run_start (cerver: int, result: list) -> None:
	"""Runs cerver_start () and keeps its result."""
	result.append (cerver_start (cerver))

def cerver_run_wait (stopped: threading.Event, thread: threading.Thread) -> None:
	"""Waits for a stop signal, or for cerver_start () to return by itself (it failed to start)."""
	while ((not stopped.wait (CERVER_RUN_POLL_SECONDS)) and thread.is_alive ()):
		pass

def cerver_run (cerver: int) -> int:
	"""Starts the cerver in a thread and waits in the calling thread for SIGINT or SIGTERM.

	A cerver started in the main thread only stops when the signal interrupts its accept (),
	because Python runs a handler only when the main thread returns to the interpreter: a
	signal that arrives while the cerver starts is lost. Here Python handles the signal in
	the calling thread and stops the cerver with cerver_shutdown (), that also cancels a start
	that has not happened yet, and then cerver_teardown ().

	It must be called from the main thread (signal.signal ()), and the previous handlers are
	restored before it returns. The caller releases the rest after it (cerver_end ()).

	Args:
		cerver: The cerver to run.

	Returns:
		0 when the cerver started, stopped and was released without errors.
	"""
	stopped = threading.Event ()
	previous = {
		number: signal.signal (number, lambda signum, frame: stopped.set ())
		for number in CERVER_RUN_STOP_SIGNALS
	}

	result = []
	thread = threading.Thread (target=cerver_run_start, args=(cerver, result), daemon=True)
	thread.start ()

	cerver_run_wait (stopped, thread)

	shutdown = cerver_shutdown (cerver)
	thread.join ()
	teardown = cerver_teardown (cerver)

	# None is a handler that was not installed from python, it can not be restored
	for number, handler in previous.items ():
		if (handler is not None):
			signal.signal (number, handler)

	return result[0] | shutdown | teardown
