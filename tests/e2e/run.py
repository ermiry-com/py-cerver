"""The web servers that cerver_run () stops, started by test_run.py as subprocesses.

serve <port>: one cerver that answers GET /api/run until SIGINT or SIGTERM.

race <port>: RACE_ROUNDS cervers in a row, each one stopped by a signal that the process sends to
itself a bit later in every round: from right after cerver_run () installed its handlers, before
the cerver started, to when it already waits in accept (). The process exits 0 only when every
round stopped in time and without errors, a lost signal hangs it.
"""

import os
import signal
import sys
import threading
import time
from ctypes import c_void_p

from cerver import CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_create_web
from cerver import cerver_run
from cerver import cerver_set_handler_type
from cerver import cerver_set_reusable_address_flags
from cerver import cerver_set_thpool_n_threads
from cerver.http import HTTP_STATUS_OK
from cerver.http import http_cerver_get
from cerver.http import http_send_response
from cerver.http.decorators import HttpGroup

SERVER_NAME = b"pycerver-run"
SERVER_THREADS = 2
SERVER_CONNECTION_QUEUE = 16

MODE_SERVE = "serve"
MODE_RACE = "race"

RACE_ROUNDS = 16
RACE_STEP_SECONDS = 0.002
RACE_POLL_SECONDS = 0.0005

# a signal per round, both of the ones that cerver_run () handles
RACE_SIGNALS = (signal.SIGINT, signal.SIGTERM)

def _create (port: int) -> c_void_p:
	cerver = cerver_create_web (SERVER_NAME, port, SERVER_CONNECTION_QUEUE)
	cerver_set_handler_type (cerver, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_thpool_n_threads (cerver, SERVER_THREADS)
	cerver_set_reusable_address_flags (cerver, True)

	group = HttpGroup.create (http_cerver_get (cerver), "api")

	@group.get ("run")
	def run_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, {"run": True})

	return cerver

def _serve (port: int) -> int:
	return cerver_run (_create (port))

def _signal_later (number: int, original, delay: float) -> None:
	"""Waits until cerver_run () replaced the handler of the signal, then sends it after the delay."""
	while (signal.getsignal (number) is original):
		time.sleep (RACE_POLL_SECONDS)

	time.sleep (delay)
	os.kill (os.getpid (), number)

def _race_round (port: int, round_index: int) -> int:
	number = RACE_SIGNALS[round_index % len (RACE_SIGNALS)]

	sender = threading.Thread (
		target=_signal_later,
		args=(number, signal.getsignal (number), round_index * RACE_STEP_SECONDS),
		daemon=True
	)

	sender.start ()

	result = cerver_run (_create (port))
	sender.join ()

	return result

def _race (port: int) -> int:
	result = 0
	for round_index in range (RACE_ROUNDS):
		result |= _race_round (port + round_index, round_index)

	return result

def main (mode: str, port: int) -> int:
	return _race (port) if (mode == MODE_RACE) else _serve (port)

if __name__ == "__main__":
	sys.exit (main (sys.argv[1], int (sys.argv[2])))
