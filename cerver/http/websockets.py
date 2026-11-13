"""WebSocket (RFC 6455 and permessage-deflate, RFC 7692): the endpoints, the connections and the client.

The methods of a connection are serialized by connection: in order and never two at the same time
(on_upgrade runs in the thread of its request). The thread that runs them is not part of the API, so
nothing of a connection is kept in the variables of a thread; a Python method holds the GIL while it
runs, and the sends can be called from any thread.

The handlers are copied by cerver, but the Python functions that they call must live as long as the
connections: web_socket_handlers () keeps them with the callbacks of the package, and an exception
of one of them never crosses into cerver (the connection is closed with 1011, an upgrade is rejected).

A connection is an int (its pointer) that is only valid inside its methods: to use it after them
(a send from another thread, a timer) keep it with web_socket_keep (), that takes a reference.
"""

import traceback

from contextlib import contextmanager
from ctypes import CFUNCTYPE, POINTER, Structure
from ctypes import c_void_p, c_int, c_uint, c_char_p, c_bool, c_size_t, c_uint8, c_uint16, c_uint64
from ctypes import cast, create_string_buffer, string_at
from typing import Any, Callable, Iterator, TypeAlias

from ..callbacks import callback_release, callback_wrap
from ..lib import lib_function
from ..types.string import StringPointer, string_text

__all__ = [
	"HTTP_WEB_SOCKET_OPCODE_CONTINUATION", "HTTP_WEB_SOCKET_OPCODE_TEXT", "HTTP_WEB_SOCKET_OPCODE_BINARY",
	"HTTP_WEB_SOCKET_OPCODE_CLOSE", "HTTP_WEB_SOCKET_OPCODE_PING", "HTTP_WEB_SOCKET_OPCODE_PONG",
	"HTTP_WEB_SOCKET_CLOSE_NORMAL", "HTTP_WEB_SOCKET_CLOSE_GOING_AWAY", "HTTP_WEB_SOCKET_CLOSE_PROTOCOL_ERROR",
	"HTTP_WEB_SOCKET_CLOSE_UNSUPPORTED_DATA", "HTTP_WEB_SOCKET_CLOSE_NO_STATUS", "HTTP_WEB_SOCKET_CLOSE_ABNORMAL",
	"HTTP_WEB_SOCKET_CLOSE_INVALID_PAYLOAD", "HTTP_WEB_SOCKET_CLOSE_POLICY_VIOLATION",
	"HTTP_WEB_SOCKET_CLOSE_MESSAGE_TOO_BIG", "HTTP_WEB_SOCKET_CLOSE_MANDATORY_EXTENSION",
	"HTTP_WEB_SOCKET_CLOSE_INTERNAL_ERROR", "HTTP_WEB_SOCKET_CLOSE_SERVICE_RESTART",
	"HTTP_WEB_SOCKET_CLOSE_TRY_AGAIN_LATER", "HTTP_WEB_SOCKET_CLOSE_BAD_GATEWAY", "HTTP_WEB_SOCKET_CLOSE_TLS_HANDSHAKE",
	"HTTP_WEB_SOCKET_STATE_CONNECTING", "HTTP_WEB_SOCKET_STATE_OPEN",
	"HTTP_WEB_SOCKET_STATE_CLOSING", "HTTP_WEB_SOCKET_STATE_CLOSED",
	"HTTP_WEB_SOCKET_ERROR_NONE", "HTTP_WEB_SOCKET_ERROR_PROTOCOL", "HTTP_WEB_SOCKET_ERROR_RECEIVE",
	"HTTP_WEB_SOCKET_ERROR_SEND", "HTTP_WEB_SOCKET_ERROR_PONG_TIMEOUT", "HTTP_WEB_SOCKET_ERROR_CLOSE_TIMEOUT",
	"HTTP_WEB_SOCKET_ERROR_MEMORY", "HTTP_WEB_SOCKET_ERROR_HANDSHAKE", "HTTP_WEB_SOCKET_ERROR_CONNECT",
	"HTTP_WEB_SOCKET_ROLE_SERVER", "HTTP_WEB_SOCKET_ROLE_CLIENT",
	"HTTP_WEB_SOCKET_REJECTION_VERSION", "HTTP_WEB_SOCKET_REJECTION_BAD_REQUEST", "HTTP_WEB_SOCKET_REJECTION_UPGRADE",
	"HTTP_WEB_SOCKET_REJECTION_ORIGIN", "HTTP_WEB_SOCKET_REJECTION_LIMIT", "HTTP_WEB_SOCKET_REJECTION_APPLICATION",
	"HTTP_WEB_SOCKET_REJECTIONS",
	"HTTP_WEB_SOCKET_DEFAULT_MAX_MESSAGE", "HTTP_WEB_SOCKET_DEFAULT_PING_INTERVAL",
	"HTTP_WEB_SOCKET_DEFAULT_PONG_TIMEOUT", "HTTP_WEB_SOCKET_DEFAULT_CLOSE_TIMEOUT", "HTTP_WEB_SOCKET_MAX_PROTOCOLS",
	"HTTP_WEB_SOCKET_DEFAULT_MAX_CONNECTIONS", "HTTP_WEB_SOCKET_DEFAULT_BROADCAST_TIMEOUT",
	"HTTP_WEB_SOCKET_MAX_ROOMS", "HTTP_WEB_SOCKET_ROOM_NAME_SIZE",
	"HTTP_WEB_SOCKET_CONTROL_MAX_SIZE", "HTTP_WEB_SOCKET_CLOSE_REASON_MAX_SIZE",
	"HTTP_WEB_SOCKET_DEFLATE_MIN_WINDOW_BITS", "HTTP_WEB_SOCKET_DEFLATE_MAX_WINDOW_BITS",
	"HTTP_WEB_SOCKET_DEFLATE_DEFAULT_LEVEL", "HTTP_WEB_SOCKET_DEFLATE_DEFAULT_MEMORY_LEVEL",
	"HTTP_WEB_SOCKET_DEFLATE_DEFAULT_MIN_SIZE",
	"HTTP_WEB_SOCKET_CLIENT_CONNECT_TIMEOUT", "HTTP_WEB_SOCKET_CLIENT_HANDSHAKE_TIMEOUT",
	"HTTP_WEB_SOCKET_CLIENT_RECONNECT_MIN", "HTTP_WEB_SOCKET_CLIENT_RECONNECT_MAX",
	"HTTP_WEB_SOCKET_KEY_LENGTH", "HTTP_WEB_SOCKET_KEY_SIZE",
	"HTTP_WEB_SOCKET_ACCEPT_LENGTH", "HTTP_WEB_SOCKET_ACCEPT_SIZE",
	"HTTP_WEB_SOCKET_CLOSE_CODES_FIRST", "HTTP_WEB_SOCKET_CLOSE_CODES_SIZE",
	"HttpWebSocketOpcode", "HttpWebSocketState", "HttpWebSocketError", "HttpWebSocketRole",
	"HttpWebSocketUpgrade", "HttpWebSocketUpgradePointer", "HttpWebSocketHandlers", "HttpWebSocketDeflateOptions",
	"HttpWebSocketStats", "HttpWebSocketStatsPointer",
	"HttpWebSocketOnUpgrade", "HttpWebSocketOnOpen", "HttpWebSocketOnMessage", "HttpWebSocketOnFragment",
	"HttpWebSocketOnControl", "HttpWebSocketOnClose", "HttpWebSocketOnError", "HttpWebSocketForEach",
	"HttpWebSocketDeleteData",
	"http_web_socket_opcode_to_string", "http_web_socket_close_code_to_string",
	"http_web_socket_close_code_description", "http_web_socket_close_code_is_valid",
	"http_web_socket_state_to_string", "http_web_socket_error_to_string", "http_web_socket_error_description",
	"http_web_socket_rejection_to_string",
	"http_web_socket_text_check", "http_web_socket_key_is_valid", "http_web_socket_accept_compute",
	"http_web_socket_deflate_available", "http_web_socket_deflate_options_init",
	"http_endpoint_set_web_socket", "http_endpoint_set_web_socket_max_message",
	"http_endpoint_set_web_socket_protocols", "http_endpoint_set_web_socket_compression",
	"http_endpoint_set_web_socket_compression_options", "http_endpoint_set_web_socket_origin_check",
	"http_endpoint_set_web_socket_ping_milliseconds", "http_endpoint_set_web_socket_close_timeout_milliseconds",
	"http_endpoint_set_web_socket_send_timeout_milliseconds",
	"http_group_web_socket_add", "http_group_set_web_socket", "http_group_set_web_socket_max_message",
	"http_group_set_web_socket_protocols", "http_group_set_web_socket_compression",
	"http_group_set_web_socket_compression_options", "http_group_set_web_socket_origin_check",
	"http_group_set_web_socket_ping_milliseconds", "http_group_set_web_socket_close_timeout_milliseconds",
	"http_group_set_web_socket_send_timeout_milliseconds",
	"http_cerver_set_web_socket_max_connections", "http_cerver_set_web_socket_broadcast_timeout_milliseconds",
	"http_cerver_web_socket_count", "http_cerver_web_socket_broadcast", "http_endpoint_web_socket_broadcast",
	"http_cerver_web_socket_for_each",
	"http_cerver_web_socket_get_stats", "http_web_socket_get_stats",
	"http_web_socket_upgrade_add_header",
	"http_web_socket_join", "http_web_socket_leave", "http_web_socket_in_room",
	"http_web_socket_get_id", "http_web_socket_get_state", "http_web_socket_get_role", "http_web_socket_get_ip",
	"http_web_socket_get_path", "http_web_socket_get_query",
	"http_web_socket_get_protocol", "http_web_socket_is_compressed",
	"http_web_socket_get_http_cerver", "http_web_socket_get_endpoint", "http_web_socket_get_endpoint_data",
	"http_web_socket_get_decoded_data", "http_web_socket_set_data", "http_web_socket_get_data",
	"http_web_socket_retain", "http_web_socket_release",
	"http_web_socket_send", "http_web_socket_send_text", "http_web_socket_send_binary",
	"http_web_socket_send_begin", "http_web_socket_send_write", "http_web_socket_send_end",
	"http_web_socket_ping", "http_web_socket_close",
	"http_web_socket_client_create", "http_web_socket_client_delete", "http_web_socket_client_set_url",
	"http_web_socket_client_add_header", "http_web_socket_client_set_protocols",
	"http_web_socket_client_set_handlers", "http_web_socket_client_set_data", "http_web_socket_client_get_data",
	"http_web_socket_client_set_compression", "http_web_socket_client_set_compression_options",
	"http_web_socket_client_set_max_message", "http_web_socket_client_set_ping_milliseconds",
	"http_web_socket_client_set_close_timeout_milliseconds", "http_web_socket_client_set_send_timeout_milliseconds",
	"http_web_socket_client_set_timeouts_milliseconds", "http_web_socket_client_set_reconnect_milliseconds",
	"http_web_socket_client_connect", "http_web_socket_client_connect_async",
	"http_web_socket_client_get_web_socket", "http_web_socket_client_send",
	"http_web_socket_client_send_text", "http_web_socket_client_send_binary",
	"http_web_socket_client_close", "http_web_socket_client_wait", "http_web_socket_client_get_connections",
	"WebSocketReference",
	"web_socket_handlers", "web_socket_handlers_release", "web_socket_protocols",
	"web_socket_send", "web_socket_close", "web_socket_stream", "web_socket_keep",
	"web_socket_accept", "web_socket_delete_data",
	"web_socket_upgrade_set_protocol", "web_socket_upgrade_add_header",
	"web_socket_query", "web_socket_stats"
]

