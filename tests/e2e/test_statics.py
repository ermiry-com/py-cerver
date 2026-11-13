"""The static paths of e2e/statics.py: a private one with a Python authentication handler next to a
public one, and the deadline of all the sends of a response for a client that stops reading.
"""

import pytest
import socket
import time
from pathlib import Path

from e2e.conftest import SERVER_ADDRESS, e2e_raw, output, start, stop, wait_listening

pytestmark = [pytest.mark.e2e]

STATICS_SCRIPT = Path (__file__).parent / "statics.py"

STATICS_PORT = 8099

# the files, the token and the body of e2e/statics.py
PUBLIC_URL = "/index.html"
PUBLIC_CONTENT = b"<h1>public</h1>"
PRIVATE_URL = "/report.txt"
PRIVATE_CONTENT = b"the private report"
MISSING_URL = "/missing.txt"
AUTHORIZATION = "Bearer statics-token"
BIG_URL = "/api/statics/big"
BIG_BODY_SIZE = 1 << 26

SEND_TIMEOUT_MILLISECONDS = 500

# the client stops reading for longer than the deadline, with a small receive buffer
STOPPED_SECONDS = 2
RECEIVE_BUFFER_SIZE = 1 << 12
READ_SECONDS = 8
READ_SIZE = 1 << 16

STATUS_OK = b"200"
STATUS_UNAUTHORIZED = b"401"
STATUS_NOT_FOUND = b"404"

def get (url: str, authorization: str | None = None) -> bytes:
	headers = f"Authorization: {authorization}\r\n" if (authorization) else ""
	request = f"GET {url} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n{headers}\r\n"

	return e2e_raw (request.encode ("utf-8"), STATICS_PORT)

def status (response: bytes) -> bytes:
	return response.split (b" ", 2)[1]

@pytest.fixture (scope="module")
def statics ():
	server = start ([
		"python3", "-u", str (STATICS_SCRIPT), str (STATICS_PORT), str (SEND_TIMEOUT_MILLISECONDS)
	])

	assert wait_listening (server, STATICS_PORT), output (server)

	yield server

	assert stop (server) == 0, output (server)

class TestStaticAuthentication:

	def test_private_file_without_authentication (self, statics):
		response = get (PRIVATE_URL)
		assert status (response) == STATUS_UNAUTHORIZED
		assert PRIVATE_CONTENT not in response

	def test_private_file_with_a_bad_authentication (self, statics):
		assert status (get (PRIVATE_URL, "Bearer bad-token")) == STATUS_UNAUTHORIZED

	def test_private_file_with_its_authentication (self, statics):
		response = get (PRIVATE_URL, AUTHORIZATION)
		assert status (response) == STATUS_OK
		assert response.endswith (PRIVATE_CONTENT)

	def test_public_file_next_to_a_private_path (self, statics):
		response = get (PUBLIC_URL)
		assert status (response) == STATUS_OK
		assert response.endswith (PUBLIC_CONTENT)

	def test_missing_file_is_answered_like_a_private_one (self, statics):
		assert status (get (MISSING_URL)) == STATUS_UNAUTHORIZED
		assert status (get (MISSING_URL, AUTHORIZATION)) == STATUS_NOT_FOUND

class TestSendTimeout:

	def test_client_that_stops_reading_gets_part_of_the_body (self, statics):
		request = f"GET {BIG_URL} HTTP/1.1\r\nHost: localhost\r\nConnection: close\r\n\r\n".encode ("utf-8")

		with socket.socket (socket.AF_INET, socket.SOCK_STREAM) as connection:
			connection.setsockopt (socket.SOL_SOCKET, socket.SO_RCVBUF, RECEIVE_BUFFER_SIZE)
			connection.settimeout (READ_SECONDS)
			connection.connect ((SERVER_ADDRESS, STATICS_PORT))
			connection.sendall (request)

			time.sleep (STOPPED_SECONDS)

			received = 0
			try:
				chunk = connection.recv (READ_SIZE)
				while (chunk):
					received += len (chunk)
					chunk = connection.recv (READ_SIZE)

			except ConnectionResetError:
				pass

		# without the deadline the cerver keeps sending once the client reads again
		assert 0 < received < BIG_BODY_SIZE, output (statics)
