"""e2e tier: real web servers of pycerver started as subprocesses.

`server` starts tests/e2e/server.py on its port, waits until it listens, and at the end
stops it with SIGINT and checks that it exited 0 in time. The tests talk to it through
localhost with http.client or raw sockets, to read the bytes that cerver sent.
"""

import http.client
import os
import pytest
import signal
import socket
import subprocess
import tempfile
import time
from pathlib import Path

SERVER_PORT = 8090
SERVER_ADDRESS = "127.0.0.1"

SERVER_SCRIPT = Path (__file__).parent / "server.py"

READY_SECONDS = 16
STOP_SECONDS = 16
POLL_SECONDS = 0.1
REQUEST_SECONDS = 16

RESPONSE_SIZE = 1 << 16

def port_is_open (port: int) -> bool:
	with socket.socket (socket.AF_INET, socket.SOCK_STREAM) as connection:
		connection.settimeout (POLL_SECONDS)
		return connection.connect_ex ((SERVER_ADDRESS, port)) == 0

def wait_listening (process, port: int) -> bool:
	deadline = time.monotonic () + READY_SECONDS
	while ((time.monotonic () < deadline) and (process.poll () is None) and (not port_is_open (port))):
		time.sleep (POLL_SECONDS)

	return port_is_open (port)

def stop (process) -> int | None:
	"""Stops the server like the orchestrator does, returns its exit code, None if it hung."""
	code = None

	if (process.poll () is None):
		process.send_signal (signal.SIGINT)

	try:
		code = process.wait (timeout=STOP_SECONDS)

	except subprocess.TimeoutExpired:
		process.kill ()
		process.wait ()

	return code

def start (arguments: list, cwd: Path | None = None, env: dict | None = None):
	"""Starts a server with its output in a file: a pipe that nobody reads fills up and blocks it."""
	log_file = tempfile.TemporaryFile ()

	environment = dict (os.environ, **(env or {}))
	process = subprocess.Popen (arguments, cwd=cwd, env=environment, stdout=log_file, stderr=subprocess.STDOUT)
	process.log_file = log_file

	return process

def output (process) -> str:
	process.log_file.seek (0)

	return process.log_file.read ().decode ("utf-8", "replace")[-4000:]

@pytest.fixture (scope="session")
def server ():
	process = start (["python3", "-u", str (SERVER_SCRIPT), str (SERVER_PORT)])

	if (not wait_listening (process, SERVER_PORT)):
		stop (process)
		pytest.fail (f"the server did not listen:\n{output (process)}")

	yield process

	code = stop (process)

	assert code == 0, f"the server exited {code}:\n{output (process)}"

class E2EResponse:

	def __init__ (self, status: int, headers: dict, body: bytes):
		self.status = status
		self.headers = headers
		self.body = body

def e2e_request (method: str, path: str, body: bytes | None = None, headers: dict | None = None) -> E2EResponse:
	connection = http.client.HTTPConnection (SERVER_ADDRESS, SERVER_PORT, timeout=REQUEST_SECONDS)
	connection.request (method, path, body=body, headers=headers or dict ())

	response = connection.getresponse ()
	result = E2EResponse (response.status, {key.lower (): value for key, value in response.getheaders ()}, response.read ())
	connection.close ()

	return result

def e2e_raw (request: bytes, port: int = SERVER_PORT) -> bytes:
	"""Sends the raw request and reads everything until the server closes the connection."""
	with socket.create_connection ((SERVER_ADDRESS, port), timeout=REQUEST_SECONDS) as connection:
		connection.sendall (request)

		response = b""
		chunk = connection.recv (RESPONSE_SIZE)
		while (chunk):
			response += chunk
			chunk = connection.recv (RESPONSE_SIZE)

	return response
