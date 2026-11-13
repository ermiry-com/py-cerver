"""The connections of a client, to a cerver or to any other host."""

from ctypes import CFUNCTYPE, POINTER, Structure
from ctypes import c_int, c_int32, c_bool, c_char_p, c_void_p
from ctypes import c_uint, c_uint8, c_uint16, c_uint32, c_size_t
from typing import TypeAlias

from ..lib import lib_function

from ..network.network import Protocol, PROTOCOL_TCP, SockaddrStoragePointer

__all__ = [
	"CONNECTION_NAME_SIZE", "CONNECTION_IP_SIZE", "CONNECTION_DEFAULT_NAME",
	"CONNECTION_DEFAULT_PROTOCOL", "CONNECTION_DEFAULT_USE_IPV6",
	"CONNECTION_DEFAULT_MAX_SLEEP", "CONNECTION_FIRST_RETRY_SECONDS",
	"CONNECTION_DEFAULT_CONNECT_TIMEOUT", "CONNECTION_CONNECT_POLL_INTERVAL",
	"CONNECTION_DEFAULT_MAX_AUTH_TRIES", "CONNECTION_DEFAULT_BAD_PACKETS",
	"CONNECTION_DEFAULT_RECEIVE_FLAGS", "CONNECTION_DEFAULT_RECEIVE_BUFFER_SIZE",
	"CONNECTION_DATAGRAM_TOKEN_SIZE", "CONNECTION_DEFAULT_UPDATE_TIMEOUT",
	"CONNECTION_DEFAULT_RECEIVE_PACKETS", "CONNECTION_DEFAULT_USE_SEND_QUEUE",
	"CONNECTION_DEFAULT_SEND_FLAGS", "CONNECTION_DEFAULT_ATTEMPT_RECONNECT",
	"CONNECTION_DEFAULT_RECONNECT_WAIT_TIME",
	"ConnectionState",
	"CONNECTION_STATE_NONE", "CONNECTION_STATE_CONNECTING", "CONNECTION_STATE_READY",
	"CONNECTION_STATE_IDLE", "CONNECTION_STATE_WORKING", "CONNECTION_STATE_BUSY",
	"CONNECTION_STATE_UNAVAILABLE", "CONNECTION_STATE_DISCONNECTING", "CONNECTION_STATE_DISCONNECTED",
	"ConnectionCustomReceive", "ConnectionCustomReceiveData", "ConnectionCustomReceiveDataPointer",
	"connection_state_string", "connection_state_description",
	"connection_stats_new", "connection_stats_print",
	"connection_new", "connection_delete", "connection_create_empty",
	"connection_create_complete", "connection_create", "connection_comparator",
	"connection_set_name", "connection_get_values", "connection_set_values",
	"connection_get_state",
	"connection_set_max_sleep", "connection_set_connect_timeout",
	"connection_set_receive", "connection_set_receive_flags", "connection_set_receive_buffer_size",
	"connection_set_received_data", "connection_set_update_timeout", "connection_set_send_timeout",
	"connection_set_custom_receive", "connection_set_send_queue", "connection_send_packet",
	"connection_set_auth_data", "connection_set_auth_object", "connection_set_auth_token",
	"connection_remove_auth_data", "connection_generate_auth_packet",
	"connection_set_attempt_reconnect", "connection_drop_request"
]

CONNECTION_NAME_SIZE = 64
CONNECTION_IP_SIZE = 64
CONNECTION_DEFAULT_NAME = "no-name"

CONNECTION_DEFAULT_PROTOCOL = PROTOCOL_TCP
CONNECTION_DEFAULT_USE_IPV6 = False

# the most secs of the exponential backoff of a connect
CONNECTION_DEFAULT_MAX_SLEEP = 60
CONNECTION_FIRST_RETRY_SECONDS = 2

# how long a connect () to each resolved address can take (ms)
CONNECTION_DEFAULT_CONNECT_TIMEOUT = 4096
CONNECTION_CONNECT_POLL_INTERVAL = 128

CONNECTION_DEFAULT_MAX_AUTH_TRIES = 2
CONNECTION_DEFAULT_BAD_PACKETS = 4

CONNECTION_DEFAULT_RECEIVE_FLAGS = 0
CONNECTION_DEFAULT_RECEIVE_BUFFER_SIZE = 4096

# an authenticated UDP connection sends this token after the packet in every datagram
CONNECTION_DATAGRAM_TOKEN_SIZE = 16

CONNECTION_DEFAULT_UPDATE_TIMEOUT = 2

CONNECTION_DEFAULT_RECEIVE_PACKETS = True

CONNECTION_DEFAULT_USE_SEND_QUEUE = False
CONNECTION_DEFAULT_SEND_FLAGS = 0

CONNECTION_DEFAULT_ATTEMPT_RECONNECT = False
CONNECTION_DEFAULT_RECONNECT_WAIT_TIME = 30

ConnectionState: TypeAlias = c_int # type: ignore