HttpWebSocketOpcode: TypeAlias = c_int # type: ignore

HTTP_WEB_SOCKET_OPCODE_CONTINUATION = 0x0
HTTP_WEB_SOCKET_OPCODE_TEXT = 0x1
HTTP_WEB_SOCKET_OPCODE_BINARY = 0x2
HTTP_WEB_SOCKET_OPCODE_CLOSE = 0x8
HTTP_WEB_SOCKET_OPCODE_PING = 0x9
HTTP_WEB_SOCKET_OPCODE_PONG = 0xA

# the codes of the close frames (RFC 6455 section 7.4.1), 1005, 1006 and 1015 are never sent
HTTP_WEB_SOCKET_CLOSE_NORMAL = 1000
HTTP_WEB_SOCKET_CLOSE_GOING_AWAY = 1001
HTTP_WEB_SOCKET_CLOSE_PROTOCOL_ERROR = 1002
HTTP_WEB_SOCKET_CLOSE_UNSUPPORTED_DATA = 1003
HTTP_WEB_SOCKET_CLOSE_NO_STATUS = 1005
HTTP_WEB_SOCKET_CLOSE_ABNORMAL = 1006
HTTP_WEB_SOCKET_CLOSE_INVALID_PAYLOAD = 1007
HTTP_WEB_SOCKET_CLOSE_POLICY_VIOLATION = 1008
HTTP_WEB_SOCKET_CLOSE_MESSAGE_TOO_BIG = 1009
HTTP_WEB_SOCKET_CLOSE_MANDATORY_EXTENSION = 1010
HTTP_WEB_SOCKET_CLOSE_INTERNAL_ERROR = 1011
HTTP_WEB_SOCKET_CLOSE_SERVICE_RESTART = 1012
HTTP_WEB_SOCKET_CLOSE_TRY_AGAIN_LATER = 1013
HTTP_WEB_SOCKET_CLOSE_BAD_GATEWAY = 1014
HTTP_WEB_SOCKET_CLOSE_TLS_HANDSHAKE = 1015

