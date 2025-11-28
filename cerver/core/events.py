"""The events of a cerver: actions that run when something happens to it or to its clients."""

from ctypes import CFUNCTYPE, POINTER, Structure, cast
from ctypes import c_int, c_void_p, c_char_p, c_bool, c_uint8
from typing import Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function

__all__ = [
	"CERVER_MAX_EVENTS",
	"CerverEventType",
	"CERVER_EVENT_NONE", "CERVER_EVENT_STARTED", "CERVER_EVENT_TEARDOWN",
	"CERVER_EVENT_ON_HOLD_CONNECTED", "CERVER_EVENT_ON_HOLD_DISCONNECTED",
	"CERVER_EVENT_ON_HOLD_DROPPED",
	"CERVER_EVENT_CLIENT_SUCCESS_AUTH", "CERVER_EVENT_CLIENT_FAILED_AUTH",
	"CERVER_EVENT_CLIENT_CONNECTED", "CERVER_EVENT_CLIENT_NEW_CONNECTION",
	"CERVER_EVENT_CLIENT_CLOSE_CONNECTION", "CERVER_EVENT_CLIENT_DISCONNECTED",
	"CERVER_EVENT_CLIENT_DROPPED",
	"CERVER_EVENT_ADMIN_FAILED_AUTH", "CERVER_EVENT_ADMIN_CONNECTED",
	"CERVER_EVENT_ADMIN_NEW_CONNECTION", "CERVER_EVENT_ADMIN_CLOSE_CONNECTION",
	"CERVER_EVENT_ADMIN_DISCONNECTED", "CERVER_EVENT_ADMIN_DROPPED",
	"CERVER_EVENT_LOBBY_CREATE", "CERVER_EVENT_LOBBY_JOIN",
	"CERVER_EVENT_LOBBY_LEAVE", "CERVER_EVENT_LOBBY_START",
	"CERVER_EVENT_UNKNOWN",
	"CerverEventWork", "CerverEventData", "CerverEventDataPointer",
	"cerver_event_type_description",
	"cerver_event_delete", "cerver_event_register", "cerver_event_unregister",
	"cerver_event_data_delete",
	"cerver_event_on"
]

CERVER_MAX_EVENTS = 32

CerverEventType: TypeAlias = c_int # type: ignore

CERVER_EVENT_NONE = 0
CERVER_EVENT_STARTED = 1
CERVER_EVENT_TEARDOWN = 2
CERVER_EVENT_ON_HOLD_CONNECTED = 3
CERVER_EVENT_ON_HOLD_DISCONNECTED = 4
CERVER_EVENT_ON_HOLD_DROPPED = 5
CERVER_EVENT_CLIENT_SUCCESS_AUTH = 6
CERVER_EVENT_CLIENT_FAILED_AUTH = 7
CERVER_EVENT_CLIENT_CONNECTED = 8
CERVER_EVENT_CLIENT_NEW_CONNECTION = 9
CERVER_EVENT_CLIENT_CLOSE_CONNECTION = 11
CERVER_EVENT_CLIENT_DISCONNECTED = 12
CERVER_EVENT_CLIENT_DROPPED = 13
CERVER_EVENT_ADMIN_FAILED_AUTH = 14
CERVER_EVENT_ADMIN_CONNECTED = 15
CERVER_EVENT_ADMIN_NEW_CONNECTION = 16
CERVER_EVENT_ADMIN_CLOSE_CONNECTION = 17
CERVER_EVENT_ADMIN_DISCONNECTED = 18
CERVER_EVENT_ADMIN_DROPPED = 19
CERVER_EVENT_LOBBY_CREATE = 20
CERVER_EVENT_LOBBY_JOIN = 21
CERVER_EVENT_LOBBY_LEAVE = 22
CERVER_EVENT_LOBBY_START = 23
CERVER_EVENT_UNKNOWN = 24

# void *(*) (void *), it gets a CerverEventData * that it must release
CerverEventWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

class CerverEventData (Structure):
	"""What the work of an event gets, ``CerverEventData``.

	Attributes:
		cerver: The cerver.
		client: The client of the event, None if it has none.
		connection: The connection of the event, None if it has none.
		action_args: The work args that were registered.
		delete_action_args: How the args are released.
	"""

	_fields_ = [
		("cerver", c_void_p),
		("client", c_void_p),
		("connection", c_void_p),

		("action_args", c_void_p),
		("delete_action_args", c_void_p)
	]

CerverEventDataPointer: TypeAlias = POINTER (CerverEventData) # type: ignore

cerver_event_type_description = lib_function (
	"cerver_event_type_description", [CerverEventType], c_char_p,
	"""Returns the description of an event type.

	Args:
		type: A CERVER_EVENT_* value.

	Returns:
		The description, as bytes.
	"""
)

cerver_event_delete = lib_function (
	"cerver_event_delete", [c_void_p], None,
	"""Releases a registered event, cerver_event_unregister () uses it.

	Args:
		event_ptr: The CerverEvent.
	"""
)

cerver_event_register = lib_function (
	"cerver_event_register",
	[c_void_p, CerverEventType, c_void_p, c_void_p, c_void_p, c_bool, c_bool],
	c_uint8,
	"""Registers the work that runs when an event of the cerver happens, it replaces a previous one.

	Args:
		cerver: The cerver.
		event_type: A CERVER_EVENT_* value.
		work: A CerverEventWork kept by the caller, it gets a CerverEventData that it must
			release with cerver_event_data_delete ().
		work_args: The action args of the CerverEventData.
		delete_action_args: An Action kept by the caller that releases the args, or None.
		create_thread: True to run the work in a new detached thread.
		drop_after_trigger: True to run the work only the first time.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_event_unregister = lib_function (
	"cerver_event_unregister", [c_void_p, CerverEventType], c_uint8,
	"""Unregisters the work of an event and releases its args.

	Args:
		cerver: The cerver.
		event_type: A CERVER_EVENT_* value.

	Returns:
		0 on success, 1 on error or if the event was not registered.
	"""
)

cerver_event_data_delete = lib_function (
	"cerver_event_data_delete", [c_void_p], None,
	"""Releases the CerverEventData that a work got.

	Args:
		event_data: The CerverEventData.
	"""
)

def cerver_event_on (
	cerver: int, event_type: int,
	method: Callable [[int, int | None, int | None], None],
	create_thread: bool = False, drop_after_trigger: bool = False
) -> int:
	"""Registers a Python method that runs when an event of the cerver happens.

	The method gets the cerver, the client and the connection of the event, and the
	CerverEventData is released after it returns.

	Args:
		cerver: The cerver.
		event_type: A CERVER_EVENT_* value.
		method: Called with (cerver, client, connection).
		create_thread: True to run the method in a new detached thread.
		drop_after_trigger: True to run the method only the first time.

	Returns:
		0 on success, 1 on error.
	"""
	def work (event_data_ptr: int) -> None:
		event_data = cast (event_data_ptr, CerverEventDataPointer).contents

		try:
			method (event_data.cerver, event_data.client, event_data.connection)

		finally:
			cerver_event_data_delete (event_data_ptr)

	return cerver_event_register (
		cerver, event_type, callback_wrap (work, CerverEventWork),
		None, None, create_thread, drop_after_trigger
	)
