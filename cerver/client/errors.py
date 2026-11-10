"""The errors of a client: actions that run when an error happens, and the error packets."""

from ctypes import CFUNCTYPE, POINTER, Structure, cast
from ctypes import c_int, c_bool, c_char_p, c_void_p, c_uint8
from typing import Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function

from ..types.string import StringPointer, string_text

__all__ = [
	"CLIENT_MAX_ERRORS",
	"ClientErrorType",
	"CLIENT_ERROR_NONE", "CLIENT_ERROR_CERVER_ERROR", "CLIENT_ERROR_PACKET_ERROR",
	"CLIENT_ERROR_FAILED_AUTH", "CLIENT_ERROR_GET_FILE", "CLIENT_ERROR_SEND_FILE",
	"CLIENT_ERROR_FILE_NOT_FOUND", "CLIENT_ERROR_CREATE_LOBBY", "CLIENT_ERROR_JOIN_LOBBY",
	"CLIENT_ERROR_LEAVE_LOBBY", "CLIENT_ERROR_FIND_LOBBY", "CLIENT_ERROR_GAME_INIT",
	"CLIENT_ERROR_GAME_START", "CLIENT_ERROR_UNKNOWN",
	"ClientErrorWork", "ClientErrorData", "ClientErrorDataPointer",
	"client_error_type_description", "client_error_register", "client_error_unregister",
	"client_error_data_delete", "client_error_packet_generate", "client_error_packet_generate_and_send",
	"client_error_on"
]

CLIENT_MAX_ERRORS = 32

ClientErrorType: TypeAlias = c_int # type: ignore

CLIENT_ERROR_NONE = 0
CLIENT_ERROR_CERVER_ERROR = 1
CLIENT_ERROR_PACKET_ERROR = 2
CLIENT_ERROR_FAILED_AUTH = 3
CLIENT_ERROR_GET_FILE = 4
CLIENT_ERROR_SEND_FILE = 5
CLIENT_ERROR_FILE_NOT_FOUND = 6
CLIENT_ERROR_CREATE_LOBBY = 7
CLIENT_ERROR_JOIN_LOBBY = 8
CLIENT_ERROR_LEAVE_LOBBY = 9
CLIENT_ERROR_FIND_LOBBY = 10
CLIENT_ERROR_GAME_INIT = 11
CLIENT_ERROR_GAME_START = 12
CLIENT_ERROR_UNKNOWN = 13

# void *(*) (void *), it gets a ClientErrorData * that it must release
ClientErrorWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

class ClientErrorData (Structure):
	"""What the work of a client error gets, ``ClientErrorData``.

	Attributes:
		client: The client.
		connection: The connection of the error.
		action_args: The work args that were registered.
		error_message: The message of the error, a StringPointer.
	"""

	_fields_ = [
		("client", c_void_p),
		("connection", c_void_p),

		("action_args", c_void_p),

		("error_message", StringPointer)
	]

ClientErrorDataPointer: TypeAlias = POINTER (ClientErrorData) # type: ignore

client_error_type_description = lib_function (
	"client_error_type_description", [ClientErrorType], c_char_p,
	"""Returns the description of a client error type.

	Args:
		type: A CLIENT_ERROR_* value.

	Returns:
		The description, as bytes.
	"""
)

client_error_register = lib_function (
	"client_error_register",
	[c_void_p, ClientErrorType, c_void_p, c_void_p, c_void_p, c_bool, c_bool],
	c_uint8,
	"""Registers the work that runs when an error of the client happens, it replaces a previous one.

	Args:
		client: The client.
		error_type: A CLIENT_ERROR_* value.
		work: A ClientErrorWork kept by the caller, it gets a ClientErrorData that it must
			release with client_error_data_delete ().
		work_args: The action args of the ClientErrorData.
		delete_action_args: An Action kept by the caller that releases the args, or None.
		create_thread: True to run the work in a new detached thread.
		drop_after_trigger: True to run the work only the first time.

	Returns:
		0 on success, 1 on error.
	"""
)

client_error_unregister = lib_function (
	"client_error_unregister", [c_void_p, ClientErrorType], c_uint8,
	"""Unregisters the work of a client error and releases its args.

	Args:
		client: The client.
		error_type: A CLIENT_ERROR_* value.

	Returns:
		0 on success, 1 on error or if the error was not registered.
	"""
)

client_error_data_delete = lib_function (
	"client_error_data_delete", [c_void_p], None,
	"""Releases the ClientErrorData that a work got.

	Args:
		error_data: The ClientErrorData.
	"""
)

client_error_packet_generate = lib_function (
	"client_error_packet_generate", [ClientErrorType, c_char_p], c_void_p,
	"""Creates an error packet of a client, ready to be sent.

	Args:
		type: A CLIENT_ERROR_* value.
		msg: The message, as bytes.

	Returns:
		The Packet, released with packet_delete (), None on error.
	"""
)

client_error_packet_generate_and_send = lib_function (
	"client_error_packet_generate_and_send",
	[ClientErrorType, c_char_p, c_void_p, c_void_p],
	c_uint8,
	"""Creates and sends an error packet of a client.

	Args:
		type: A CLIENT_ERROR_* value.
		msg: The message, as bytes.
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

def client_error_on (
	client: int, error_type: int,
	method: Callable [[int, int | None, str | None], None],
	create_thread: bool = False, drop_after_trigger: bool = False
) -> int:
	"""Registers a Python method that runs when an error of the client happens.

	The method gets the client, the connection and the message of the error, and the
	ClientErrorData is released after it returns.

	Args:
		client: The client.
		error_type: A CLIENT_ERROR_* value.
		method: Called with (client, connection, message).
		create_thread: True to run the method in a new detached thread.
		drop_after_trigger: True to run the method only the first time.

	Returns:
		0 on success, 1 on error.
	"""
	def work (error_data_ptr: int) -> None:
		error_data = cast (error_data_ptr, ClientErrorDataPointer).contents

		try:
			method (error_data.client, error_data.connection, string_text (error_data.error_message))

		finally:
			client_error_data_delete (error_data_ptr)

	return client_error_register (
		client, error_type, callback_wrap (work, ClientErrorWork),
		None, None, create_thread, drop_after_trigger
	)
