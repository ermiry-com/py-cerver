"""The connections that a web server of pycerver keeps between requests (cerver 2.1b-16).

The server of the tier is started here with CERVER_TEST_KEEP_ALIVE=1, in the handler type of the run:
with event loops a cerver keeps its connections by default, with threads when it is asked to.

What these tests pin:
- a connection handles more than one request, and its responses do not say "Connection: close"
- a client that asks for the close gets it, with the header in its response
- the requests that a client sends without waiting for their responses are answered in their order
- a connection reaches its limit of requests and says it in its last response
"""

import http.client
import pytest
import socket
from pathlib import Path

from cerver.http import HTTP_CERVER_DEFAULT_KEEP_ALIVE_REQUESTS

from e2e.conftest import REQUEST_SECONDS
from e2e.conftest import RESPONSE_SIZE
from e2e.conftest import SERVER_ADDRESS
from e2e.conftest import output
from e2e.conftest import start
from e2e.conftest import stop
from e2e.conftest import wait_listening

pytestmark = [pytest.mark.e2e]

SERVER_SCRIPT = Path (__file__).parent / "server.py"

KEEP_ALIVE_PORT = 8094

KEEP_ALIVE_ENVIRONMENT = {"CERVER_TEST_KEEP_ALIVE": "1"}

REQUESTS = 8
PIPELINED = 3

JSON_PATH = "/api/e2e/json"

JSON_REQUEST = b"GET /api/e2e/json HTTP/1.1\r\nHost: localhost\r\n\r\n"
CLOSE_REQUEST = b"GET /api/e2e/json HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n"

HTTP_OK_LINE = b"HTTP/1.1 200"
CONNECTION_CLOSE = b"Connection: close"

@pytest.fixture (scope="module")
def keeper ():
	process = start (
		["python3", "-u", str (SERVER_SCRIPT), str (KEEP_ALIVE_PORT)], env=KEEP_ALIVE_ENVIRONMENT
	)

	if (not wait_listening (process, KEEP_ALIVE_PORT)):
		stop (process)
		pytest.fail (f"the server did not listen:\n{output (process)}")

	yield process

	code = stop (process)

	assert code == 0, f"the server exited {code}:\n{output (process)}"

def _read_until_close (connection) -> bytes:
	response = b""
	chunk = connection.recv (RESPONSE_SIZE)
	while (chunk):
		response += chunk
		chunk = connection.recv (RESPONSE_SIZE)

	return response

class TestKeepAlive:

	def test_a_connection_handles_many_requests (self, keeper):
		connection = http.client.HTTPConnection (SERVER_ADDRESS, KEEP_ALIVE_PORT, timeout=REQUEST_SECONDS)

		connection.request ("GET", JSON_PATH)
		first = connection.getresponse ()
		first.read ()

		kept = connection.sock

		for _ in range (REQUESTS):
			connection.request ("GET", JSON_PATH)
			response = connection.getresponse ()
			body = response.read ()

			assert response.status == 200
			assert body
			assert response.getheader ("Connection") is None

			# http.client opens another socket when the server closed the one that it had
			assert connection.sock is kept

		connection.close ()

	def test_a_client_that_asks_for_the_close_gets_it (self, keeper):
		with socket.create_connection ((SERVER_ADDRESS, KEEP_ALIVE_PORT), timeout=REQUEST_SECONDS) as connection:
			connection.sendall (JSON_REQUEST + CLOSE_REQUEST)

			# the server closes the connection after the second response, the read ends there
			response = _read_until_close (connection)

		assert response.count (HTTP_OK_LINE) == 2
		assert response.count (CONNECTION_CLOSE) == 1
		assert response.index (CONNECTION_CLOSE) > response.rindex (HTTP_OK_LINE)

	def test_pipelined_requests_are_answered_in_order (self, keeper):
		with socket.create_connection ((SERVER_ADDRESS, KEEP_ALIVE_PORT), timeout=REQUEST_SECONDS) as connection:
			connection.sendall ((JSON_REQUEST * PIPELINED) + CLOSE_REQUEST)

			response = _read_until_close (connection)

		assert response.count (HTTP_OK_LINE) == PIPELINED + 1
		assert response.count (CONNECTION_CLOSE) == 1

	def test_the_default_limit_of_requests_is_not_reached_by_a_few (self, keeper):
		assert HTTP_CERVER_DEFAULT_KEEP_ALIVE_REQUESTS > REQUESTS