HttpWebSocketState: TypeAlias = c_uint # type: ignore

HTTP_WEB_SOCKET_STATE_CONNECTING = 0
HTTP_WEB_SOCKET_STATE_OPEN = 1
HTTP_WEB_SOCKET_STATE_CLOSING = 2
HTTP_WEB_SOCKET_STATE_CLOSED = 3

HttpWebSocketError: TypeAlias = c_int # type: ignore

HTTP_WEB_SOCKET_ERROR_NONE = 0
HTTP_WEB_SOCKET_ERROR_PROTOCOL = 1
HTTP_WEB_SOCKET_ERROR_RECEIVE = 2
HTTP_WEB_SOCKET_ERROR_SEND = 3
HTTP_WEB_SOCKET_ERROR_PONG_TIMEOUT = 4
HTTP_WEB_SOCKET_ERROR_CLOSE_TIMEOUT = 5
HTTP_WEB_SOCKET_ERROR_MEMORY = 6
HTTP_WEB_SOCKET_ERROR_HANDSHAKE = 7
HTTP_WEB_SOCKET_ERROR_CONNECT = 8

HttpWebSocketRole: TypeAlias = c_int # type: ignore

HTTP_WEB_SOCKET_ROLE_SERVER = 0
HTTP_WEB_SOCKET_ROLE_CLIENT = 1

HTTP_WEB_SOCKET_REJECTION_VERSION = 0
HTTP_WEB_SOCKET_REJECTION_BAD_REQUEST = 1
HTTP_WEB_SOCKET_REJECTION_UPGRADE = 2
HTTP_WEB_SOCKET_REJECTION_ORIGIN = 3
HTTP_WEB_SOCKET_REJECTION_LIMIT = 4
HTTP_WEB_SOCKET_REJECTION_APPLICATION = 5
HTTP_WEB_SOCKET_REJECTIONS = 6

# milliseconds and bytes
HTTP_WEB_SOCKET_DEFAULT_MAX_MESSAGE = 1 << 20
HTTP_WEB_SOCKET_DEFAULT_PING_INTERVAL = (1 << 5) * 1000
HTTP_WEB_SOCKET_DEFAULT_PONG_TIMEOUT = (1 << 4) * 1000
HTTP_WEB_SOCKET_DEFAULT_CLOSE_TIMEOUT = (1 << 2) * 1000
HTTP_WEB_SOCKET_MAX_PROTOCOLS = 1 << 4

HTTP_WEB_SOCKET_DEFAULT_MAX_CONNECTIONS = 1 << 10
HTTP_WEB_SOCKET_DEFAULT_BROADCAST_TIMEOUT = 1 << 8

HTTP_WEB_SOCKET_MAX_ROOMS = 1 << 4
HTTP_WEB_SOCKET_ROOM_NAME_SIZE = 1 << 6

HTTP_WEB_SOCKET_CONTROL_MAX_SIZE = 125
HTTP_WEB_SOCKET_CLOSE_REASON_MAX_SIZE = 123

HTTP_WEB_SOCKET_DEFLATE_MIN_WINDOW_BITS = 8
HTTP_WEB_SOCKET_DEFLATE_MAX_WINDOW_BITS = 15
HTTP_WEB_SOCKET_DEFLATE_DEFAULT_LEVEL = 6
HTTP_WEB_SOCKET_DEFLATE_DEFAULT_MEMORY_LEVEL = 8
HTTP_WEB_SOCKET_DEFLATE_DEFAULT_MIN_SIZE = 1 << 7

HTTP_WEB_SOCKET_CLIENT_CONNECT_TIMEOUT = (1 << 3) * 1000
HTTP_WEB_SOCKET_CLIENT_HANDSHAKE_TIMEOUT = (1 << 3) * 1000
HTTP_WEB_SOCKET_CLIENT_RECONNECT_MIN = 1 << 8
HTTP_WEB_SOCKET_CLIENT_RECONNECT_MAX = 1 << 15

# the characters of a Sec-WebSocket-Key and of its Sec-WebSocket-Accept, and their buffers with their end
HTTP_WEB_SOCKET_KEY_LENGTH = 24
HTTP_WEB_SOCKET_KEY_SIZE = HTTP_WEB_SOCKET_KEY_LENGTH + 1
HTTP_WEB_SOCKET_ACCEPT_LENGTH = 28
HTTP_WEB_SOCKET_ACCEPT_SIZE = HTTP_WEB_SOCKET_ACCEPT_LENGTH + 1

# the close codes that the stats count one by one, from 1000
HTTP_WEB_SOCKET_CLOSE_CODES_FIRST = 1000
HTTP_WEB_SOCKET_CLOSE_CODES_SIZE = 16

# deletes the data of a connection when it is released
HttpWebSocketDeleteData: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

class HttpWebSocketUpgrade (Structure):
	"""What on_upgrade () decides about a connection before its 101 (HttpWebSocketUpgrade).

	cerver reads the protocol after on_upgrade () returns, so its bytes must outlive the call:
	set it with web_socket_upgrade_set_protocol (), never with a bytes object of the method.
	The headers are of cerver, web_socket_upgrade_add_header () adds one to the 101.
	"""

	_fields_ = [
		("protocol", c_char_p),
		("data", c_void_p),
		("delete_data", HttpWebSocketDeleteData),
		("adopt_decoded_data", c_bool),
		("status", c_int),
		("headers", c_void_p)
	]

HttpWebSocketUpgradePointer = POINTER (HttpWebSocketUpgrade)

class HttpWebSocketStats (Structure):
	"""A copy of the counters of the WebSocket connections of an HTTP cerver (HttpWebSocketStats).

	The stats of one connection only have its messages and its bytes.
	"""

	_fields_ = [
		("n_connections", c_uint64),
		("n_opened", c_uint64),
		("n_closed", c_uint64),
		("n_rejected", c_uint64 * HTTP_WEB_SOCKET_REJECTIONS),
		("n_messages_received", c_uint64),
		("n_messages_sent", c_uint64),
		("n_bytes_received", c_uint64),
		("n_bytes_sent", c_uint64),
		("n_slow", c_uint64),
		("n_errors", c_uint64),
		("n_closes", c_uint64 * HTTP_WEB_SOCKET_CLOSE_CODES_SIZE),
		("n_closes_other", c_uint64)
	]

HttpWebSocketStatsPointer = POINTER (HttpWebSocketStats)

