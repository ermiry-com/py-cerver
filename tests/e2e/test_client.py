"""A client of pycerver against an echo cerver of pycerver (e2e/echo.py), over TCP and UDP,
in IPv4 and in IPv6 loopback: packets, handlers, events and the teardown of both sides.
"""

import pytest
import threading
import time
from ctypes import POINTER, cast
from pathlib import Path

from cerver import handler_create, handler_set_direct_handle, HandlerMethod
from cerver.callbacks import callback_wrap
from cerver.client import client_create, client_connection_create, client_connect_and_start
from cerver.client import client_set_app_handlers, client_teardown, client_event_on, client_set_name
from cerver.client import client_connection_end, CLIENT_EVENT_CONNECTED
from cerver.core import connection_get_state, connection_state_string
from cerver.core import CONNECTION_STATE_READY, CONNECTION_STATE_WORKING
from cerver.core import Packet, PACKET_TYPE_APP, packet_send_data, packet_data
from cerver.network import PROTOCOL_TCP, PROTOCOL_UDP

from e2e.conftest import output, start, stop

pytestmark = [pytest.mark.e2e]

ECHO_SCRIPT = Path (__file__).parent / "echo.py"

ECHO_PORT = 8095

# what a TCP and an UDP cerver log when they are ready
READY_MESSAGES = ("ready", "receives UDP datagrams")
POLL_SECONDS = 0.1

# a started connection receives its packets in its own thread
CONNECTED_STATES = (CONNECTION_STATE_READY, CONNECTION_STATE_WORKING)

READY_SECONDS = 16
ANSWER_SECONDS = 8

MESSAGES = [b"first", b"second", "ñandú".encode ("utf-8")]

PAIRS = [
	("tcp", "127.0.0.1", PROTOCOL_TCP), ("tcp", "::1", PROTOCOL_TCP),
	("udp", "127.0.0.1", PROTOCOL_UDP), ("udp", "::1", PROTOCOL_UDP)
]

class EchoClient:
	"""A client of pycerver that keeps the data of the answers of the echo cerver."""

	def __init__ (self, address: str, protocol: int):
		self.answers = []
		self.answered = threading.Condition ()
		self.connected = threading.Event ()

		self.client = client_create ()
		client_set_name (self.client, b"pycerver-e2e-client")

		handler = handler_create (callback_wrap (self.receive, HandlerMethod))
		handler_set_direct_handle (handler, True)
		client_set_app_handlers (self.client, handler, None)

		client_event_on (self.client, CLIENT_EVENT_CONNECTED, lambda client, connection: self.connected.set ())

		self.connection = client_connection_create (
			self.client, address.encode ("utf-8"), ECHO_PORT, protocol, ":" in address
		)

	def receive (self, packet_ptr: int) -> None:
		with self.answered:
			self.answers.append (packet_data (cast (packet_ptr, POINTER (Packet))))
			self.answered.notify_all ()

	def send (self, data: bytes) -> int:
		return packet_send_data (PACKET_TYPE_APP, 0, data, None, self.client, self.connection)

	def wait_answers (self, count: int) -> bool:
		with self.answered:
			return self.answered.wait_for (lambda: len (self.answers) >= count, ANSWER_SECONDS)

	def end (self) -> None:
		client_connection_end (self.client, self.connection)
		client_teardown (self.client)

def wait_ready (server) -> bool:
	"""Waits until the cerver logs that it is ready, the way to know it for UDP too."""
	def ready () -> bool:
		text = output (server)
		return any (message in text for message in READY_MESSAGES)

	deadline = time.monotonic () + READY_SECONDS
	while ((time.monotonic () < deadline) and (server.poll () is None) and (not ready ())):
		time.sleep (POLL_SECONDS)

	return ready ()

@pytest.mark.parametrize ("transport, address, protocol", PAIRS)
def test_echo (transport, address, protocol):
	server = start (["python3", "-u", str (ECHO_SCRIPT), transport, address, str (ECHO_PORT)])

	client = None
	try:
		assert wait_ready (server), output (server)

		client = EchoClient (address, protocol)
		assert client_connect_and_start (client.client, client.connection) == 0, output (server)
		state = connection_get_state (client.connection)
		assert state in CONNECTED_STATES, connection_state_string (state)

		for message in MESSAGES:
			assert client.send (message) == 0

		assert client.wait_answers (len (MESSAGES)), f"answers {client.answers}\n{output (server)}"
		assert sorted (client.answers) == sorted (MESSAGES)

	finally:
		if (client):
			client.end ()

		assert stop (server) == 0, output (server)
