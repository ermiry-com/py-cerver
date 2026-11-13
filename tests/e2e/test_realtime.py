"""WebSocket end to end: the server of tests/e2e/realtime.py (every method in Python) against the
websockets package, an implementation that is not cerver, and against the client of cerver from Python."""

import json
import pytest
import sys
import threading
import time
from pathlib import Path

from websockets.exceptions import ConnectionClosed, InvalidStatus
from websockets.sync.client import connect

from cerver.http import websockets as ws

from e2e.conftest import output, start, stop, wait_listening

pytestmark = [pytest.mark.e2e]

PORT = 8093
URL = f"ws://127.0.0.1:{PORT}"

SCRIPT = Path (__file__).parent / "realtime.py"

TIMEOUT_SECONDS = 16

LARGE_SIZE = 300000

CHAT_CLIENTS = 3

# the questions about the data that was deleted, the connection that had it ends in its own thread
DELETED_ATTEMPTS = 64
DELETED_INTERVAL_SECONDS = 0.05

@pytest.fixture (scope="module")
def websockets_server ():
	process = start ([sys.executable, "-u", str (SCRIPT), str (PORT)])

	if (not wait_listening (process, PORT)):
		stop (process)
		pytest.fail (f"the server did not listen:\n{output (process)}")

	yield process

	code = stop (process)

	assert code == 0, f"the server exited {code}:\n{output (process)}"

class TestEcho:

	def test_text_and_binary (self, websockets_server):
		with connect (f"{URL}/ws/echo", open_timeout=TIMEOUT_SECONDS) as client:
			client.send ("ñandú y café")
			assert client.recv (timeout=TIMEOUT_SECONDS) == "ñandú y café"

			large = bytes (index % 251 for index in range (LARGE_SIZE))
			client.send (large)
			assert client.recv (timeout=TIMEOUT_SECONDS) == large

	def test_compression (self, websockets_server):
		with connect (f"{URL}/ws/echo", open_timeout=TIMEOUT_SECONDS) as client:
			assert "permessage-deflate" in client.response.headers["Sec-WebSocket-Extensions"]

			text = "cerver " * 1000
			for _ in range (3):
				client.send (text)
				assert client.recv (timeout=TIMEOUT_SECONDS) == text

	def test_without_compression (self, websockets_server):
		with connect (f"{URL}/ws/echo", compression=None, open_timeout=TIMEOUT_SECONDS) as client:
			assert "Sec-WebSocket-Extensions" not in client.response.headers
			client.send (b"\x00\x01\x02")
			assert client.recv (timeout=TIMEOUT_SECONDS) == b"\x00\x01\x02"

	def test_fragments (self, websockets_server):
		with connect (f"{URL}/ws/echo", open_timeout=TIMEOUT_SECONDS) as client:
			client.send (["in ", "three ", "fragments"])
			assert client.recv (timeout=TIMEOUT_SECONDS) == "in three fragments"

	def test_close (self, websockets_server):
		client = connect (f"{URL}/ws/echo", open_timeout=TIMEOUT_SECONDS)
		client.close (code=4000, reason="bye")
		assert client.close_code == 4000

class TestUpgrade:

	def test_data_of_on_upgrade (self, websockets_server):
		with connect (f"{URL}/ws/upgrade", open_timeout=TIMEOUT_SECONDS) as client:
			assert client.recv (timeout=TIMEOUT_SECONDS) == b"python-data"

	def test_rejected_by_on_upgrade (self, websockets_server):
		with pytest.raises (InvalidStatus) as rejected:
			connect (f"{URL}/ws/upgrade", additional_headers={"X-Reject": "yes"}, open_timeout=TIMEOUT_SECONDS)

		assert rejected.value.response.status_code == 409

	def test_headers_of_on_upgrade (self, websockets_server):
		with connect (f"{URL}/ws/upgrade", open_timeout=TIMEOUT_SECONDS) as client:
			headers = client.response.headers
			assert headers["X-Python"] == "yes"
			assert headers.get_all ("Set-Cookie") == ["first=1", "second=2"]
			assert headers.get_all ("Upgrade") == ["websocket"]

	def test_protocol_of_on_upgrade (self, websockets_server):
		# the bytes of the protocol were built in on_upgrade (), cerver reads them after it returned
		with connect (
			f"{URL}/ws/upgrade", subprotocols=["chat", "chat.v2"],
			additional_headers={"X-Protocol": "chat.v2"}, open_timeout=TIMEOUT_SECONDS
		) as client:
			assert client.subprotocol == "chat.v2"

		with connect (f"{URL}/ws/upgrade", subprotocols=["chat", "chat.v2"], open_timeout=TIMEOUT_SECONDS) as client:
			assert client.subprotocol == "chat"

	def test_query (self, websockets_server):
		with connect (f"{URL}/ws/upgrade?room=7&name=a%20b", open_timeout=TIMEOUT_SECONDS) as client:
			assert client.recv (timeout=TIMEOUT_SECONDS) == b"python-data"
			client.send (b"query")
			assert client.recv (timeout=TIMEOUT_SECONDS) == "room=7&name=a%20b"

		with connect (f"{URL}/ws/upgrade", open_timeout=TIMEOUT_SECONDS) as client:
			assert client.recv (timeout=TIMEOUT_SECONDS) == b"python-data"
			client.send (b"query")
			assert client.recv (timeout=TIMEOUT_SECONDS) == "none"

