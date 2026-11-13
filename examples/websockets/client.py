"""The WebSocket client of cerver: it connects (resolving the host and trying each address), offers a
subprotocol and permessage-deflate, sends texts and a binary message, gets the answers in its own
thread, reconnects when the connection ends without a close, and ends with a close of 1000.

	python3 examples/websockets/echo.py &
	python3 examples/websockets/client.py ws://localhost:8080/ws/echo
"""

import sys
import threading

from cerver import cerver_init, cerver_end
from cerver.http import HTTP_WEB_SOCKET_CLOSE_NORMAL, HTTP_WEB_SOCKET_OPCODE_TEXT, HTTP_WEB_SOCKET_OPCODE_BINARY
from cerver.http import http_web_socket_client_create, http_web_socket_client_delete
from cerver.http import http_web_socket_client_set_url, http_web_socket_client_set_handlers
from cerver.http import http_web_socket_client_set_protocols, http_web_socket_client_set_compression
from cerver.http import http_web_socket_client_add_header, http_web_socket_client_set_reconnect_milliseconds
from cerver.http import http_web_socket_client_set_timeouts_milliseconds
from cerver.http import http_web_socket_client_connect, http_web_socket_client_send
from cerver.http import http_web_socket_client_close, http_web_socket_client_wait
from cerver.http import http_web_socket_get_protocol, http_web_socket_is_compressed
from cerver.http import http_web_socket_error_to_string
from cerver.http import web_socket_handlers, web_socket_protocols
from cerver.utils import cerver_log_success, cerver_log_error, cerver_log_msg

DEFAULT_URL = "ws://localhost:8080/ws/echo"

MESSAGES = ("first", "second", "third", b"\x00\x01\x02")

PROTOCOLS = web_socket_protocols (["echo"])

# the milliseconds of the connect () of each address and of the handshake
CONNECT_TIMEOUT = 2048
HANDSHAKE_TIMEOUT = 4096

# the milliseconds between the attempts to reconnect, from the first to the longest
RECONNECT_MIN = 256
RECONNECT_MAX = 8192

ANSWERS_SECONDS = 8

answers = []
answered = threading.Condition ()

def on_open (web_socket):
	cerver_log_success (
		f"Connected, protocol {http_web_socket_get_protocol (web_socket)}, "
		f"compressed {http_web_socket_is_compressed (web_socket)}"
	)

def on_message (web_socket, opcode, data):
	"""Runs in the thread of the connection."""
	with answered:
		answers.append (data.decode () if (opcode == HTTP_WEB_SOCKET_OPCODE_TEXT) else data)
		answered.notify_all ()

def on_close (web_socket, code, reason):
	cerver_log_msg (f"Closed with {code}")

def on_error (web_socket, error):
	cerver_log_error (f"Error: {http_web_socket_error_to_string (error).decode ()}")

HANDLERS = web_socket_handlers (on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)

def send (client: int, message: str | bytes) -> int:
	"""Sends a str as a text and bytes as a binary message."""
	text = isinstance (message, str)
	data = message.encode () if (text) else message

	opcode = HTTP_WEB_SOCKET_OPCODE_TEXT if (text) else HTTP_WEB_SOCKET_OPCODE_BINARY

	return http_web_socket_client_send (client, opcode, data, len (data))

def main () -> int:
	url = sys.argv[1] if (len (sys.argv) > 1) else DEFAULT_URL

	cerver_init ()

	client = http_web_socket_client_create ()
	if (http_web_socket_client_set_url (client, url.encode ())):
		cerver_log_error (f"Invalid url {url}")
		return 1

	http_web_socket_client_set_handlers (client, HANDLERS)
	http_web_socket_client_set_protocols (client, *PROTOCOLS)
	http_web_socket_client_set_compression (client, True)
	http_web_socket_client_add_header (client, b"X-Client", b"pycerver")
	http_web_socket_client_set_timeouts_milliseconds (client, CONNECT_TIMEOUT, HANDSHAKE_TIMEOUT)
	http_web_socket_client_set_reconnect_milliseconds (client, True, RECONNECT_MIN, RECONNECT_MAX)

	result = 1
	if (not http_web_socket_client_connect (client)):
		for message in MESSAGES:
			send (client, message)

		with answered:
			answered.wait_for (lambda: len (answers) == len (MESSAGES), ANSWERS_SECONDS)

		cerver_log_success (f"Answers: {answers}")
		result = 0 if (answers == list (MESSAGES)) else 1

		http_web_socket_client_close (client, HTTP_WEB_SOCKET_CLOSE_NORMAL, b"done")
		http_web_socket_client_wait (client)

	else:
		cerver_log_error (f"Failed to connect to {url}")

	http_web_socket_client_delete (client)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
