"""The errors of a cerver: actions that run when an error happens, and the error packets."""

from ctypes import CFUNCTYPE, POINTER, Structure, cast
from ctypes import c_int, c_void_p, c_char_p, c_bool, c_uint8
from typing import Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function

from ..types.string import StringPointer, string_text

__all__ = [
	"CERVER_MAX_ERRORS", "ERROR_MESSAGE_LENGTH",
	"CerverErrorType",
	"CERVER_ERROR_NONE", "CERVER_ERROR_CERVER_ERROR", "CERVER_ERROR_PACKET_ERROR",
	"CERVER_ERROR_FAILED_AUTH", "CERVER_ERROR_GET_FILE", "CERVER_ERROR_SEND_FILE",
	"CERVER_ERROR_FILE_NOT_FOUND", "CERVER_ERROR_CREATE_LOBBY", "CERVER_ERROR_JOIN_LOBBY",
	"CERVER_ERROR_LEAVE_LOBBY", "CERVER_ERROR_FIND_LOBBY", "CERVER_ERROR_GAME_INIT",
	"CERVER_ERROR_GAME_START", "CERVER_ERROR_DESTROY_LOBBY", "CERVER_ERROR_UNKNOWN",
	"CerverErrorWork", "CerverErrorEventData", "CerverErrorEventDataPointer",
	"cerver_error_type_description",
	"cerver_error_event_delete", "cerver_error_event_register", "cerver_error_event_unregister",
	"cerver_error_event_data_delete",
	"error_packet_generate", "error_packet_generate_and_send",
	"cerver_error_on"
]

CERVER_MAX_ERRORS = 32

ERROR_MESSAGE_LENGTH = 128

CerverErrorType: TypeAlias = c_int # type: ignore

CERVER_ERROR_NONE = 0
CERVER_ERROR_CERVER_ERROR = 1
CERVER_ERROR_PACKET_ERROR = 2
CERVER_ERROR_FAILED_AUTH = 3
CERVER_ERROR_GET_FILE = 4
CERVER_ERROR_SEND_FILE = 5
CERVER_ERROR_FILE_NOT_FOUND = 6
CERVER_ERROR_CREATE_LOBBY = 7
CERVER_ERROR_JOIN_LOBBY = 8
CERVER_ERROR_LEAVE_LOBBY = 9
CERVER_ERROR_FIND_LOBBY = 10
CERVER_ERROR_GAME_INIT = 11
CERVER_ERROR_GAME_START = 12
CERVER_ERROR_DESTROY_LOBBY = 13
CERVER_ERROR_UNKNOWN = 14

# void *(*) (void *), it gets a CerverErrorEventData * that it must release
CerverErrorWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

class CerverErrorEventData (Structure):
	"""What the work of an error gets, ``CerverErrorEventData``.

	Attributes:
		cerver: The cerver.
		client: The client of the error, None if it has none.
		connection: The connection of the error, None if it has none.
		action_args: The work args that were registered.
		delete_action_args: How the args are released.
		owns_action_args: The error was dropped after this trigger, so
			cerver_error_event_data_delete () releases the args with delete_action_args.
		error_message: The message of the error, a StringPointer.
	"""

	_fields_ = [
		("cerver", c_void_p),
		("client", c_void_p),
		("connection", c_void_p),

		("action_args", c_void_p),

		("delete_action_args", c_void_p),
		("owns_action_args", c_bool),

		("error_message", StringPointer)
	]

CerverErrorEventDataPointer: TypeAlias = POINTER (CerverErrorEventData) # type: ignore

cerver_error_type_description = lib_function (
	"cerver_error_type_description", [CerverErrorType], c_char_p,
	"""Returns the description of an error type.

	Args:
		type: A CERVER_ERROR_* value.

	Returns:
		The description, as bytes.
	"""
)

cerver_error_event_delete = lib_function (
	"cerver_error_event_delete", [c_void_p], None,
	"""Releases a registered error event, cerver_error_event_unregister () uses it.

	Args:
		event_ptr: The CerverErrorEvent.
	"""
)

cerver_error_event_register = lib_function (
	"cerver_error_event_register",
	[c_void_p, CerverErrorType, c_void_p, c_void_p, c_void_p, c_bool, c_bool],
	c_uint8,
	"""Registers the work that runs when an error of the cerver happens, it replaces a previous one.

	Args:
		cerver: The cerver.
		error_type: A CERVER_ERROR_* value.
		work: A CerverErrorWork kept by the caller, it gets a CerverErrorEventData that it
			must release with cerver_error_event_data_delete ().
		work_args: The action args of the CerverErrorEventData.
		delete_action_args: An Action kept by the caller that releases the args, or None.
		create_thread: True to run the work in a new detached thread.
		drop_after_trigger: True to run the work only the first time.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_error_event_unregister = lib_function (
	"cerver_error_event_unregister", [c_void_p, CerverErrorType], c_uint8,
	"""Unregisters the work of an error and releases its args.

	Args:
		cerver: The cerver.
		error_type: A CERVER_ERROR_* value.

	Returns:
		0 on success, 1 on error or if the error was not registered.
	"""
)

cerver_error_event_data_delete = lib_function (
	"cerver_error_event_data_delete", [c_void_p], None,
	"""Releases the CerverErrorEventData that a work got.

	Args:
		error_event_data: The CerverErrorEventData.
	"""
)

error_packet_generate = lib_function (
	"error_packet_generate", [CerverErrorType, c_char_p], c_void_p,
	"""Creates an error packet ready to be sent.

	Args:
		type: A CERVER_ERROR_* value.
		msg: The message, as bytes, up to ERROR_MESSAGE_LENGTH bytes.

	Returns:
		The packet, that must be released with packet_delete (), None on error.
	"""
)

error_packet_generate_and_send = lib_function (
	"error_packet_generate_and_send",
	[CerverErrorType, c_char_p, c_void_p, c_void_p, c_void_p],
	c_uint8,
	"""Creates and sends an error packet to a connection.

	Args:
		type: A CERVER_ERROR_* value.
		msg: The message, as bytes.
		cerver: The cerver.
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

def cerver_error_on (
	cerver: int, error_type: int,
	method: Callable [[int, int | None, int | None, str | None], None],
	create_thread: bool = False, drop_after_trigger: bool = False
) -> int:
	"""Registers a Python method that runs when an error of the cerver happens.

	The method gets the cerver, the client, the connection and the message of the error,
	and the CerverErrorEventData is released after it returns.

	Args:
		cerver: The cerver.
		error_type: A CERVER_ERROR_* value.
		method: Called with (cerver, client, connection, message).
		create_thread: True to run the method in a new detached thread.
		drop_after_trigger: True to run the method only the first time.

	Returns:
		0 on success, 1 on error.
	"""
	def work (error_data_ptr: int) -> None:
		error_data = cast (error_data_ptr, CerverErrorEventDataPointer).contents

		try:
			method (
				error_data.cerver, error_data.client, error_data.connection,
				string_text (error_data.error_message)
			)

		finally:
			cerver_error_event_data_delete (error_data_ptr)

	return cerver_error_event_register (
		cerver, error_type, callback_wrap (work, CerverErrorWork),
		None, None, create_thread, drop_after_trigger
	)
