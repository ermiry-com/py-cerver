"""The pools of threads of a web server of pycerver and the routes that cerver answers (cerver 2.1b-17).

The server of the tier is started here with CERVER_TEST_POOLS=1: a pool named "slow" with a route in it,
a route in the thpool of the cerver, and the health and ready routes. Each route answers with the name
that the system has for the thread that ran its handler, and cerver names the threads of a thpool after it.

What these tests pin:
- with event loops a route runs in the threads of the pool that it chose, the others in the thpool
- with a thread for each connection the named pool does not start and every route runs in the thpool
- the health and the ready routes are answered by cerver, for a GET and a HEAD of their exact path
"""

import json
import os
import pytest
from pathlib import Path

from e2e.conftest import SERVER_ADDRESS
from e2e.conftest import REQUEST_SECONDS
from e2e.conftest import output
from e2e.conftest import start
from e2e.conftest import stop
from e2e.conftest import wait_listening

import http.client

pytestmark = [pytest.mark.e2e]

SERVER_SCRIPT = Path (__file__).parent / "server.py"

POOLS_PORT = 8089

POOLS_ENVIRONMENT = {"CERVER_TEST_POOLS": "1"}

HANDLER_VARIABLE = "CERVER_TEST_HANDLER"
HANDLER_EVENTS = "events"

# "thpool-<name>-<id>", cut by the system to 15 bytes: the cerver is "pycerver-e2e", its pool "slow"
DEFAULT_THREAD = "thpool-pycerver"
SLOW_THREAD = "thpool-slow-"

FAST_PATH = "/api/pools/fast"
SLOW_PATH = "/api/pools/slow"
HEALTH_PATH = "/health"
READY_PATH = "/ready"

def _events () -> bool:
	return os.environ.get (HANDLER_VARIABLE) == HANDLER_EVENTS

@pytest.fixture (scope="module")
def pooled ():
	process = start (["python3", "-u", str (SERVER_SCRIPT), str (POOLS_PORT)], env=POOLS_ENVIRONMENT)

	if (not wait_listening (process, POOLS_PORT)):
		stop (process)
		pytest.fail (f"the server did not listen:\n{output (process)}")

	yield process

	code = stop (process)

	assert code == 0, f"the server exited {code}:\n{output (process)}"

def _request (method: str, path: str):
	connection = http.client.HTTPConnection (SERVER_ADDRESS, POOLS_PORT, timeout=REQUEST_SECONDS)
	connection.request (method, path)

	response = connection.getresponse ()
	body = response.read ()
	connection.close ()

	return response.status, body

def _thread (path: str) -> str:
	status, body = _request ("GET", path)

	assert status == 200

	return json.loads (body)["thread"]

class TestPools:

	def test_a_route_without_a_pool_runs_in_the_thpool (self, pooled):
		assert _thread (FAST_PATH).startswith (DEFAULT_THREAD)

	def test_a_route_runs_in_the_pool_that_it_chose (self, pooled):
		thread = _thread (SLOW_PATH)

		# only the event loops give each request to the pool of its route
		expected = SLOW_THREAD if (_events ()) else DEFAULT_THREAD

		assert thread.startswith (expected), thread

class TestHealth:

	def test_health (self, pooled):
		status, body = _request ("GET", HEALTH_PATH)

		assert status == 200
		assert body

	def test_health_head (self, pooled):
		status, body = _request ("HEAD", HEALTH_PATH)

		assert status == 200
		assert not body

	def test_ready (self, pooled):
		status, body = _request ("GET", READY_PATH)

		assert status == 200

	def test_another_method_is_a_request_like_any_other (self, pooled):
		status, body = _request ("POST", HEALTH_PATH)

		assert status == 404

	def test_another_path_is_a_request_like_any_other (self, pooled):
		status, body = _request ("GET", HEALTH_PATH + "/more")

		assert status == 404
