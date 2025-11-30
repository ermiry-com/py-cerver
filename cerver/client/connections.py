"""The connections of a client to a cerver: creation, connect, start, requests, receive and end."""

from ctypes import c_int, c_bool, c_char_p, c_void_p, c_uint, c_uint8, c_uint16

from ..lib import lib_function

from ..network.network import Protocol

__all__ = [
	"CLIENT_NEXT_PACKET_BUFFER_SIZE",
	"client_connection_create", "client_connection_register", "client_connection_unregister",
	"client_connection_get_next_packet",
	"client_connect", "client_connect_to_cerver", "client_connect_async",
	"client_connect_to_cerver_async",
	"client_connection_start", "client_connect_and_start", "client_connect_and_start_async",
	"client_request_to_cerver", "client_request_to_cerver_async", "client_requests_wait",
	"client_receive",
	"client_connection_stop", "client_connection_close", "client_connection_end",
	"client_teardown", "client_teardown_async"
]

# the pieces in which client_connection_get_next_packet () reads a packet
CLIENT_NEXT_PACKET_BUFFER_SIZE = 1 << 12

client_connection_create = lib_function (
	"client_connection_create", [c_void_p, c_char_p, c_uint16, Protocol, c_bool], c_void_p,
	"""Creates a connection of the client, ready to connect.

	Args:
		client: The client.
		ip_address: The ip or the host name, as bytes.
		port: The port.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.
		use_ipv6: True to prefer IPv6 when a host name resolves to both families.

	Returns:
		The connection, None on error.
	"""
)

client_connection_register = lib_function (
	"client_connection_register", [c_void_p, c_void_p], c_int,
	"""Registers an existing connection to the client.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connection_unregister = lib_function (
	"client_connection_unregister", [c_void_p, c_void_p], c_int,
	"""Unregisters a connection from the client.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error or if it is not a connection of the client.
	"""
)

client_connection_get_next_packet = lib_function (
	"client_connection_get_next_packet", [c_void_p, c_void_p], c_uint,
	"""Receives a complete packet from the connection and handles it.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connect = lib_function (
	"client_connect", [c_void_p, c_void_p], c_uint,
	"""Connects a connection of the client, blocking until it connects or fails.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 when it connected, 1 on error.
	"""
)

client_connect_to_cerver = lib_function (
	"client_connect_to_cerver", [c_void_p, c_void_p], c_uint,
	"""Connects a connection of the client to a cerver and receives its info, blocking.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 when it connected, 1 on error.
	"""
)

client_connect_async = lib_function (
	"client_connect_async", [c_void_p, c_void_p], c_uint,
	"""Connects a connection of the client in a new thread.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 when the thread was created, 1 on error.
	"""
)

client_connect_to_cerver_async = lib_function (
	"client_connect_to_cerver_async", [c_void_p, c_void_p], c_uint,
	"""Connects a connection of the client to a cerver in a new thread, and receives its info.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 when the thread was created, 1 on error.
	"""
)

client_connection_start = lib_function (
	"client_connection_start", [c_void_p, c_void_p], c_int,
	"""Starts the threads of a connection that connected, like the one that receives its packets.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connect_and_start = lib_function (
	"client_connect_and_start", [c_void_p, c_void_p], c_int,
	"""Connects a connection of the client and starts it, blocking.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connect_and_start_async = lib_function (
	"client_connect_and_start_async", [c_void_p, c_void_p], c_uint8,
	"""Connects a connection of the client and starts it in a new thread.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 when the thread was created, 1 on error.
	"""
)

client_request_to_cerver = lib_function (
	"client_request_to_cerver", [c_void_p, c_void_p, c_void_p], c_uint,
	"""Sends a request packet and waits for the response, that the handlers of the client handle.

	The response must be a single packet, and the request packet is not deleted.

	Args:
		client: The client.
		connection: The connection.
		request: The Packet of the request.

	Returns:
		0 when the response was handled, 1 on error.
	"""
)

client_request_to_cerver_async = lib_function (
	"client_request_to_cerver_async", [c_void_p, c_void_p, c_void_p], c_uint,
	"""Sends a request packet and handles its response in a new thread.

	CLIENT_EVENT_CONNECTION_DATA is triggered when the response was handled, or wait for
	it with client_requests_wait ().

	Args:
		client: The client.
		connection: The connection.
		request: The Packet of the request.

	Returns:
		0 on success, 1 on error.
	"""
)

client_requests_wait = lib_function (
	"client_requests_wait", [c_void_p], None,
	"""Waits until every async request and connect of the client ended.

	It must not be called from the handlers of the client.

	Args:
		client: The client.
	"""
)

client_receive = lib_function (
	"client_receive", [c_void_p, c_void_p], c_uint,
	"""Receives from the connection into a new buffer and handles the packets.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error (the connection most likely ended).
	"""
)

client_connection_stop = lib_function (
	"client_connection_stop", [c_void_p, c_void_p], c_int,
	"""Closes the socket of a connection without sending a close packet to the cerver.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connection_close = lib_function (
	"client_connection_close", [c_void_p, c_void_p], c_int,
	"""Ends a connection and closes its socket, without deleting it.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connection_end = lib_function (
	"client_connection_end", [c_void_p, c_void_p], c_int,
	"""Ends a connection of the client and deletes it.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_teardown = lib_function (
	"client_teardown", [c_void_p], c_uint8,
	"""Ends every connection and process of the client and deletes it.

	Args:
		client: The client, it must not be used after this call.

	Returns:
		0 on success, 1 on error.
	"""
)

client_teardown_async = lib_function (
	"client_teardown_async", [c_void_p], c_uint8,
	"""Calls client_teardown () in a new thread.

	Args:
		client: The client, it must not be used after this call.

	Returns:
		0 when the thread was created, 1 on error.
	"""
)