class TestExceptions:

	def test_method_that_raises (self, websockets_server):
		# the connection is closed with 1011, it was left open with the exception only printed
		client = connect (f"{URL}/ws/broken", open_timeout=TIMEOUT_SECONDS)
		client.send ("anything")
		with pytest.raises (ConnectionClosed):
			client.recv (timeout=TIMEOUT_SECONDS)

		assert client.close_code == ws.HTTP_WEB_SOCKET_CLOSE_INTERNAL_ERROR

	def test_upgrade_that_raises (self, websockets_server):
		with pytest.raises (InvalidStatus) as rejected:
			connect (f"{URL}/ws/broken", additional_headers={"X-Raise": "yes"}, open_timeout=TIMEOUT_SECONDS)

		assert rejected.value.response.status_code == 500

		# the server goes on
		with connect (f"{URL}/ws/echo", open_timeout=TIMEOUT_SECONDS) as client:
			client.send ("still")
			assert client.recv (timeout=TIMEOUT_SECONDS) == "still"

class TestHelpers:

	def test_stats (self, websockets_server):
		with connect (f"{URL}/ws/stats", open_timeout=TIMEOUT_SECONDS) as client:
			client.send ("cerver")
			first = json.loads (client.recv (timeout=TIMEOUT_SECONDS))
			assert first["connections"] >= 1
			assert first["opened"] >= first["connections"]
			assert len (first["rejected"]) == ws.HTTP_WEB_SOCKET_REJECTIONS

			client.send ("cerver")
			second = json.loads (client.recv (timeout=TIMEOUT_SECONDS))
			assert second["messages_received"] == first["messages_received"] + 1

			# the ones of the connection: its three messages and their bytes
			client.send ("connection")
			connection = json.loads (client.recv (timeout=TIMEOUT_SECONDS))
			assert connection["messages_received"] == 3
			assert connection["bytes_received"] == len ("cerver") * 2 + len ("connection")
			assert connection["connections"] == 0

	def test_stream (self, websockets_server):
		with connect (f"{URL}/ws/stream", open_timeout=TIMEOUT_SECONDS) as client:
			client.send ("go")
			assert client.recv (timeout=TIMEOUT_SECONDS) == "one two"

	def test_send_after_its_method (self, websockets_server):
		# the answer is sent from another thread with a reference that was kept
		with connect (f"{URL}/ws/later", open_timeout=TIMEOUT_SECONDS) as client:
			for _ in range (3):
				client.send ("go")
				assert client.recv (timeout=TIMEOUT_SECONDS) == "later"

	def test_reference_after_the_connection_ended (self, websockets_server):
		# the client leaves before the answer: the send of the reference only fails
		client = connect (f"{URL}/ws/later", open_timeout=TIMEOUT_SECONDS)
		client.send ("go")
		client.close ()

		with connect (f"{URL}/ws/later", open_timeout=TIMEOUT_SECONDS) as other:
			other.send ("go")
			assert other.recv (timeout=TIMEOUT_SECONDS) == "later"

	def test_binary_types (self, websockets_server):
		with connect (f"{URL}/ws/types", open_timeout=TIMEOUT_SECONDS) as client:
			client.send (b"\x00\x01\x02")
			assert client.recv (timeout=TIMEOUT_SECONDS) == b"\x00\x01\x02"
			assert client.recv (timeout=TIMEOUT_SECONDS) == b"\x00\x01\x02"

	def test_delete_data (self, websockets_server):
		# the data of a connection is deleted with the method that its upgrade kept
		connect (f"{URL}/ws/deleted", open_timeout=TIMEOUT_SECONDS).close ()

		with connect (f"{URL}/ws/deleted", open_timeout=TIMEOUT_SECONDS) as client:
			count = 0
			for _ in range (DELETED_ATTEMPTS):
				client.send ("count")
				count = int (client.recv (timeout=TIMEOUT_SECONDS))
				if (count):
					break

				time.sleep (DELETED_INTERVAL_SECONDS)

			assert count >= 1

class TestChat:

	def test_broadcast_to_the_room (self, websockets_server):
		clients = [connect (f"{URL}/ws/chat", open_timeout=TIMEOUT_SECONDS) for _ in range (CHAT_CLIENTS)]
		for client in clients:
			client.send ("join:python")
			assert client.recv (timeout=TIMEOUT_SECONDS) == "joined"

		clients[0].send ("say:python:hello")
		for client in clients[1:]:
			assert client.recv (timeout=TIMEOUT_SECONDS) == "hello"

		for client in clients:
			client.close ()

class TestClient:

	def test_client_of_cerver (self, websockets_server):
		received = []
		closed = []
		event = threading.Event ()

		def on_message (web_socket, opcode, data):
			received.append ((opcode, data))
			event.set ()

		def on_close (web_socket, code, reason):
			closed.append (code)

		client = ws.http_web_socket_client_create ()
		assert ws.http_web_socket_client_set_url (client, f"{URL}/ws/echo".encode ()) == 0
		ws.http_web_socket_client_set_handlers (client, ws.web_socket_handlers (on_message=on_message, on_close=on_close))
		ws.http_web_socket_client_set_compression (client, True)

		assert ws.http_web_socket_client_connect (client) == 0

		web_socket = ws.http_web_socket_client_get_web_socket (client)
		assert ws.http_web_socket_is_compressed (web_socket)
		assert ws.http_web_socket_get_state (web_socket) == ws.HTTP_WEB_SOCKET_STATE_OPEN
		ws.http_web_socket_release (web_socket)

		text = "from the client of cerver".encode ()
		assert ws.http_web_socket_client_send_text (client, text, len (text)) == 0
		assert event.wait (TIMEOUT_SECONDS)
		assert received == [(ws.HTTP_WEB_SOCKET_OPCODE_TEXT, text)]

		assert ws.http_web_socket_client_close (client, ws.HTTP_WEB_SOCKET_CLOSE_NORMAL, None) == 0
		ws.http_web_socket_client_wait (client)
		assert closed == [ws.HTTP_WEB_SOCKET_CLOSE_NORMAL]

		ws.http_web_socket_client_delete (client)