# the methods of a connection, the data of a message is a pointer and its size
HttpWebSocketOnUpgrade: TypeAlias = CFUNCTYPE (c_bool, c_void_p, c_void_p, HttpWebSocketUpgradePointer) # type: ignore
HttpWebSocketOnOpen: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore
HttpWebSocketOnMessage: TypeAlias = CFUNCTYPE (None, c_void_p, c_int, c_void_p, c_size_t) # type: ignore
HttpWebSocketOnFragment: TypeAlias = CFUNCTYPE (None, c_void_p, c_int, c_void_p, c_size_t, c_bool, c_bool) # type: ignore
HttpWebSocketOnControl: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p, c_size_t) # type: ignore
HttpWebSocketOnClose: TypeAlias = CFUNCTYPE (None, c_void_p, c_uint16, c_void_p, c_size_t) # type: ignore
HttpWebSocketOnError: TypeAlias = CFUNCTYPE (None, c_void_p, c_int) # type: ignore

HttpWebSocketForEach: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p) # type: ignore

class HttpWebSocketHandlers (Structure):
	"""The methods of the connections of an endpoint or of a client (HttpWebSocketHandlers)."""

	_fields_ = [
		("on_upgrade", HttpWebSocketOnUpgrade),
		("on_open", HttpWebSocketOnOpen),
		("on_message", HttpWebSocketOnMessage),
		("on_fragment", HttpWebSocketOnFragment),
		("on_ping", HttpWebSocketOnControl),
		("on_pong", HttpWebSocketOnControl),
		("on_close", HttpWebSocketOnClose),
		("on_error", HttpWebSocketOnError)
	]

class HttpWebSocketDeflateOptions (Structure):
	"""How permessage-deflate is offered or accepted (HttpWebSocketDeflateOptions)."""

	_fields_ = [
		("enabled", c_bool),
		("level", c_int),
		("memory_level", c_int),
		("window_bits", c_uint8),
		("no_context_takeover", c_bool),
		("min_size", c_size_t)
	]

HttpWebSocketHandlersPointer = POINTER (HttpWebSocketHandlers)
HttpWebSocketDeflateOptionsPointer = POINTER (HttpWebSocketDeflateOptions)

# strings and checks
http_web_socket_opcode_to_string = lib_function (
	"http_web_socket_opcode_to_string", [HttpWebSocketOpcode], c_char_p,
	"""Returns the name of an opcode, as bytes."""
)

http_web_socket_close_code_to_string = lib_function (
	"http_web_socket_close_code_to_string", [c_uint16], c_char_p,
	"""Returns the name of a close code, as bytes."""
)

http_web_socket_close_code_description = lib_function (
	"http_web_socket_close_code_description", [c_uint16], c_char_p,
	"""Returns the description of a close code, as bytes."""
)

http_web_socket_close_code_is_valid = lib_function (
	"http_web_socket_close_code_is_valid", [c_uint16], c_bool,
	"""Returns True for a code that can be sent in a close frame."""
)

http_web_socket_state_to_string = lib_function (
	"http_web_socket_state_to_string", [HttpWebSocketState], c_char_p,
	"""Returns the name of the state of a connection, as bytes."""
)

http_web_socket_error_to_string = lib_function (
	"http_web_socket_error_to_string", [HttpWebSocketError], c_char_p,
	"""Returns the name of an error, as bytes."""
)

http_web_socket_error_description = lib_function (
	"http_web_socket_error_description", [HttpWebSocketError], c_char_p,
	"""Returns the description of an error, as bytes."""
)

http_web_socket_rejection_to_string = lib_function (
	"http_web_socket_rejection_to_string", [c_int], c_char_p,
	"""Returns the name of the reason of a rejected upgrade, as bytes."""
)

http_web_socket_text_check = lib_function (
	"http_web_socket_text_check", [c_char_p, c_size_t], c_bool,
	"""Returns True when the bytes are a whole valid UTF-8 text."""
)

http_web_socket_key_is_valid = lib_function (
	"http_web_socket_key_is_valid", [c_char_p, c_size_t], c_bool,
	"""Returns True when a Sec-WebSocket-Key is the base64 of 16 bytes, in the only form that they have."""
)

http_web_socket_accept_compute = lib_function (
	"http_web_socket_accept_compute", [c_char_p, c_size_t, c_void_p], c_bool,
	"""Writes the Sec-WebSocket-Accept of a key in a buffer of HTTP_WEB_SOCKET_ACCEPT_SIZE bytes.

	The buffer is one that can be written (create_string_buffer ()), never a bytes object:
	web_socket_accept () returns the accept of a key as bytes.

	Returns:
		True on success.
	"""
)

http_web_socket_deflate_available = lib_function (
	"http_web_socket_deflate_available", [], c_bool,
	"""Returns True when cerver was built with zlib, so permessage-deflate can be negotiated."""
)

http_web_socket_deflate_options_init = lib_function (
	"http_web_socket_deflate_options_init", [HttpWebSocketDeflateOptionsPointer], None,
	"""Sets the default options of permessage-deflate, disabled."""
)

# endpoints and groups
http_endpoint_set_web_socket = lib_function (
	"http_endpoint_set_web_socket", [c_void_p, HttpWebSocketHandlersPointer], None,
	"""Makes a GET endpoint take WebSocket connections with the methods of the handlers.

	A request without an upgrade goes to the handler of the endpoint, or it is answered with 426.
	"""
)

http_endpoint_set_web_socket_max_message = lib_function (
	"http_endpoint_set_web_socket_max_message", [c_void_p, c_size_t], None,
	"""Sets the most bytes of a message (and of each frame), a larger one closes with 1009."""
)

http_endpoint_set_web_socket_protocols = lib_function (
	"http_endpoint_set_web_socket_protocols", [c_void_p, POINTER (c_char_p), c_uint], c_uint8,
	"""Sets the subprotocols, in the order of preference of the server, returns 0 on success."""
)

http_endpoint_set_web_socket_compression = lib_function (
	"http_endpoint_set_web_socket_compression", [c_void_p, c_bool], None,
	"""Enables permessage-deflate with the default options (only with zlib)."""
)

http_endpoint_set_web_socket_compression_options = lib_function (
	"http_endpoint_set_web_socket_compression_options", [c_void_p, HttpWebSocketDeflateOptionsPointer], None,
	"""Sets the options of permessage-deflate."""
)

http_endpoint_set_web_socket_origin_check = lib_function (
	"http_endpoint_set_web_socket_origin_check", [c_void_p, c_bool], None,
	"""The Origin of the upgrade must be in the origins whitelist, 403 if it is not."""
)

http_endpoint_set_web_socket_ping_milliseconds = lib_function (
	"http_endpoint_set_web_socket_ping_milliseconds", [c_void_p, c_uint, c_uint], None,
	"""Sets the milliseconds without receiving before a ping (0 disables them) and to wait for its pong."""
)

