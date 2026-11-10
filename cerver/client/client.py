"""A client that connects to a cerver: its creation, its values, its handlers and its settings."""

from ctypes import create_string_buffer
from ctypes import c_int, c_bool, c_char_p, c_void_p, c_uint8, c_size_t
from typing import TypeAlias

from ..lib import lib_function, lib_text

from ..network.network import MAX_UDP_PACKET_SIZE

__all__ = [
	"CLIENT_NAME_SIZE", "CLIENT_DEFAULT_NAME",
	"CLIENT_DEFAULT_MAX_RECEIVED_PACKET_SIZE", "CLIENT_DEFAULT_MAX_BAD_PACKETS",
	"CLIENT_SESSION_ID_SIZE",
	"ClientHandlerError",
	"CLIENT_HANDLER_ERROR_NONE", "CLIENT_HANDLER_ERROR_PACKET", "CLIENT_HANDLER_ERROR_CLOSED",
	"client_stats_print",
	"client_new", "client_delete", "client_delete_dummy", "client_create",
	"client_set_name", "client_set_session_id", "client_get_session_id",
	"client_get_data", "client_set_data",
	"client_set_app_handlers", "client_set_custom_handler",
	"client_set_max_received_packet_size", "client_set_check_packets", "client_set_max_bad_packets",
	"client_comparator_client_id", "client_comparator_session_id",
	"client_is_running",
	"client_handler_error_to_string", "client_handler_error_description",
	"client_session_id"
]

CLIENT_NAME_SIZE = 64
CLIENT_DEFAULT_NAME = "no-name"

CLIENT_DEFAULT_MAX_RECEIVED_PACKET_SIZE = MAX_UDP_PACKET_SIZE
CLIENT_DEFAULT_MAX_BAD_PACKETS = 16

# the buffer of client_session_id ()
CLIENT_SESSION_ID_SIZE = 1 << 8

ClientHandlerError: TypeAlias = c_int # type: ignore

CLIENT_HANDLER_ERROR_NONE = 0
CLIENT_HANDLER_ERROR_PACKET = 1
CLIENT_HANDLER_ERROR_CLOSED = 2

client_stats_print = lib_function (
	"client_stats_print", [c_void_p], None,
	"""Prints the stats of a client.

	Args:
		client: The client.
	"""
)

client_new = lib_function (
	"client_new", [], c_void_p,
	"""Allocates an empty client.

	Returns:
		The Client, released with client_delete ().
	"""
)

client_delete = lib_function (
	"client_delete", [c_void_p], None,
	"""Releases a client with its data.

	Args:
		ptr: The Client.
	"""
)

client_delete_dummy = lib_function (
	"client_delete_dummy", [c_void_p], None,
	"""Does nothing, for the structures that need a delete function but must keep the client.

	Args:
		ptr: The Client.
	"""
)

client_create = lib_function (
	"client_create", [], c_void_p,
	"""Creates a client, ready to create connections to a cerver.

	Returns:
		The Client, released with client_teardown ().
	"""
)

client_set_name = lib_function (
	"client_set_name", [c_void_p, c_char_p], None,
	"""Sets the name of the client.

	Args:
		client: The client.
		name: The name, as bytes, up to CLIENT_NAME_SIZE bytes.
	"""
)

client_set_session_id = lib_function (
	"client_set_session_id", [c_void_p, c_char_p], c_uint8,
	"""Sets the session id of the client.

	Args:
		client: The client.
		session_id: The session id, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

client_get_session_id = lib_function (
	"client_get_session_id", [c_void_p, c_void_p, c_size_t], c_size_t,
	"""Copies the session id of the client into a buffer, use client_session_id ().

	Args:
		client: The client.
		session_id: A writable buffer.
		size: The size of the buffer.

	Returns:
		The bytes that were copied, 0 if the client has no session id.
	"""
)

client_get_data = lib_function (
	"client_get_data", [c_void_p], c_void_p,
	"""Returns the app data of the client.

	Args:
		client: The client.

	Returns:
		The data, None if it has none.
	"""
)

client_set_data = lib_function (
	"client_set_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets the app data of the client, releasing the previous one.

	Args:
		client: The client.
		data: The data.
		delete_data: An Action kept by the caller that releases it, or None.
	"""
)

client_set_app_handlers = lib_function (
	"client_set_app_handlers", [c_void_p, c_void_p, c_void_p], None,
	"""Sets the handlers of the PACKET_TYPE_APP and PACKET_TYPE_APP_ERROR packets of the client.

	Args:
		client: The client.
		app_handler: A Handler of handler_create (), or None.
		app_error_handler: A Handler of handler_create (), or None.
	"""
)

client_set_custom_handler = lib_function (
	"client_set_custom_handler", [c_void_p, c_void_p], None,
	"""Sets the handler of the PACKET_TYPE_CUSTOM packets of the client.

	Args:
		client: The client.
		custom_handler: A Handler of handler_create (), or None.
	"""
)

client_set_max_received_packet_size = lib_function (
	"client_set_max_received_packet_size", [c_void_p, c_size_t], None,
	"""Sets the biggest packet that the client handles, a bigger one is a bad packet.

	Args:
		client: The client.
		max_received_packet_size: The size in bytes.
	"""
)

client_set_check_packets = lib_function (
	"client_set_check_packets", [c_void_p, c_bool], None,
	"""Sets if the protocol of every packet is checked with packet_check ().

	Args:
		client: The client.
		check_packets: True to check them, False by default.
	"""
)

client_set_max_bad_packets = lib_function (
	"client_set_max_bad_packets", [c_void_p, c_uint8], None,
	"""Sets the bad packets of a connection before the client ends it.

	Args:
		client: The client.
		max_bad_packets: The number of bad packets, 0 disables the limit.
	"""
)

client_comparator_client_id = lib_function (
	"client_comparator_client_id", [c_void_p, c_void_p], c_int,
	"""Compares two clients by their ids.

	Args:
		a: A Client.
		b: A Client.

	Returns:
		Less than, equal to or greater than 0.
	"""
)

client_comparator_session_id = lib_function (
	"client_comparator_session_id", [c_void_p, c_void_p], c_int,
	"""Compares two clients by their session ids.

	Args:
		a: A Client.
		b: A Client.

	Returns:
		Less than, equal to or greater than 0.
	"""
)

client_is_running = lib_function (
	"client_is_running", [c_void_p], c_bool,
	"""Returns if the client is running.

	Args:
		client: The client.

	Returns:
		True while it runs.
	"""
)

client_handler_error_to_string = lib_function (
	"client_handler_error_to_string", [ClientHandlerError], c_char_p,
	"""Returns the name of a client handler error.

	Args:
		error: A CLIENT_HANDLER_ERROR_* value.

	Returns:
		The name, as bytes.
	"""
)

client_handler_error_description = lib_function (
	"client_handler_error_description", [ClientHandlerError], c_char_p,
	"""Returns the description of a client handler error.

	Args:
		error: A CLIENT_HANDLER_ERROR_* value.

	Returns:
		The description, as bytes.
	"""
)

def client_session_id (client: int) -> str | None:
	"""Returns the session id of a client.

	Args:
		client: The client.

	Returns:
		The session id, None if it has none.
	"""
	result = None

	buffer = create_string_buffer (CLIENT_SESSION_ID_SIZE)
	if (client_get_session_id (client, buffer, CLIENT_SESSION_ID_SIZE)):
		result = lib_text (buffer.value)

	return result
