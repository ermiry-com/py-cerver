"""Every example of examples/ runs: a web example answers a request and stops with SIGINT,
the worker handles its events, the client gets the answers of its echo server, the long handler
stops when its client leaves, and the WebSocket examples talk with the websockets package and
with the client of cerver.
"""

import json
import os
import pytest
import socket
import subprocess
import sys
import time
from pathlib import Path

import http.client

from websockets.exceptions import InvalidStatus
from websockets.sync.client import connect

from e2e.conftest import output, start, stop, wait_listening
from e2e.conftest import SERVER_ADDRESS, REQUEST_SECONDS

pytestmark = [pytest.mark.e2e]

PACKAGE_ROOT = Path (__file__).resolve ().parent.parent.parent
EXAMPLES = PACKAGE_ROOT / "examples"

EXAMPLE_PORT = 8097
ECHO_PORT = 7097

STATUS_OK = 200
STATUS_CREATED = 201
STATUS_ACCEPTED = 202
STATUS_MULTI_STATUS = 207
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_METHOD_NOT_ALLOWED = 405
STATUS_UPGRADE_REQUIRED = 426

READY_SECONDS = 16
POLL_SECONDS = 0.1
WORKER_SECONDS = 3
CLIENT_SECONDS = 60

# the report of the abandoned example takes 8 seconds, its client leaves after the first step
ABANDONED_STEPS = 64
ABANDONED_STEP_SECONDS = 0.125

# an example, the request that it answers, the body of the request and the status
WEB_EXAMPLES = [
	("basics/quick.py", "GET", "/api/hello/world", None, STATUS_OK),
	("basics/configuration.py", "GET", "/api/status", None, STATUS_OK),
	("basics/static.py", "GET", "/index.html", None, STATUS_OK),
	("basics/version.py", "GET", "/version", None, STATUS_OK),
	("routing/groups.py", "GET", "/api/items/507f1f77bcf86cd799439011", None, STATUS_OK),
	("routing/groups.py", "GET", "/api/files/a/b/c.txt", None, STATUS_OK),
	("requests/values.py", "GET", "/api/search?page=0", None, STATUS_BAD_REQUEST),
	("requests/values.py", "POST", "/api/orders", {"product": "chair", "quantity": 2, "date": "2026-11-09"}, STATUS_CREATED),
	("requests/proxied.py", "GET", "/api/client", None, STATUS_OK),
	("responses/messages.py", "GET", "/api/missing/1", None, 404),
	("responses/transfers.py", "GET", "/api/stream", None, STATUS_OK),
	("auth/tokens.py", "GET", "/api/profile", None, STATUS_UNAUTHORIZED),
	("auth/custom.py", "GET", "/api/reports", None, STATUS_UNAUTHORIZED),
	("uploads/files.py", "POST", "/api/images", None, STATUS_BAD_REQUEST),
	("middleware/chain.py", "GET", "/api/orders", None, STATUS_OK),
	("service/main.py", "POST", "/api/notes", {"title": "first"}, STATUS_CREATED),
	("workers/handlers.py", "POST", "/api/predict", {"values": [1, 2, 3]}, STATUS_OK),
	("workers/manager.py", "POST", "/api/reports", {"name": "monthly"}, STATUS_ACCEPTED),
	("requests/methods.py", "QUERY", "/api/items", {"name": "chair"}, STATUS_OK),
	("requests/methods.py", "PROPFIND", "/api/files/report.txt", None, STATUS_MULTI_STATUS),
	("requests/methods.py", "MKCOL", "/api/files/archive", None, STATUS_CREATED),
	("requests/methods.py", "DELETE", "/api/items", None, STATUS_METHOD_NOT_ALLOWED),
	("requests/methods.py", "GET", "/api/lenient", None, STATUS_OK),
	("requests/abandoned.py", "GET", "/api/stage", None, STATUS_OK),
	("websockets/echo.py", "GET", "/api/connections", None, STATUS_OK),
	("websockets/chat.py", "GET", "/api/rooms/lobby", None, STATUS_OK),
	("websockets/chat.py", "GET", "/ws/chat", None, STATUS_UPGRADE_REQUIRED)
]

def request (method: str, path: str, body: dict | None) -> int:
	connection = http.client.HTTPConnection (SERVER_ADDRESS, EXAMPLE_PORT, timeout=REQUEST_SECONDS)
	connection.request (method, path, body=json.dumps (body).encode ("utf-8") if (body is not None) else None)

	response = connection.getresponse ()
	response.read ()
	connection.close ()

	return response.status

@pytest.mark.parametrize ("example, method, path, body, status", WEB_EXAMPLES)
def test_web_example (example, method, path, body, status):
	process = start ([sys.executable, "-u", str (EXAMPLES / example)], PACKAGE_ROOT, {"PORT": str (EXAMPLE_PORT)})

	try:
		assert wait_listening (process, EXAMPLE_PORT), output (process)
		assert request (method, path, body) == status, output (process)

	finally:
		code = stop (process)

	assert code == 0, f"{example} exited {code}:\n{output (process)}"

def test_tokens_login_and_profile ():
	process = start ([sys.executable, "-u", str (EXAMPLES / "auth" / "tokens.py")], PACKAGE_ROOT, {"PORT": str (EXAMPLE_PORT)})

	try:
		assert wait_listening (process, EXAMPLE_PORT), output (process)

		connection = http.client.HTTPConnection (SERVER_ADDRESS, EXAMPLE_PORT, timeout=REQUEST_SECONDS)
		connection.request ("POST", "/api/login", body=b"{\"username\": \"user\"}")
		token = json.loads (connection.getresponse ().read ())["token"]
		connection.close ()

		connection = http.client.HTTPConnection (SERVER_ADDRESS, EXAMPLE_PORT, timeout=REQUEST_SECONDS)
		connection.request ("GET", "/api/profile", headers={"Authorization": token})
		response = connection.getresponse ()
		profile = json.loads (response.read ())
		connection.close ()

		assert response.status == STATUS_OK
		assert profile["token"]["username"] == "user"

	finally:
		assert stop (process) == 0, output (process)