http_endpoint_set_web_socket_close_timeout_milliseconds = lib_function (
	"http_endpoint_set_web_socket_close_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the milliseconds that the closing handshake waits for the peer."""
)

http_endpoint_set_web_socket_send_timeout_milliseconds = lib_function (
	"http_endpoint_set_web_socket_send_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the milliseconds of each send, 0 uses the send timeout of the HTTP cerver."""
)

http_group_web_socket_add = lib_function (
	"http_group_web_socket_add", [c_void_p, c_char_p, HttpWebSocketHandlersPointer], c_void_p,
	"""Adds a WebSocket endpoint (GET) to a group, with NULL handlers it inherits the ones of its groups."""
)

http_group_set_web_socket = lib_function (
	"http_group_set_web_socket", [c_void_p, HttpWebSocketHandlersPointer], None,
	"""Sets the methods that the WebSocket endpoints of the group inherit."""
)

http_group_set_web_socket_max_message = lib_function (
	"http_group_set_web_socket_max_message", [c_void_p, c_size_t], None,
	"""Sets the most bytes of a message of the WebSocket endpoints of the group."""
)

http_group_set_web_socket_protocols = lib_function (
	"http_group_set_web_socket_protocols", [c_void_p, POINTER (c_char_p), c_uint], c_uint8,
	"""Sets the subprotocols of the WebSocket endpoints of the group, returns 0 on success."""
)

http_group_set_web_socket_compression = lib_function (
	"http_group_set_web_socket_compression", [c_void_p, c_bool], None,
	"""Enables permessage-deflate in the WebSocket endpoints of the group."""
)

http_group_set_web_socket_compression_options = lib_function (
	"http_group_set_web_socket_compression_options", [c_void_p, HttpWebSocketDeflateOptionsPointer], None,
	"""Sets the options of permessage-deflate of the WebSocket endpoints of the group."""
)

http_group_set_web_socket_origin_check = lib_function (
	"http_group_set_web_socket_origin_check", [c_void_p, c_bool], None,
	"""The WebSocket endpoints of the group check the Origin with the whitelist."""
)

http_group_set_web_socket_ping_milliseconds = lib_function (
	"http_group_set_web_socket_ping_milliseconds", [c_void_p, c_uint, c_uint], None,
	"""Sets the pings of the WebSocket endpoints of the group, in milliseconds."""
)

http_group_set_web_socket_close_timeout_milliseconds = lib_function (
	"http_group_set_web_socket_close_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the close timeout of the WebSocket endpoints of the group, in milliseconds."""
)

http_group_set_web_socket_send_timeout_milliseconds = lib_function (
	"http_group_set_web_socket_send_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the send timeout of the WebSocket endpoints of the group, in milliseconds."""
)

# the connections of a cerver
http_cerver_set_web_socket_max_connections = lib_function (
	"http_cerver_set_web_socket_max_connections", [c_void_p, c_uint], None,
	"""Sets the most WebSocket connections, an upgrade above it is answered with 503."""
)

http_cerver_set_web_socket_broadcast_timeout_milliseconds = lib_function (
	"http_cerver_set_web_socket_broadcast_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the milliseconds that a broadcast waits for each connection."""
)

http_cerver_web_socket_get_stats = lib_function (
	"http_cerver_web_socket_get_stats", [c_void_p, HttpWebSocketStatsPointer], c_uint8,
	"""Copies the stats of the WebSocket connections of an HTTP cerver, returns 0 on success."""
)

http_web_socket_get_stats = lib_function (
	"http_web_socket_get_stats", [c_void_p, HttpWebSocketStatsPointer], c_uint8,
	"""Copies the stats of a connection (its messages and its bytes), returns 0 on success."""
)