CONNECTION_STATE_NONE = 0
CONNECTION_STATE_CONNECTING = 1
CONNECTION_STATE_READY = 2
CONNECTION_STATE_IDLE = 3
CONNECTION_STATE_WORKING = 4
CONNECTION_STATE_BUSY = 5
CONNECTION_STATE_UNAVAILABLE = 6
CONNECTION_STATE_DISCONNECTING = 7
CONNECTION_STATE_DISCONNECTED = 8

# u8 (*) (void *custom_data_ptr, char *buffer, const size_t buffer_size), returns 0 on success
ConnectionCustomReceive: TypeAlias = CFUNCTYPE (c_uint8, c_void_p, c_void_p, c_size_t) # type: ignore

class ConnectionCustomReceiveData (Structure):
	"""What a custom receive method gets, ``ConnectionCustomReceiveData``.

	Attributes:
		client: The client.
		connection: The connection.
		args: The args that were given with the method.
	"""

	_fields_ = [
		("client", c_void_p),
		("connection", c_void_p),
		("args", c_void_p)
	]

ConnectionCustomReceiveDataPointer: TypeAlias = POINTER (ConnectionCustomReceiveData) # type: ignore

connection_state_string = lib_function (
	"connection_state_string", [ConnectionState], c_char_p,
	"""Returns the name of a connection state.

	Args:
		state: A CONNECTION_STATE_* value.

	Returns:
		The name, as bytes.
	"""
)

connection_state_description = lib_function (
	"connection_state_description", [ConnectionState], c_char_p,
	"""Returns the description of a connection state.

	Args:
		state: A CONNECTION_STATE_* value.

	Returns:
		The description, as bytes.
	"""
)

connection_stats_new = lib_function (
	"connection_stats_new", [], c_void_p,
	"""Allocates the stats of a connection.

	Returns:
		The ConnectionStats.
	"""
)

connection_stats_print = lib_function (
	"connection_stats_print", [c_void_p], None,
	"""Prints the stats of a connection.

	Args:
		connection: The connection.
	"""
)

connection_new = lib_function (
	"connection_new", [], c_void_p,
	"""Allocates an empty connection.

	Returns:
		The Connection, released with connection_delete ().
	"""
)

connection_delete = lib_function (
	"connection_delete", [c_void_p], None,
	"""Releases a connection.

	Args:
		connection_ptr: The Connection.
	"""
)

connection_create_empty = lib_function (
	"connection_create_empty", [], c_void_p,
	"""Creates a connection without its synchronization values.

	Returns:
		The Connection, released with connection_delete ().
	"""
)

connection_create_complete = lib_function (
	"connection_create_complete", [], c_void_p,
	"""Creates an empty connection with its synchronization values, ready to connect to a cerver.

	Returns:
		The Connection, released with connection_delete ().
	"""
)

connection_create = lib_function (
	"connection_create", [c_int32, SockaddrStoragePointer, Protocol], c_void_p,
	"""Creates a connection for an accepted socket.

	Args:
		sock_fd: The socket.
		address: The SockaddrStorage of the peer.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.

	Returns:
		The Connection, released with connection_delete ().
	"""
)

connection_comparator = lib_function (
	"connection_comparator", [c_void_p, c_void_p], c_int,
	"""Compares two connections by their sockets.

	Args:
		a: A Connection.
		b: A Connection.

	Returns:
		Less than, equal to or greater than 0.
	"""
)

connection_set_name = lib_function (
	"connection_set_name", [c_void_p, c_char_p], None,
	"""Sets the name of the connection.

	Args:
		connection: The connection.
		name: The name, as bytes, up to CONNECTION_NAME_SIZE bytes.
	"""
)

connection_get_values = lib_function (
	"connection_get_values", [c_void_p], None,
	"""Sets the ip and the port of the connection from its address.

	Args:
		connection: The connection.
	"""
)

connection_set_values = lib_function (
	"connection_set_values", [c_void_p, c_char_p, c_uint16, Protocol, c_bool], None,
	"""Sets the network values of the connection.

	Args:
		connection: The connection.
		ip_address: The ip or the host name, as bytes.
		port: The port.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.
		use_ipv6: True to prefer IPv6 when a host name resolves to both families.
	"""
)

connection_get_state = lib_function (
	"connection_get_state", [c_void_p], ConnectionState,
	"""Returns the state of the connection.

	Args:
		connection: The connection.

	Returns:
		A CONNECTION_STATE_* value.
	"""
)

connection_set_max_sleep = lib_function (
	"connection_set_max_sleep", [c_void_p, c_uint32], None,
	"""Sets the most seconds of the backoff between the attempts to connect.

	Args:
		connection: The connection.
		max_sleep: The seconds, CONNECTION_DEFAULT_MAX_SLEEP by default.
	"""
)

connection_set_connect_timeout = lib_function (
	"connection_set_connect_timeout", [c_void_p, c_uint32], None,
	"""Sets how long a connect () to each resolved address can take before the next one is tried.

	Args:
		connection: The connection.
		timeout: The milliseconds, CONNECTION_DEFAULT_CONNECT_TIMEOUT by default.
	"""
)

