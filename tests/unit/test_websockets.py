"""The bindings of WebSocket that do not need a connection: the checks, the names and the handlers."""

import ctypes
import pytest

from cerver.callbacks import callbacks
from cerver.http import websockets as ws

pytestmark = [pytest.mark.unit]

RFC_KEY = b"dGhlIHNhbXBsZSBub25jZQ=="
RFC_ACCEPT = b"s3pPLMBiTxaQ9kYGzzhZRbK+xOo="

ACCEPT_SIZE = 29

class TestHandshake:

	def test_accept_of_rfc_6455 (self):
		accept = ctypes.create_string_buffer (ACCEPT_SIZE)
		assert ws.http_web_socket_accept_compute (RFC_KEY, len (RFC_KEY), accept)
		assert accept.value == RFC_ACCEPT

	def test_accept_helper (self):
		assert ws.web_socket_accept (RFC_KEY) == RFC_ACCEPT
		assert ws.web_socket_accept (RFC_KEY.decode ()) == RFC_ACCEPT
		assert ws.web_socket_accept (b"short") is None
		assert ws.HTTP_WEB_SOCKET_ACCEPT_SIZE == ACCEPT_SIZE
		assert len (RFC_KEY) == ws.HTTP_WEB_SOCKET_KEY_LENGTH

	@pytest.mark.parametrize ("key, valid", [
		(RFC_KEY, True),
		(b"AAAAAAAAAAAAAAAAAAAAAA==", True),
		(b"AAAAAAAAAAAAAAAAAAAAAQ==", True),
		(b"AAAAAAAAAAAAAAAAAAAAAB==", False),
		(b"short", False),
		(b"dGhlIHNhbXBsZSBub25jZQAA", False),
		(b"dGhlIHNhbXBsZSBub2!jZQ==", False)
	])
	def test_key (self, key, valid):
		assert ws.http_web_socket_key_is_valid (key, len (key)) == valid

class TestText:

	@pytest.mark.parametrize ("text, valid", [
		("ñandú y café".encode (), True),
		(b"", True),
		(b"\xc0\xaf", False),
		(b"\xed\xa0\x80", False),
		(b"\xf4\x90\x80\x80", False),
		(b"\xe2\x82", False)
	])
	def test_utf_8 (self, text, valid):
		assert ws.http_web_socket_text_check (text, len (text)) == valid

class TestCodes:

	@pytest.mark.parametrize ("code, valid", [
		(1000, True), (1001, True), (1003, True), (1007, True), (1014, True), (3000, True), (4999, True),
		(999, False), (1004, False), (1005, False), (1006, False), (1015, False), (2999, False), (5000, False)
	])
	def test_close_code (self, code, valid):
		assert ws.http_web_socket_close_code_is_valid (code) == valid

	def test_names (self):
		assert ws.http_web_socket_opcode_to_string (ws.HTTP_WEB_SOCKET_OPCODE_TEXT) == b"Text"
		assert ws.http_web_socket_close_code_to_string (ws.HTTP_WEB_SOCKET_CLOSE_MESSAGE_TOO_BIG) == b"Message Too Big"
		assert ws.http_web_socket_state_to_string (ws.HTTP_WEB_SOCKET_STATE_OPEN) == b"Open"
		assert ws.http_web_socket_error_to_string (ws.HTTP_WEB_SOCKET_ERROR_PONG_TIMEOUT) == b"Pong Timeout"
		assert ws.http_web_socket_rejection_to_string (ws.HTTP_WEB_SOCKET_REJECTION_LIMIT) == b"Limit"

class TestDeflate:

	def test_options_default (self):
		options = ws.HttpWebSocketDeflateOptions ()
		ws.http_web_socket_deflate_options_init (ctypes.byref (options))
		assert not options.enabled
		assert options.level == ws.HTTP_WEB_SOCKET_DEFLATE_DEFAULT_LEVEL
		assert options.window_bits == ws.HTTP_WEB_SOCKET_DEFLATE_MAX_WINDOW_BITS
		assert options.min_size == ws.HTTP_WEB_SOCKET_DEFLATE_DEFAULT_MIN_SIZE

	def test_available (self):
		# the test image builds cerver with zlib
		assert ws.http_web_socket_deflate_available ()