def test_worker_example ():
	process = start ([sys.executable, "-u", str (EXAMPLES / "workers" / "worker.py")], PACKAGE_ROOT)

	time.sleep (WORKER_SECONDS)

	assert stop (process) == 0, output (process)
	assert "Handled event 7" in output (process)

@pytest.mark.parametrize ("transport", ["tcp", "udp"])
def test_client_example (transport):
	server = start (
		[sys.executable, "-u", str (EXAMPLES / "client" / "server.py"), transport],
		PACKAGE_ROOT, {"PORT": str (ECHO_PORT)}
	)

	try:
		deadline = time.monotonic () + READY_SECONDS
		while ((time.monotonic () < deadline) and ("receives UDP datagrams" not in output (server)) and ("ready" not in output (server))):
			time.sleep (POLL_SECONDS)

		result = subprocess.run (
			[sys.executable, str (EXAMPLES / "client" / "client.py"), transport, "127.0.0.1"],
			cwd=PACKAGE_ROOT, env=dict (os.environ, PORT=str (ECHO_PORT)),
			capture_output=True, text=True, errors="replace", timeout=CLIENT_SECONDS
		)

		assert result.returncode == 0, f"{result.stdout}\n{result.stderr}\nserver:\n{output (server)}"

	finally:
		assert stop (server) == 0, output (server)

def wait_output (process, text: str) -> bool:
	deadline = time.monotonic () + READY_SECONDS
	while ((time.monotonic () < deadline) and (text not in output (process))):
		time.sleep (POLL_SECONDS)

	return text in output (process)

def test_abandoned_report ():
	process = start (
		[sys.executable, "-u", str (EXAMPLES / "requests" / "abandoned.py")],
		PACKAGE_ROOT, {"PORT": str (EXAMPLE_PORT), "STEPS": str (ABANDONED_STEPS), "STEP_SECONDS": str (ABANDONED_STEP_SECONDS)}
	)

	try:
		assert wait_listening (process, EXAMPLE_PORT), output (process)

		client = socket.create_connection ((SERVER_ADDRESS, EXAMPLE_PORT), timeout=REQUEST_SECONDS)
		client.sendall (b"GET /api/reports/monthly HTTP/1.1\r\nHost: example\r\n\r\n")
		time.sleep (ABANDONED_STEP_SECONDS)
		client.close ()

		assert wait_output (process, "The client of the report monthly is gone"), output (process)

	finally:
		assert stop (process) == 0, output (process)

def test_websocket_echo_and_client ():
	server = start ([sys.executable, "-u", str (EXAMPLES / "websockets" / "echo.py")], PACKAGE_ROOT, {"PORT": str (EXAMPLE_PORT)})

	try:
		assert wait_listening (server, EXAMPLE_PORT), output (server)

		with connect (f"ws://{SERVER_ADDRESS}:{EXAMPLE_PORT}/ws/echo", subprotocols=["echo"], open_timeout=REQUEST_SECONDS) as client:
			assert client.subprotocol == "echo"
			client.send ("hello")
			assert client.recv (timeout=REQUEST_SECONDS) == "hello"

		result = subprocess.run (
			[sys.executable, str (EXAMPLES / "websockets" / "client.py"), f"ws://localhost:{EXAMPLE_PORT}/ws/echo"],
			cwd=PACKAGE_ROOT, capture_output=True, text=True, errors="replace", timeout=CLIENT_SECONDS
		)

		assert result.returncode == 0, f"{result.stdout}\n{result.stderr}\nserver:\n{output (server)}"

	finally:
		assert stop (server) == 0, output (server)

def test_websocket_chat ():
	server = start ([sys.executable, "-u", str (EXAMPLES / "websockets" / "chat.py")], PACKAGE_ROOT, {"PORT": str (EXAMPLE_PORT)})
	url = f"ws://{SERVER_ADDRESS}:{EXAMPLE_PORT}/ws/chat"

	try:
		assert wait_listening (server, EXAMPLE_PORT), output (server)

		with pytest.raises (InvalidStatus) as rejected:
			connect (url, open_timeout=REQUEST_SECONDS)

		assert rejected.value.response.status_code == STATUS_BAD_REQUEST

		with connect (f"{url}?name=ana", open_timeout=REQUEST_SECONDS) as ana:
			assert ana.recv (timeout=REQUEST_SECONDS) == "ana joined lobby"

			with connect (f"{url}?name=luis", open_timeout=REQUEST_SECONDS) as luis:
				assert luis.recv (timeout=REQUEST_SECONDS) == "luis joined lobby"
				assert ana.recv (timeout=REQUEST_SECONDS) == "luis joined lobby"

				ana.send ("hola")
				assert ana.recv (timeout=REQUEST_SECONDS) == "ana: hola"
				assert luis.recv (timeout=REQUEST_SECONDS) == "ana: hola"

				luis.send ("/join kitchen")
				assert ana.recv (timeout=REQUEST_SECONDS) == "luis left to kitchen"
				assert luis.recv (timeout=REQUEST_SECONDS) == "luis joined kitchen"

				ana.send ("alone")
				assert ana.recv (timeout=REQUEST_SECONDS) == "ana: alone"

	finally:
		assert stop (server) == 0, output (server)