http_web_socket_upgrade_add_header = lib_function (
	"http_web_socket_upgrade_add_header", [HttpWebSocketUpgradePointer, c_char_p, c_char_p], c_uint8,
	"""Adds a header to the 101 of the connection that on_upgrade () accepts, like a Set-Cookie.

	A name can be added many times; the headers that cerver writes in a 101 (Server, Upgrade,
	Connection, Sec-WebSocket-Accept, -Protocol, -Extensions, Content-Length and
	Transfer-Encoding) can not be added.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_web_socket_count = lib_function (
	"http_cerver_web_socket_count", [c_void_p, c_char_p], c_uint,
	"""Returns the WebSocket connections that are open, of a room or of every one with None."""
)

http_cerver_web_socket_broadcast = lib_function (
	"http_cerver_web_socket_broadcast", [c_void_p, c_char_p, c_void_p, HttpWebSocketOpcode, c_void_p, c_size_t], c_uint,
	"""Sends a message to the connections of a room (every one with None) but one, returns how many got it."""
)

http_endpoint_web_socket_broadcast = lib_function (
	"http_endpoint_web_socket_broadcast", [c_void_p, c_void_p, HttpWebSocketOpcode, c_void_p, c_size_t], c_uint,
	"""Sends a message to every connection of an endpoint, returns how many got it."""
)

http_cerver_web_socket_for_each = lib_function (
	"http_cerver_web_socket_for_each", [c_void_p, c_char_p, HttpWebSocketForEach, c_void_p], None,
	"""Calls a method with every connection of a room (every one with None)."""
)

http_web_socket_join = lib_function (
	"http_web_socket_join", [c_void_p, c_char_p], c_uint8,
	"""Adds the connection to a room, returns 0 on success."""
)

http_web_socket_leave = lib_function (
	"http_web_socket_leave", [c_void_p, c_char_p], c_uint8,
	"""Removes the connection from a room, returns 0 on success."""
)

http_web_socket_in_room = lib_function (
	"http_web_socket_in_room", [c_void_p, c_char_p], c_bool,
	"""Returns True when the connection is in the room."""
)

# a connection
http_web_socket_get_id = lib_function ("http_web_socket_get_id", [c_void_p], c_uint64, """Returns the id of a connection.""")
http_web_socket_get_state = lib_function ("http_web_socket_get_state", [c_void_p], HttpWebSocketState, """Returns the HTTP_WEB_SOCKET_STATE_* of a connection.""")
http_web_socket_get_role = lib_function ("http_web_socket_get_role", [c_void_p], HttpWebSocketRole, """Returns the role of a connection.""")
http_web_socket_get_ip = lib_function ("http_web_socket_get_ip", [c_void_p], c_char_p, """Returns the address of the peer, as bytes.""")
http_web_socket_get_path = lib_function ("http_web_socket_get_path", [c_void_p], c_void_p, """Returns the String of the path of the upgrade.""")
http_web_socket_get_query = lib_function ("http_web_socket_get_query", [c_void_p], c_void_p, """Returns the String of the query of the upgrade as it was sent, None when it had none.""")
http_web_socket_get_protocol = lib_function ("http_web_socket_get_protocol", [c_void_p], c_char_p, """Returns the subprotocol that was agreed, None for none.""")
http_web_socket_is_compressed = lib_function ("http_web_socket_is_compressed", [c_void_p], c_bool, """Returns True when permessage-deflate was negotiated.""")
http_web_socket_get_http_cerver = lib_function ("http_web_socket_get_http_cerver", [c_void_p], c_void_p, """Returns the HttpCerver of a connection of the server.""")
http_web_socket_get_endpoint = lib_function ("http_web_socket_get_endpoint", [c_void_p], c_void_p, """Returns the endpoint of a connection of the server.""")
http_web_socket_get_endpoint_data = lib_function ("http_web_socket_get_endpoint_data", [c_void_p], c_void_p, """Returns the custom data of the endpoint.""")
http_web_socket_get_decoded_data = lib_function ("http_web_socket_get_decoded_data", [c_void_p], c_void_p, """Returns the decoded data that the connection adopted.""")

http_web_socket_set_data = lib_function (
	"http_web_socket_set_data", [c_void_p, c_void_p, HttpWebSocketDeleteData], None,
	"""Sets the data of a connection and the method that deletes it.

	The method is a HttpWebSocketDeleteData that is kept (web_socket_delete_data ()), or None:
	a callback that is collected leaves cerver with a pointer to freed memory.
	"""
)

http_web_socket_get_data = lib_function ("http_web_socket_get_data", [c_void_p], c_void_p, """Returns the data of a connection.""")

http_web_socket_retain = lib_function (
	"http_web_socket_retain", [c_void_p], c_void_p,
	"""Takes a reference, so the connection stays valid outside of its methods."""
)

http_web_socket_release = lib_function (
	"http_web_socket_release", [c_void_p], None,
	"""Releases a reference, the last one deletes the connection."""
)

http_web_socket_send = lib_function (
	"http_web_socket_send", [c_void_p, HttpWebSocketOpcode, c_void_p, c_size_t], c_uint8,
	"""Sends a whole message from any thread, returns 0 on success."""
)

http_web_socket_send_text = lib_function (
	"http_web_socket_send_text", [c_void_p, c_char_p, c_size_t], c_uint8,
	"""Sends a text message, returns 0 on success."""
)

http_web_socket_send_binary = lib_function (
	"http_web_socket_send_binary", [c_void_p, c_void_p, c_size_t], c_uint8,
	"""Sends a binary message, returns 0 on success."""
)

http_web_socket_send_begin = lib_function (
	"http_web_socket_send_begin", [c_void_p, HttpWebSocketOpcode], c_uint8,
	"""Starts a message that is sent in pieces, returns 0 on success.

	A stream that began is always ended with http_web_socket_send_end (), also when a piece failed;
	one that did not begin (it returned 1) holds nothing and must not be ended.
	web_socket_stream () does both.
	"""
)

http_web_socket_send_write = lib_function (
	"http_web_socket_send_write", [c_void_p, c_void_p, c_size_t], c_uint8,
	"""Sends the next piece of the message, returns 0 on success."""
)

http_web_socket_send_end = lib_function (
	"http_web_socket_send_end", [c_void_p], c_uint8,
	"""Ends the message that was sent in pieces, returns 0 on success."""
)

http_web_socket_ping = lib_function (
	"http_web_socket_ping", [c_void_p, c_void_p, c_size_t], c_uint8,
	"""Sends a ping, returns 0 on success."""
)

http_web_socket_close = lib_function (
	"http_web_socket_close", [c_void_p, c_uint16, c_char_p], c_uint8,
	"""Starts the closing handshake with a code and a reason of 123 bytes or less, returns 0 on success."""
)

# the client
http_web_socket_client_create = lib_function ("http_web_socket_client_create", [], c_void_p, """Creates a client.""")

http_web_socket_client_delete = lib_function (
	"http_web_socket_client_delete", [c_void_p], None,
	"""Closes the connection with 1000, waits for its thread and releases the client.

	It is the last call of a client, from a thread that is not running one of its methods:
	a method of the client that deletes it only closes it.
	"""
)

http_web_socket_client_set_url = lib_function (
	"http_web_socket_client_set_url", [c_void_p, c_char_p], c_uint8,
	"""Sets the URL, ws://host[:port][/path][?query], returns 0 on success."""
)

http_web_socket_client_add_header = lib_function (
	"http_web_socket_client_add_header", [c_void_p, c_char_p, c_char_p], c_uint8,
	"""Adds a header to the request of the handshake, returns 0 on success."""
)

http_web_socket_client_set_protocols = lib_function (
	"http_web_socket_client_set_protocols", [c_void_p, POINTER (c_char_p), c_uint], c_uint8,
	"""Sets the subprotocols that are offered, returns 0 on success."""
)

http_web_socket_client_set_handlers = lib_function (
	"http_web_socket_client_set_handlers", [c_void_p, HttpWebSocketHandlersPointer], None,
	"""Sets the methods of the connections of the client."""
)

http_web_socket_client_set_data = lib_function (
	"http_web_socket_client_set_data", [c_void_p, c_void_p], None,
	"""Sets the data that every connection of the client has."""
)

http_web_socket_client_get_data = lib_function ("http_web_socket_client_get_data", [c_void_p], c_void_p, """Returns the data of the client.""")

http_web_socket_client_set_compression = lib_function (
	"http_web_socket_client_set_compression", [c_void_p, c_bool], None,
	"""Offers permessage-deflate with the default options."""
)

http_web_socket_client_set_compression_options = lib_function (
	"http_web_socket_client_set_compression_options", [c_void_p, HttpWebSocketDeflateOptionsPointer], None,
	"""Sets the options of permessage-deflate of the client."""
)

http_web_socket_client_set_max_message = lib_function (
	"http_web_socket_client_set_max_message", [c_void_p, c_size_t], None,
	"""Sets the most bytes of a message of the client."""
)

http_web_socket_client_set_ping_milliseconds = lib_function (
	"http_web_socket_client_set_ping_milliseconds", [c_void_p, c_uint, c_uint], None,
	"""Sets the pings of the client, in milliseconds."""
)

http_web_socket_client_set_close_timeout_milliseconds = lib_function (
	"http_web_socket_client_set_close_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the close timeout of the client, in milliseconds."""
)

http_web_socket_client_set_send_timeout_milliseconds = lib_function (
	"http_web_socket_client_set_send_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the send timeout of the client, in milliseconds."""
)

http_web_socket_client_set_timeouts_milliseconds = lib_function (
	"http_web_socket_client_set_timeouts_milliseconds", [c_void_p, c_uint, c_uint], None,
	"""Sets the milliseconds of the connect () of each address and of the handshake."""
)

