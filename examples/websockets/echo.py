"""A WebSocket echo: every message comes back, with permessage-deflate (when cerver has zlib), a
subprotocol, the pings of the cerver and a limit of the messages, next to an HTTP route that
counts the connections that are open.

	python3 examples/websockets/echo.py
	python3 examples/websockets/client.py ws://localhost:8080/ws/echo
	python3 -m websockets ws://localhost:8080/ws/echo
	curl http://localhost:8080/api/connections
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, REQUEST_METHOD_GET
from cerver.http import http_cerver_configuration, http_cerver_get, http_group, http_cerver_group_create
from cerver.http import http_receive_get_cerver, http_response_json_send
from cerver.http import http_web_socket_send, http_web_socket_get_ip, http_web_socket_get_protocol
from cerver.http import http_web_socket_is_compressed, http_web_socket_close_code_to_string
from cerver.http import http_group_web_socket_add, http_cerver_web_socket_count
from cerver.http import http_endpoint_set_web_socket_protocols, http_endpoint_set_web_socket_compression
from cerver.http import http_endpoint_set_web_socket_max_message, http_endpoint_set_web_socket_ping_milliseconds
from cerver.http import web_socket_handlers, web_socket_protocols
from cerver.utils import cerver_log_success, cerver_log_warning

SERVICE_NAME = "echo"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

# the biggest message, a bigger one closes the connection with 1009
MAX_MESSAGE = 1 << 16

# the milliseconds between the pings of the cerver, and the ones that it waits for each pong
PING_INTERVAL = 16000
PONG_TIMEOUT = 8000

# the subprotocols that the endpoint accepts, a client that offers none of them is accepted without one
PROTOCOLS = web_socket_protocols (["echo"])

def on_open (web_socket):
	protocol = http_web_socket_get_protocol (web_socket)
	cerver_log_success (
		f"{http_web_socket_get_ip (web_socket).decode ()} connected, protocol {protocol}, "
		f"compressed {http_web_socket_is_compressed (web_socket)}"
	)

def on_message (web_socket, opcode, data):
	"""A text comes back as a text and a binary message as a binary one."""
	http_web_socket_send (web_socket, opcode, data, len (data))

def on_close (web_socket, code, reason):
	cerver_log_warning (f"Closed with {code} ({http_web_socket_close_code_to_string (code).decode ()}) {reason}")

HANDLERS = web_socket_handlers (on_open=on_open, on_message=on_message, on_close=on_close)

def connections (http_receive, request):
	"""GET /api/connections"""
	http_cerver = http_receive_get_cerver (http_receive)
	http_response_json_send (http_receive, HTTP_STATUS_OK, {"connections": http_cerver_web_socket_count (http_cerver, None)})

def register (http_cerver: int) -> None:
	group = http_cerver_group_create (http_cerver, b"ws")

	echo = http_group_web_socket_add (group, b"echo", HANDLERS)
	http_endpoint_set_web_socket_protocols (echo, *PROTOCOLS)
	http_endpoint_set_web_socket_compression (echo, True)
	http_endpoint_set_web_socket_max_message (echo, MAX_MESSAGE)
	http_endpoint_set_web_socket_ping_milliseconds (echo, PING_INTERVAL, PONG_TIMEOUT)

	http_group (http_cerver, "api/connections", REQUEST_METHOD_GET, connections)

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	register (http_cerver_get (service))

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
