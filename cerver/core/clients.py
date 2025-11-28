"""The clients of a cerver: anyone that connects to it, its connections and how the cerver drops them."""

from ctypes import c_int, c_int32, c_char_p, c_void_p, c_uint8
from typing import TypeAlias

from ..lib import lib_function

from ..network.network import SockaddrStoragePointer

__all__ = [
	"ClientConnectionsStatus",
	"CLIENT_CONNECTIONS_STATUS_NONE", "CLIENT_CONNECTIONS_STATUS_ERROR",
	"CLIENT_CONNECTIONS_STATUS_ONE", "CLIENT_CONNECTIONS_STATUS_DROPPED",
	"client_connections_status_to_string", "client_connections_status_description",
	"client_create_with_connection",
	"client_disconnect", "client_got_disconnected", "client_drop",
	"client_connection_add", "client_connection_remove", "client_connection_drop",
	"client_remove_connection_by_sock_fd",
	"client_get_by_sock_fd", "client_get_by_session_id", "client_broadcast_to_all_avl"
]

ClientConnectionsStatus: TypeAlias = c_int # type: ignore

CLIENT_CONNECTIONS_STATUS_NONE = 0
CLIENT_CONNECTIONS_STATUS_ERROR = 1
CLIENT_CONNECTIONS_STATUS_ONE = 2
CLIENT_CONNECTIONS_STATUS_DROPPED = 3

client_connections_status_to_string = lib_function (
	"client_connections_status_to_string", [ClientConnectionsStatus], c_char_p,
	"""Returns the name of a connections status.

	Args:
		status: A CLIENT_CONNECTIONS_STATUS_* value.

	Returns:
		The name, as bytes.
	"""
)

client_connections_status_description = lib_function (
	"client_connections_status_description", [ClientConnectionsStatus], c_char_p,
	"""Returns the description of a connections status.

	Args:
		status: A CLIENT_CONNECTIONS_STATUS_* value.

	Returns:
		The description, as bytes.
	"""
)

client_create_with_connection = lib_function (
	"client_create_with_connection", [c_void_p, c_int32, SockaddrStoragePointer], c_void_p,
	"""Creates a client of a cerver with a connection for an accepted socket.

	Args:
		cerver: The cerver.
		sock_fd: The socket.
		address: The SockaddrStorage of the peer.

	Returns:
		The Client.
	"""
)

client_disconnect = lib_function (
	"client_disconnect", [c_void_p], c_uint8,
	"""Closes every connection of a client.

	Args:
		client: The client.

	Returns:
		0 on success, 1 on error.
	"""
)

client_got_disconnected = lib_function (
	"client_got_disconnected", [c_void_p], None,
	"""Clears the data of a client that the cerver disconnected.

	Args:
		client: The client.
	"""
)

client_drop = lib_function (
	"client_drop", [c_void_p, c_void_p], None,
	"""Unregisters a client from a cerver and deletes it.

	Args:
		cerver: The cerver.
		client: The client.
	"""
)

client_connection_add = lib_function (
	"client_connection_add", [c_void_p, c_void_p], c_uint8,
	"""Adds a connection to a client, without registering it anywhere else.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connection_remove = lib_function (
	"client_connection_remove", [c_void_p, c_void_p], c_uint8,
	"""Removes a connection from a client.

	Args:
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_connection_drop = lib_function (
	"client_connection_drop", [c_void_p, c_void_p, c_void_p], c_uint8,
	"""Closes a connection, removes it from its client and deletes it.

	Args:
		cerver: The cerver.
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

client_remove_connection_by_sock_fd = lib_function (
	"client_remove_connection_by_sock_fd", [c_void_p, c_void_p, c_int32], ClientConnectionsStatus,
	"""Drops the connection of a socket, and the client of the cerver if it was its last one.

	Args:
		cerver: The cerver.
		client: The client.
		sock_fd: The socket of the connection.

	Returns:
		A CLIENT_CONNECTIONS_STATUS_* value.
	"""
)

client_get_by_sock_fd = lib_function (
	"client_get_by_sock_fd", [c_void_p, c_int32], c_void_p,
	"""Returns the client of a cerver that has the connection of a socket.

	Args:
		cerver: The cerver.
		sock_fd: The socket.

	Returns:
		The client, None if there is none.
	"""
)

client_get_by_session_id = lib_function (
	"client_get_by_session_id", [c_void_p, c_char_p], c_void_p,
	"""Returns the client of a cerver with sessions that has a session id.

	Args:
		cerver: The cerver.
		session_id: The session id, as bytes.

	Returns:
		The client, None if there is none.
	"""
)

client_broadcast_to_all_avl = lib_function (
	"client_broadcast_to_all_avl", [c_void_p, c_void_p, c_void_p], None,
	"""Sends a packet to every client of an AVL node of a cerver.

	Args:
		node: The AVLNode of the clients of the cerver.
		cerver: The cerver.
		packet: The Packet.
	"""
)