http_web_socket_client_set_reconnect_milliseconds = lib_function (
	"http_web_socket_client_set_reconnect_milliseconds", [c_void_p, c_bool, c_uint, c_uint], None,
	"""Reconnects after an end without a close, waiting from min to max milliseconds.

	The wait is doubled after each failure; a connection that ends before it lasted max milliseconds
	counts as a failure, so a server that accepts and closes is not reconnected without a wait.
	"""
)

http_web_socket_client_connect = lib_function (
	"http_web_socket_client_connect", [c_void_p], c_uint8,
	"""Connects and returns after the handshake, returns 0 on success."""
)

http_web_socket_client_connect_async = lib_function (
	"http_web_socket_client_connect_async", [c_void_p], c_uint8,
	"""Connects in the thread of the connection, returns 0 when the thread started."""
)

http_web_socket_client_get_web_socket = lib_function (
	"http_web_socket_client_get_web_socket", [c_void_p], c_void_p,
	"""Returns the connection of now with a reference (release it), None between connections."""
)

http_web_socket_client_send = lib_function (
	"http_web_socket_client_send", [c_void_p, HttpWebSocketOpcode, c_void_p, c_size_t], c_uint8,
	"""Sends a whole message with the connection of now, returns 0 on success."""
)

http_web_socket_client_send_text = lib_function (
	"http_web_socket_client_send_text", [c_void_p, c_char_p, c_size_t], c_uint8,
	"""Sends a text with the connection of now, returns 0 on success."""
)

http_web_socket_client_send_binary = lib_function (
	"http_web_socket_client_send_binary", [c_void_p, c_void_p, c_size_t], c_uint8,
	"""Sends a binary message with the connection of now, returns 0 on success."""
)

http_web_socket_client_close = lib_function (
	"http_web_socket_client_close", [c_void_p, c_uint16, c_char_p], c_uint8,
	"""Stops the reconnections and starts the closing handshake, returns 0 on success."""
)

http_web_socket_client_wait = lib_function (
	"http_web_socket_client_wait", [c_void_p], None,
	"""Waits until the thread of the client ends; a method of the client does not wait, it runs in that thread."""
)

http_web_socket_client_get_connections = lib_function (
	"http_web_socket_client_get_connections", [c_void_p], c_uint,
	"""Returns the connections that the client opened."""
)

# the helpers of Python

# the status of an upgrade whose on_upgrade () raised
_UPGRADE_FAILED_STATUS = 500

# the protocols that the upgrades chose, kept because cerver reads them after on_upgrade () returns
_protocols: dict = {}

def _bytes (data: Any, size: int) -> bytes:
	return string_at (data, size) if size else b""

def _payload (data: Any) -> bytes:
	"""Returns the bytes of a binary message: a bytearray and a memoryview are copied, anything else is an error."""
	if (isinstance (data, bytes)):
		return data

	if (isinstance (data, (bytearray, memoryview))):
		return bytes (data)

	raise TypeError (f"a binary message is bytes, a bytearray or a memoryview, not {type (data).__name__}")

def _guarded (method: Callable) -> Callable:
	"""Returns a method of a connection whose exceptions never cross into cerver.

	Its traceback is printed and the connection is closed with 1011: ctypes only prints an exception
	of a callback and goes on, so the connection stayed open after a method that failed.
	"""
	def guarded (web_socket: Any, *args: Any) -> None:
		try:
			method (web_socket, *args)

		except Exception:
			traceback.print_exc ()
			http_web_socket_close (web_socket, HTTP_WEB_SOCKET_CLOSE_INTERNAL_ERROR, None)

	return guarded

def _guarded_upgrade (on_upgrade: Callable) -> Callable:
	"""Returns an on_upgrade () that rejects the upgrade with 500 when it raises.

	The value that ctypes returned after an exception decided if the connection was accepted.
	"""
	def guarded (http_receive: Any, request: Any, upgrade: Any) -> bool:
		accepted = False
		try:
			accepted = bool (on_upgrade (http_receive, request, upgrade))

		except Exception:
			traceback.print_exc ()
			upgrade.contents.status = _UPGRADE_FAILED_STATUS

		return accepted

	return guarded

def web_socket_handlers (
	on_upgrade: Callable | None = None, on_open: Callable | None = None,
	on_message: Callable | None = None, on_fragment: Callable | None = None,
	on_ping: Callable | None = None, on_pong: Callable | None = None,
	on_close: Callable | None = None, on_error: Callable | None = None
) -> HttpWebSocketHandlers:
	"""Returns the handlers of Python functions, that are kept until web_socket_handlers_release ().

	The methods take the connection (an int) and bytes instead of pointers and sizes:
	on_message (web_socket, opcode, data), on_fragment (web_socket, opcode, data, first, last),
	on_ping / on_pong (web_socket, data), on_close (web_socket, code, reason) and
	on_error (web_socket, error); on_upgrade (http_receive, request, upgrade) and on_open (web_socket)
	are called as they are.

	An exception of a method closes its connection with 1011, one of on_upgrade () rejects the
	upgrade with 500; its traceback is printed.
	"""
	handlers = HttpWebSocketHandlers ()

	# the callbacks of these handlers as they were kept (a field of the Structure gives a copy of its callback),
	# to release them when their cerver or their client ended
	kept = []

	def keep (method: Callable, callback_type: Any) -> Any:
		callback = callback_wrap (method, callback_type)
		kept.append (callback)

		return callback

	if (on_upgrade):
		handlers.on_upgrade = keep (_guarded_upgrade (on_upgrade), HttpWebSocketOnUpgrade)

	if (on_open):
		handlers.on_open = keep (_guarded (on_open), HttpWebSocketOnOpen)

	if (on_message):
		handlers.on_message = keep (
			_guarded (lambda web_socket, opcode, data, size: on_message (web_socket, opcode, _bytes (data, size))),
			HttpWebSocketOnMessage
		)

	if (on_fragment):
		handlers.on_fragment = keep (
			_guarded (
				lambda web_socket, opcode, data, size, first, last: on_fragment (
					web_socket, opcode, _bytes (data, size), first, last
				)
			),
			HttpWebSocketOnFragment
		)

	if (on_ping):
		handlers.on_ping = keep (
			_guarded (lambda web_socket, data, size: on_ping (web_socket, _bytes (data, size))), HttpWebSocketOnControl
		)

	if (on_pong):
		handlers.on_pong = keep (
			_guarded (lambda web_socket, data, size: on_pong (web_socket, _bytes (data, size))), HttpWebSocketOnControl
		)

	if (on_close):
		handlers.on_close = keep (
			_guarded (lambda web_socket, code, reason, length: on_close (web_socket, code, _bytes (reason, length))),
			HttpWebSocketOnClose
		)

	if (on_error):
		handlers.on_error = keep (_guarded (on_error), HttpWebSocketOnError)

	handlers.kept = kept

	return handlers

