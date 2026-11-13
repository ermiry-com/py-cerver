"""The protocol of cerver in the wire, read and written from Python with a plain socket against
the echo cerver of pycerver (e2e/echo.py): the header of PACKET_HEADER_SIZE bytes and the objects
encoded by their schemas, that any CBOR decoder reads (cbor2 here).
"""

import cbor2
import pytest
import socket
from pathlib import Path

from cerver.core import CERVER_PACKET_TYPE_INFO, CERVER_ERROR_PACKET_ERROR, CERVER_TYPE_CUSTOM
from cerver.core import GAME_PACKET_TYPE_LOBBY_CREATE
from cerver.core import PACKET_FLAG_SERIALIZED, PACKET_HEADER_RESULT_NONE, PACKET_HEADER_SIZE
from cerver.core import PACKET_TYPE_APP, PACKET_TYPE_CERVER, PACKET_TYPE_ERROR, PACKET_TYPE_GAME
from cerver.core import PacketHeader, packet_header_from_bytes, packet_header_to_bytes
from cerver.core import SERIALIZER_VERSION_KEY
from cerver.network import PROTOCOL_TCP

from e2e.conftest import output, start, stop, wait_listening

pytestmark = [pytest.mark.e2e]

ECHO_SCRIPT = Path (__file__).parent / "echo.py"

PROTOCOL_ADDRESS = "127.0.0.1"
PROTOCOL_PORT = 8096

# the name and the request type of the answers of e2e/echo.py
ECHO_NAME = "pycerver-echo"
ECHO_REQUEST = 7

RECEIVE_SECONDS = 8

APP_REQUEST = 3
APP_DATA = "ñandú".encode ("utf-8")

# the keys of the fields of a CerverSummary and of an ErrorMessage
SUMMARY_TYPE = 1
SUMMARY_NAME = 2
SUMMARY_PROTOCOL = 5
SUMMARY_PORT = 6
ERROR_TYPE = 2
ERROR_MESSAGE = 3

def receive_exactly (connection: socket.socket, size: int) -> bytes:
	data = b""
	while (len (data) < size):
		chunk = connection.recv (size - len (data))
		if (not chunk):
			raise ConnectionError (f"the cerver closed after {len (data)} of {size} bytes")

		data += chunk

	return data

def receive_packet (connection: socket.socket) -> tuple[PacketHeader, bytes]:
	"""Reads a packet: its header and then the rest of its size."""
	result, header = packet_header_from_bytes (receive_exactly (connection, PACKET_HEADER_SIZE))
	assert result == PACKET_HEADER_RESULT_NONE

	return header, receive_exactly (connection, header.packet_size - PACKET_HEADER_SIZE)

def send_packet (connection: socket.socket, packet_type: int, request_type: int, data: bytes) -> None:
	header = PacketHeader ()
	header.packet_type = packet_type
	header.request_type = request_type
	header.packet_size = PACKET_HEADER_SIZE + len (data)

	connection.sendall (packet_header_to_bytes (header) + data)

@pytest.fixture (scope="module")
def echo ():
	server = start (["python3", "-u", str (ECHO_SCRIPT), "tcp", PROTOCOL_ADDRESS, str (PROTOCOL_PORT)])
	assert wait_listening (server, PROTOCOL_PORT), output (server)

	yield server

	assert stop (server) == 0, output (server)

@pytest.fixture
def connection (echo):
	with socket.create_connection ((PROTOCOL_ADDRESS, PROTOCOL_PORT), timeout=RECEIVE_SECONDS) as connection:
		yield connection

class TestProtocol:

	def test_header_bytes_round_trip (self):
		header = PacketHeader ()
		header.packet_type = PACKET_TYPE_APP
		header.request_type = APP_REQUEST
		header.packet_size = PACKET_HEADER_SIZE + len (APP_DATA)
		header.route_id = 0xCAFE

		data = packet_header_to_bytes (header)
		assert len (data) == PACKET_HEADER_SIZE

		result, decoded = packet_header_from_bytes (data)
		assert result == PACKET_HEADER_RESULT_NONE
		assert (decoded.packet_type, decoded.request_type) == (PACKET_TYPE_APP, APP_REQUEST)
		assert (decoded.packet_size, decoded.route_id) == (header.packet_size, header.route_id)

	def test_cerver_summary_is_cbor (self, connection):
		header, data = receive_packet (connection)
		assert (header.packet_type, header.request_type) == (PACKET_TYPE_CERVER, CERVER_PACKET_TYPE_INFO)
		assert header.flags & PACKET_FLAG_SERIALIZED

		summary = cbor2.loads (data)
		assert SERIALIZER_VERSION_KEY in summary
		assert summary[SUMMARY_TYPE] == CERVER_TYPE_CUSTOM
		assert summary[SUMMARY_NAME] == ECHO_NAME
		assert summary.get (SUMMARY_PROTOCOL, PROTOCOL_TCP) == PROTOCOL_TCP
		assert summary[SUMMARY_PORT] == PROTOCOL_PORT

	def test_app_packet_is_echoed (self, connection):
		receive_packet (connection)

		send_packet (connection, PACKET_TYPE_APP, APP_REQUEST, APP_DATA)

		header, data = receive_packet (connection)
		assert (header.packet_type, header.request_type) == (PACKET_TYPE_APP, ECHO_REQUEST)
		assert not (header.flags & PACKET_FLAG_SERIALIZED)
		assert data == APP_DATA

	def test_error_message_is_cbor (self, connection):
		receive_packet (connection)

		# a cerver that is not a game cerver answers every game request with an error
		send_packet (connection, PACKET_TYPE_GAME, GAME_PACKET_TYPE_LOBBY_CREATE, b"")

		header, data = receive_packet (connection)
		assert header.packet_type == PACKET_TYPE_ERROR
		assert header.flags & PACKET_FLAG_SERIALIZED

		message = cbor2.loads (data)
		assert message[ERROR_TYPE] == CERVER_ERROR_PACKET_ERROR
		assert message[ERROR_MESSAGE]