connection_set_receive = lib_function (
	"connection_set_receive", [c_void_p, c_bool], None,
	"""Sets if the connection receives packets in its own thread.

	Args:
		connection: The connection.
		receive: True (the default) to create the thread when it starts.
	"""
)

connection_set_receive_flags = lib_function (
	"connection_set_receive_flags", [c_void_p, c_int], None,
	"""Sets the flags of recv ().

	Args:
		connection: The connection.
		flags: The flags.
	"""
)

connection_set_receive_buffer_size = lib_function (
	"connection_set_receive_buffer_size", [c_void_p, c_uint32], None,
	"""Sets the size of the buffer that receives the packets.

	Args:
		connection: The connection.
		size: The size in bytes.
	"""
)

connection_set_received_data = lib_function (
	"connection_set_received_data", [c_void_p, c_void_p, c_size_t, c_void_p], None,
	"""Sets the data of the response of a request, in a place that is safe to read later.

	Args:
		connection: The connection.
		data: The data.
		data_size: Its size.
		data_delete: An Action kept by the caller that releases it, or None.
	"""
)

connection_set_update_timeout = lib_function (
	"connection_set_update_timeout", [c_void_p, c_uint32], None,
	"""Sets the seconds that the receive thread of the connection waits for data.

	Args:
		connection: The connection.
		timeout: The seconds.
	"""
)

connection_set_send_timeout = lib_function (
	"connection_set_send_timeout", [c_void_p, c_uint32], None,
	"""Sets the seconds that a send waits for space in a full non blocking socket.

	Args:
		connection: The connection.
		timeout: The seconds, 0 uses CERVER_DEFAULT_SEND_TIMEOUT.
	"""
)

connection_set_custom_receive = lib_function (
	"connection_set_custom_receive", [c_void_p, c_void_p, c_void_p, c_void_p], None,
	"""Sets a method that handles the bytes that the connection receives.

	Args:
		connection: The connection.
		custom_receive: A ConnectionCustomReceive kept by the caller, it gets a
			ConnectionCustomReceiveData and the buffer.
		args: The args of the ConnectionCustomReceiveData.
		args_delete: An Action kept by the caller that releases the args, or None.
	"""
)

connection_set_send_queue = lib_function (
	"connection_set_send_queue", [c_void_p, c_int], None,
	"""Sends the packets of connection_send_packet () from a thread of the connection.

	Args:
		connection: The connection.
		flags: The flags of send ().
	"""
)

connection_send_packet = lib_function (
	"connection_send_packet", [c_void_p, c_void_p], None,
	"""Pushes a packet to the send queue of the connection, its thread sends it and deletes it.

	Args:
		connection: The connection.
		packet: The Packet, it must not be used after this call.
	"""
)

connection_set_auth_data = lib_function (
	"connection_set_auth_data", [c_void_p, c_void_p, c_size_t, c_void_p, c_bool], None,
	"""Sets the data that the connection sends when the cerver requires authentication.

	Args:
		connection: The connection.
		auth_data: The data.
		auth_data_size: Its size.
		delete_auth_data: An Action kept by the caller that releases it, or None.
		admin_auth: True to authenticate as an admin.
	"""
)

connection_set_auth_object = lib_function (
	"connection_set_auth_object", [c_void_p, c_void_p, c_void_p, c_bool], c_uint8,
	"""Sets the credentials as an object of the auth schema of the cerver, encoded now.

	Args:
		connection: The connection.
		schema: The address of the SerializerSchema of the credentials.
		object: The address of the object, it can be released after this.
		admin_auth: True to authenticate as an admin.

	Returns:
		0 on success, 1 if the object can not be encoded.
	"""
)

connection_set_auth_token = lib_function (
	"connection_set_auth_token", [c_void_p, c_char_p, c_bool], c_uint8,
	"""Sets the session token that a cerver with sessions gave, to authenticate with it instead of credentials.

	Args:
		connection: The connection.
		token: The token, as bytes.
		admin_auth: True to authenticate as an admin.

	Returns:
		0 on success, 1 on error.
	"""
)

connection_remove_auth_data = lib_function (
	"connection_remove_auth_data", [c_void_p], None,
	"""Releases the auth data of the connection.

	Args:
		connection: The connection.
	"""
)

connection_generate_auth_packet = lib_function (
	"connection_generate_auth_packet", [c_void_p], c_uint8,
	"""Generates the auth packet of the connection from its auth data.

	Args:
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

connection_set_attempt_reconnect = lib_function (
	"connection_set_attempt_reconnect", [c_void_p, c_uint], None,
	"""Reconnects when the cerver ends the connection, until the client ends it.

	Args:
		connection: The connection.
		wait_time: The seconds between the attempts.
	"""
)

connection_drop_request = lib_function (
	"connection_drop_request", [c_void_p], c_uint8,
	"""Asks the cerver to drop a connection from any packet handler.

	The socket is shut down and the receive loop removes the connection when the handler
	returns, so the connection must not be used after this call.

	Args:
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)
