"""A started web server of pycerver, with the groups API, against real HTTP requests.

Bugs these tests fixed:
- http_send_response () counted the Content-Length in characters, so a body with accents
  was sent with a shorter length and the client read it truncated
- http_send_response () without a body raised TypeError from len (None)
- redirect () sent the Location escaped as HTML, "&" as "&amp;", which is another url
- http_request_get_body_json () of a request without a body raised: NULL pointer access
- a handler that raised closed the connection without a response, now cerver answers it with 500
"""

import json
import pytest
import socket
import struct
import time

from e2e.conftest import SERVER_ADDRESS
from e2e.conftest import SERVER_PORT
from e2e.conftest import e2e_raw
from e2e.conftest import e2e_request

pytestmark = [pytest.mark.e2e]

UNICODE_TEXT = "ñandú, añejo y café"

REDIRECT_LOCATION = "/api/e2e/next?a=1&b=<2>"

OBJECTID = "507f1f77bcf86cd799439011"

BOUNDARY = "----PyCerverBoundary7MA4YWxk"

GONE_REQUEST = b"GET /api/e2e/gone HTTP/1.1\r\nHost: localhost\r\n\r\n"

# the handler starts to wait before the client leaves
GONE_START_SECONDS = 0.3
GONE_WAIT_SECONDS = 8
GONE_POLL_SECONDS = 0.05

# SO_LINGER without lingering: close () resets the connection
LINGER_RESET = struct.pack ("ii", 1, 0)

def _multipart (filename: str, content: bytes) -> bytes:
	return (
		f"--{BOUNDARY}\r\n"
		f"Content-Disposition: form-data; name=\"file\"; filename=\"{filename}\"\r\n"
		"Content-Type: application/octet-stream\r\n\r\n"
	).encode ("utf-8") + content + f"\r\n--{BOUNDARY}--\r\n".encode ("utf-8")

class TestResponses:

	def test_json_with_accents_is_complete (self, server):
		response = e2e_request ("GET", "/api/e2e/json")

		assert response.status == 200
		assert int (response.headers["content-length"]) == len (response.body)
		assert json.loads (response.body) == {"text": UNICODE_TEXT}

	def test_text_with_accents_is_complete (self, server):
		raw = e2e_raw (b"GET /api/e2e/text HTTP/1.1\r\nHost: localhost\r\n\r\n")

		head, body = raw.split (b"\r\n\r\n", 1)
		length = int ([line for line in head.split (b"\r\n") if line.lower ().startswith (b"content-length")][0].split (b":")[1])

		assert length == len (UNICODE_TEXT.encode ("utf-8"))
		assert body == UNICODE_TEXT.encode ("utf-8")

	def test_response_without_body (self, server):
		response = e2e_request ("GET", "/api/e2e/empty")

		assert response.status == 200
		assert response.body == b""

	def test_redirect_location_is_the_url (self, server):
		response = e2e_request ("GET", "/api/e2e/redirect")

		assert response.status == 303
		assert response.headers["location"] == REDIRECT_LOCATION
		assert b"&amp;" in response.body

	def test_handler_that_raises_is_answered_with_500 (self, server):
		response = e2e_request ("GET", "/api/e2e/raise")

		assert response.status == 500
		assert response.headers["connection"] == "close"
		assert json.loads (response.body) == {"error": "Internal error!"}

		# the server keeps serving
		assert e2e_request ("GET", "/api/e2e/json").status == 200

class TestRoutes:

	def test_typed_param (self, server):
		response = e2e_request ("GET", f"/api/e2e/items/{OBJECTID}")

		assert response.status == 200
		assert json.loads (response.body) == {"id": OBJECTID}

	def test_param_that_is_not_its_type (self, server):
		assert e2e_request ("GET", "/api/e2e/items/not-an-objectid").status == 404

	def test_unknown_route (self, server):
		assert e2e_request ("GET", "/api/e2e/unknown").status == 404

	def test_method_not_allowed (self, server):
		response = e2e_request ("GET", "/api/e2e/method")

		assert response.status == 405
		assert "POST" in response.headers["allow"]

	def test_middleware_stops_the_request (self, server):
		response = e2e_request ("GET", "/api/e2e/json", headers={"Content-Type": "X-Block"})

		assert response.status == 403
		assert json.loads (response.body) == {"error": "blocked"}

class TestBody:

	def test_object (self, server):
		body = {"name": UNICODE_TEXT, "count": 2}
		response = e2e_request ("POST", "/api/e2e/body", json.dumps (body).encode ("utf-8"), {"Content-Type": "application/json"})

		assert response.status == 200
		assert json.loads (response.body) == body

	def test_without_body (self, server):
		assert e2e_request ("POST", "/api/e2e/body").status == 400

	@pytest.mark.parametrize ("content", [b"{", b"[1]", b"\xff\xfe"])
	def test_body_that_is_not_an_object (self, server, content):
		assert e2e_request ("POST", "/api/e2e/body", content, {"Content-Type": "application/json"}).status == 400

class TestUpload:

	def test_file (self, server):
		response = e2e_request (
			"POST", "/api/e2e/upload", _multipart ("photo.jpg", b"content"),
			{"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}
		)

		assert response.status == 200

		files = json.loads (response.body)["files"]
		assert len (files) == 1
		assert files[0]["original"] == "photo.jpg"
		assert files[0]["saved"]

	def test_file_input_without_file (self, server):
		response = e2e_request (
			"POST", "/api/e2e/upload", _multipart ("", b""),
			{"Content-Type": f"multipart/form-data; boundary={BOUNDARY}"}
		)

		assert response.status == 200

def _gone_found () -> dict:
	return json.loads (e2e_request ("GET", "/api/e2e/gone/found").body)

def _gone_leave (reset: bool) -> dict:
	"""Leaves while the python handler waits, returns what the handler found."""
	before = len (_gone_found ()["states"])

	connection = socket.create_connection ((SERVER_ADDRESS, SERVER_PORT))
	connection.sendall (GONE_REQUEST)
	time.sleep (GONE_START_SECONDS)

	if (reset):
		connection.setsockopt (socket.SOL_SOCKET, socket.SO_LINGER, LINGER_RESET)

	connection.close ()

	deadline = time.monotonic () + GONE_WAIT_SECONDS
	found = _gone_found ()
	while ((len (found["states"]) == before) and (time.monotonic () < deadline)):
		time.sleep (GONE_POLL_SECONDS)
		found = _gone_found ()

	return {"state": found["states"][before], "gone": found["gone"][before]}

class TestClientGone:

	def test_handler_finds_its_client_closed (self, server):
		assert _gone_leave (False) == {"state": "Closed", "gone": True}

	def test_handler_finds_its_client_reset (self, server):
		assert _gone_leave (True) == {"state": "Reset", "gone": True}