class TestHandlers:

	def test_only_the_given_methods (self):
		handlers = ws.web_socket_handlers (on_message=lambda web_socket, opcode, data: None)
		assert handlers.on_message
		assert not handlers.on_open
		assert not handlers.on_close
		assert not handlers.on_upgrade

	def test_every_method (self):
		def nothing (*arguments):
			return None

		handlers = ws.web_socket_handlers (
			on_upgrade=lambda http_receive, request, upgrade: True,
			on_open=nothing, on_message=nothing, on_fragment=nothing,
			on_ping=nothing, on_pong=nothing, on_close=nothing, on_error=nothing
		)

		for name, _ in ws.HttpWebSocketHandlers._fields_:
			assert getattr (handlers, name), name

	def test_protocols (self):
		array, count = ws.web_socket_protocols (["chat", b"superchat"])
		assert count == 2
		assert array[0] == b"chat"
		assert array[1] == b"superchat"

	def test_release (self):
		# the callbacks of the handlers are kept until they are released
		before = len (callbacks)
		handlers = ws.web_socket_handlers (on_open=lambda web_socket: None, on_error=lambda web_socket, error: None)
		assert len (handlers.kept) == 2
		assert len (callbacks) == before + 2

		ws.web_socket_handlers_release (handlers)
		assert handlers.kept == []
		assert len (callbacks) == before

		# releasing them again does nothing
		ws.web_socket_handlers_release (handlers)
		assert len (callbacks) == before

	def test_delete_data_is_kept (self):
		before = len (callbacks)
		delete_data = ws.web_socket_delete_data (lambda data: None)
		assert isinstance (delete_data, ws.HttpWebSocketDeleteData)
		assert len (callbacks) == before + 1

class TestUpgrade:

	def test_protocol_is_kept (self):
		upgrade = ctypes.pointer (ws.HttpWebSocketUpgrade ())

		# built at run time, the Structure must not be the only owner of its bytes
		ws.web_socket_upgrade_set_protocol (upgrade, "chat" + str (2))
		assert upgrade.contents.protocol == b"chat2"

		ws.web_socket_upgrade_set_protocol (upgrade, bytearray (b"other"))
		assert upgrade.contents.protocol == b"other"

		ws.web_socket_upgrade_set_protocol (upgrade, None)
		assert upgrade.contents.protocol is None

	def test_header_without_the_headers_of_cerver (self):
		# an upgrade that cerver did not create has no list of headers
		upgrade = ctypes.pointer (ws.HttpWebSocketUpgrade ())
		assert ws.web_socket_upgrade_add_header (upgrade, "X-Test", "yes") == 1

	def test_layout (self):
		names = [name for name, _ in ws.HttpWebSocketUpgrade._fields_]
		assert names == ["protocol", "data", "delete_data", "adopt_decoded_data", "status", "headers"]

class TestPayloads:

	def test_text_is_not_a_binary_message (self):
		with pytest.raises (TypeError):
			ws.web_socket_send (None, 5)

		with pytest.raises (TypeError):
			ws.web_socket_send (None, ["a"])

	def test_types (self):
		# a connection that does not exist: every type reaches cerver, that returns its error
		assert ws.web_socket_send (None, "text") == 1
		assert ws.web_socket_send (None, b"bytes") == 1
		assert ws.web_socket_send (None, bytearray (b"bytes")) == 1
		assert ws.web_socket_send (None, memoryview (b"bytes")) == 1

	def test_stream_that_does_not_begin (self):
		with pytest.raises (ConnectionError):
			with ws.web_socket_stream (None):
				pass

class TestStats:

	def test_without_a_cerver (self):
		assert ws.web_socket_stats () is None
		assert ws.web_socket_stats (web_socket=None) is None

	def test_layout (self):
		stats = ws.HttpWebSocketStats ()
		assert len (stats.n_rejected) == ws.HTTP_WEB_SOCKET_REJECTIONS
		assert len (stats.n_closes) == ws.HTTP_WEB_SOCKET_CLOSE_CODES_SIZE
		assert ctypes.sizeof (stats) == 8 * (10 + ws.HTTP_WEB_SOCKET_REJECTIONS + ws.HTTP_WEB_SOCKET_CLOSE_CODES_SIZE)

class TestReference:

	def test_without_a_connection (self):
		reference = ws.web_socket_keep (None)
		assert reference.send ("text") == 1
		assert reference.close () == 1
		reference.release ()
		reference.release ()

class TestWithoutConnection:

	def test_null_connection (self):
		assert ws.http_web_socket_send_text (None, b"text", 4) == 1
		assert ws.http_web_socket_close (None, ws.HTTP_WEB_SOCKET_CLOSE_NORMAL, None) == 1
		assert ws.http_web_socket_get_state (None) == ws.HTTP_WEB_SOCKET_STATE_CLOSED

	def test_client_without_url (self):
		client = ws.http_web_socket_client_create ()
		assert client
		assert ws.http_web_socket_client_set_url (client, b"wss://example.com") == 1
		assert ws.http_web_socket_client_set_url (client, b"ws://example.com:9001/chat") == 0
		assert ws.http_web_socket_client_get_web_socket (client) is None
		assert ws.http_web_socket_client_get_connections (client) == 0
		ws.http_web_socket_client_delete (client)
