"""cerver_run (): a cerver that is stopped by a signal at any moment of its start, in a subprocess.

Bugs these tests fixed:
- a signal that arrived while a cerver started in the main thread was lost, python ran its
  handler only after cerver_start () returned, and it never returned
- cerver_start () set its running flag without a condition, so a cerver_shutdown () from
  another thread before it was lost too and the cerver kept accepting (cerver 2.0b-60)
"""

import pytest
import signal
import subprocess
from pathlib import Path

from cerver import CERVER_RUN_STOP_SIGNALS
from cerver import cerver_create_web
from cerver import cerver_run

from e2e.conftest import e2e_raw
from e2e.conftest import output
from e2e.conftest import start
from e2e.conftest import stop
from e2e.conftest import wait_listening

pytestmark = [pytest.mark.e2e]

RUN_SCRIPT = Path (__file__).parent / "run.py"

SERVE_PORT = 8091
RACE_PORT = 8200
FAILED_PORT = 8092

FAILED_NAME = b"pycerver-run-failed"
FAILED_CONNECTION_QUEUE = 4

# every round of the race starts and stops a cerver, a lost signal hangs the process
RACE_SECONDS = 64

HTTP_OK_LINE = b"HTTP/1.1 200"

RUN_REQUEST = b"GET /api/run HTTP/1.1\r\nHost: localhost\r\n\r\n"

class TestRun:

	def test_serves_and_stops_with_sigint (self):
		process = start (["python3", "-u", str (RUN_SCRIPT), "serve", str (SERVE_PORT)])

		listening = wait_listening (process, SERVE_PORT)
		response = e2e_raw (RUN_REQUEST, SERVE_PORT) if (listening) else b""
		code = stop (process)

		assert listening, output (process)
		assert response.startswith (HTTP_OK_LINE), output (process)
		assert code == 0, output (process)

	def test_stops_right_after_it_listens (self):
		# the signal of §13: milliseconds after the port listens, the old pattern hung here
		process = start (["python3", "-u", str (RUN_SCRIPT), "serve", str (SERVE_PORT)])

		listening = wait_listening (process, SERVE_PORT)
		code = stop (process)

		assert listening, output (process)
		assert code == 0, output (process)

	def test_stops_with_sigterm (self):
		process = start (["python3", "-u", str (RUN_SCRIPT), "serve", str (SERVE_PORT)])

		listening = wait_listening (process, SERVE_PORT)
		process.send_signal (signal.SIGTERM)
		code = stop (process)

		assert listening, output (process)
		assert code == 0, output (process)

	def test_a_signal_at_any_moment_of_the_start_stops_it (self):
		process = start (["python3", "-u", str (RUN_SCRIPT), "race", str (RACE_PORT)])

		try:
			code = process.wait (timeout=RACE_SECONDS)

		except subprocess.TimeoutExpired:
			process.kill ()
			process.wait ()
			code = None

		assert code == 0, f"the race exited {code}:\n{output (process)}"

	def test_a_cerver_that_fails_to_start_returns_without_a_signal (self):
		# without a handler type cerver_start () fails at once, in this process
		previous = [signal.getsignal (number) for number in CERVER_RUN_STOP_SIGNALS]

		result = cerver_run (cerver_create_web (FAILED_NAME, FAILED_PORT, FAILED_CONNECTION_QUEUE))

		assert result != 0
		assert [signal.getsignal (number) for number in CERVER_RUN_STOP_SIGNALS] == previous