def web_socket_handlers_release (handlers: HttpWebSocketHandlers) -> None:
	"""Stops keeping the callbacks of the handlers of web_socket_handlers ().

	Only when cerver will never call them again: their cerver was torn down or their client was deleted.
	A program that creates handlers for each client would keep 8 callbacks per client forever.
	"""
	for callback in getattr (handlers, "kept", []):
		callback_release (callback)

	handlers.kept = []

def web_socket_protocols (protocols: list) -> tuple:
	"""Returns the C array of a list of protocols (bytes or str) and its length."""
	encoded = [protocol.encode () if isinstance (protocol, str) else protocol for protocol in protocols]
	array = (c_char_p * len (encoded)) (*encoded)

	return array, len (encoded)

def web_socket_send (web_socket: Any, data: Any) -> int:
	"""Sends a str as a text and bytes, a bytearray or a memoryview as a binary message.

	Returns:
		0 on success, 1 on error.

	Raises:
		TypeError: The data is of another type.
	"""
	retval = 1
	if (isinstance (data, str)):
		encoded = data.encode ()
		retval = http_web_socket_send_text (web_socket, encoded, len (encoded))

	else:
		payload = _payload (data)
		retval = http_web_socket_send_binary (web_socket, payload, len (payload))

	return retval

def web_socket_close (web_socket: Any, code: int = HTTP_WEB_SOCKET_CLOSE_NORMAL, reason: str = "") -> int:
	"""Starts the closing handshake of a connection, returns 0 on success."""
	return http_web_socket_close (web_socket, code, reason.encode () if reason else None)

@contextmanager
def web_socket_stream (web_socket: Any, opcode: int = HTTP_WEB_SOCKET_OPCODE_TEXT) -> Iterator[Callable]:
	"""A message that is sent in pieces: yields the method that writes each one and ends the message.

	with web_socket_stream (web_socket) as write:
		write ("first ")
		write ("second")

	The method takes a str or bytes and returns 0 on success. A stream that does not begin
	(the connection is closing) raises ConnectionError and is not ended, one that began always is.

	Raises:
		ConnectionError: The stream did not begin.
	"""
	if (http_web_socket_send_begin (web_socket, opcode)):
		raise ConnectionError ("the stream of the connection did not begin")

	def write (data: Any) -> int:
		payload = data.encode () if isinstance (data, str) else _payload (data)
		return http_web_socket_send_write (web_socket, payload, len (payload))

	try:
		yield write

	finally:
		http_web_socket_send_end (web_socket)

class WebSocketReference:
	"""A connection that is kept outside of its methods, with a reference of its own.

	The connection of a method (an int) is released when its last method returns: a send with it
	from another thread or after on_close () reads freed memory. A reference keeps it valid until
	release (), and the sends of a connection that ended only return 1.

	Attributes:
		web_socket: The connection, None after release ().
	"""

	def __init__ (self, web_socket: Any) -> None:
		self.web_socket = http_web_socket_retain (web_socket)

	def send (self, data: Any) -> int:
		"""Sends a str as a text and bytes as a binary message, returns 0 on success."""
		return web_socket_send (self.web_socket, data) if self.web_socket else 1

	def close (self, code: int = HTTP_WEB_SOCKET_CLOSE_NORMAL, reason: str = "") -> int:
		"""Starts the closing handshake of the connection, returns 0 on success."""
		return web_socket_close (self.web_socket, code, reason) if self.web_socket else 1

	def release (self) -> None:
		"""Gives the reference back, the connection is not used through this object anymore."""
		if (self.web_socket):
			http_web_socket_release (self.web_socket)
			self.web_socket = None

	def __enter__ (self) -> "WebSocketReference":
		return self

	def __exit__ (self, *args: Any) -> None:
		self.release ()

	def __del__ (self) -> None:
		self.release ()

def web_socket_keep (web_socket: Any) -> WebSocketReference:
	"""Returns a reference to the connection of a method, to use it after the method returns."""
	return WebSocketReference (web_socket)

def web_socket_accept (key: bytes | str) -> bytes | None:
	"""Returns the Sec-WebSocket-Accept of a key, None when the key is not one."""
	encoded = key.encode () if isinstance (key, str) else key
	accept = create_string_buffer (HTTP_WEB_SOCKET_ACCEPT_SIZE)

	return accept.value if http_web_socket_accept_compute (encoded, len (encoded), accept) else None

def web_socket_delete_data (function: Callable) -> Any:
	"""Returns a kept HttpWebSocketDeleteData of a function that takes the data (an int).

	For upgrade.contents.delete_data and http_web_socket_set_data (): a callback that is created
	in place is collected, and cerver calls it when the connection is released.
	"""
	return callback_wrap (function, HttpWebSocketDeleteData)

def web_socket_upgrade_set_protocol (upgrade: Any, protocol: bytes | str | None) -> None:
	"""Sets the protocol of the response of an upgrade, one that the client offered, or None for none.

	cerver reads it after on_upgrade () returns, so its bytes are kept for as long as the process lives
	(a protocol is one of a few names): a bytes object of the method would already be collected.
	"""
	kept = None
	if (protocol is not None):
		encoded = protocol.encode () if isinstance (protocol, str) else bytes (protocol)
		kept = _protocols.setdefault (encoded, encoded)

	upgrade.contents.protocol = kept

def web_socket_upgrade_add_header (upgrade: Any, name: bytes | str, value: bytes | str) -> int:
	"""Adds a header to the 101 of the connection that on_upgrade () accepts, returns 0 on success."""
	return http_web_socket_upgrade_add_header (
		upgrade,
		name.encode () if isinstance (name, str) else name,
		value.encode () if isinstance (value, str) else value
	)

def web_socket_query (web_socket: Any) -> str | None:
	"""Returns the query of the request of the upgrade as it was sent, None when it had none."""
	query = http_web_socket_get_query (web_socket)

	return string_text (cast (query, StringPointer)) if query else None

def web_socket_stats (http_cerver: Any = None, web_socket: Any = None) -> HttpWebSocketStats | None:
	"""Returns the stats of the WebSocket connections of an HTTP cerver, or the ones of a connection.

	Args:
		http_cerver: The HttpCerver, for the stats of every connection.
		web_socket: A connection, for its messages and its bytes.

	Returns:
		The stats, None on error.
	"""
	stats = HttpWebSocketStats ()

	failed = http_web_socket_get_stats (web_socket, stats) if web_socket \
		else http_cerver_web_socket_get_stats (http_cerver, stats)

	return None if failed else stats
