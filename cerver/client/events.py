"""The events of a client: actions that run when something happens to its connections."""

from ctypes import CFUNCTYPE, POINTER, Structure, cast
from ctypes import c_int, c_bool, c_char_p, c_void_p, c_uint8
from typing import Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function

__all__ = [
	"CLIENT_MAX_EVENTS",
	"ClientEventType",
	"CLIENT_EVENT_NONE", "CLIENT_EVENT_CONNECTED", "CLIENT_EVENT_DISCONNECTED",
	"CLIENT_EVENT_CONNECTION_FAILED", "CLIENT_EVENT_CONNECTION_CLOSE", "CLIENT_EVENT_CONNECTION_DATA",
	"CLIENT_EVENT_CERVER_INFO", "CLIENT_EVENT_CERVER_TEARDOWN", "CLIENT_EVENT_CERVER_STATS",
	"CLIENT_EVENT_CERVER_GAME_STATS", "CLIENT_EVENT_AUTH_SENT", "CLIENT_EVENT_SUCCESS_AUTH",
	"CLIENT_EVENT_MAX_AUTH_TRIES", "CLIENT_EVENT_LOBBY_CREATE", "CLIENT_EVENT_LOBBY_JOIN",
	"CLIENT_EVENT_LOBBY_LEAVE", "CLIENT_EVENT_LOBBY_START", "CLIENT_EVENT_LOBBY_UPDATE",
	"CLIENT_EVENT_LOBBY_DESTROY", "CLIENT_EVENT_GAME_INIT", "CLIENT_EVENT_UNKNOWN",
	"ClientEventWork", "ClientEventData", "ClientEventDataPointer",
	"client_event_type_description", "client_event_register", "client_event_unregister",
	"client_event_data_delete", "client_event_on"
]

CLIENT_MAX_EVENTS = 32

ClientEventType: TypeAlias = c_int # type: ignore

CLIENT_EVENT_NONE = 0
CLIENT_EVENT_CONNECTED = 1
CLIENT_EVENT_DISCONNECTED = 2
CLIENT_EVENT_CONNECTION_FAILED = 3
CLIENT_EVENT_CONNECTION_CLOSE = 4
CLIENT_EVENT_CONNECTION_DATA = 5
CLIENT_EVENT_CERVER_INFO = 6
CLIENT_EVENT_CERVER_TEARDOWN = 7
CLIENT_EVENT_CERVER_STATS = 8
CLIENT_EVENT_CERVER_GAME_STATS = 9
CLIENT_EVENT_AUTH_SENT = 10
CLIENT_EVENT_SUCCESS_AUTH = 11
CLIENT_EVENT_MAX_AUTH_TRIES = 12
CLIENT_EVENT_LOBBY_CREATE = 13
CLIENT_EVENT_LOBBY_JOIN = 14
CLIENT_EVENT_LOBBY_LEAVE = 15
CLIENT_EVENT_LOBBY_START = 16
CLIENT_EVENT_LOBBY_UPDATE = 17
CLIENT_EVENT_LOBBY_DESTROY = 18
CLIENT_EVENT_GAME_INIT = 19
CLIENT_EVENT_UNKNOWN = 20

# void *(*) (void *), it gets a ClientEventData * that it must release
ClientEventWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

class ClientEventData (Structure):
	"""What the work of a client event gets, ``ClientEventData``.

	Attributes:
		client: The client.
		connection: The connection of the event.
		response_data: The data that came with the response.
		delete_response_data: How the response data is released.
		owns_response_data: client_event_data_delete () releases the response of this event only,
			like the LobbySummary of the lobby events.
		action_args: The work args that were registered.
		delete_action_args: How the args are released.
		owns_action_args: The event was dropped after this trigger, so
			client_event_data_delete () releases the args with delete_action_args.
	"""

	_fields_ = [
		("client", c_void_p),
		("connection", c_void_p),

		("response_data", c_void_p),
		("delete_response_data", c_void_p),

		("owns_response_data", c_bool),

		("action_args", c_void_p),
		("delete_action_args", c_void_p),

		("owns_action_args", c_bool)
	]

ClientEventDataPointer: TypeAlias = POINTER (ClientEventData) # type: ignore

client_event_type_description = lib_function (
	"client_event_type_description", [ClientEventType], c_char_p,
	"""Returns the description of a client event type.

	Args:
		type: A CLIENT_EVENT_* value.

	Returns:
		The description, as bytes.
	"""
)

client_event_register = lib_function (
	"client_event_register",
	[c_void_p, ClientEventType, c_void_p, c_void_p, c_void_p, c_bool, c_bool],
	c_uint8,
	"""Registers the work that runs when an event of the client happens, it replaces a previous one.

	Args:
		client: The client.
		event_type: A CLIENT_EVENT_* value.
		work: A ClientEventWork kept by the caller, it gets a ClientEventData that it must
			release with client_event_data_delete ().
		work_args: The action args of the ClientEventData.
		delete_action_args: An Action kept by the caller that releases the args, or None.
		create_thread: True to run the work in a new detached thread.
		drop_after_trigger: True to run the work only the first time.

	Returns:
		0 on success, 1 on error.
	"""
)

client_event_unregister = lib_function (
	"client_event_unregister", [c_void_p, ClientEventType], c_uint8,
	"""Unregisters the work of a client event and releases its args.

	Args:
		client: The client.
		event_type: A CLIENT_EVENT_* value.

	Returns:
		0 on success, 1 on error or if the event was not registered.
	"""
)

client_event_data_delete = lib_function (
	"client_event_data_delete", [c_void_p], None,
	"""Releases the ClientEventData that a work got.

	Args:
		event_data: The ClientEventData.
	"""
)

def client_event_on (
	client: int, event_type: int,
	method: Callable [[int, int | None], None],
	create_thread: bool = False, drop_after_trigger: bool = False
) -> int:
	"""Registers a Python method that runs when an event of the client happens.

	The method gets the client and the connection of the event, and the ClientEventData is
	released after it returns.

	Args:
		client: The client.
		event_type: A CLIENT_EVENT_* value.
		method: Called with (client, connection).
		create_thread: True to run the method in a new detached thread.
		drop_after_trigger: True to run the method only the first time.

	Returns:
		0 on success, 1 on error.
	"""
	def work (event_data_ptr: int) -> None:
		event_data = cast (event_data_ptr, ClientEventDataPointer).contents

		try:
			method (event_data.client, event_data.connection)

		finally:
			client_event_data_delete (event_data_ptr)

	return client_event_register (
		client, event_type, callback_wrap (work, ClientEventWork),
		None, None, create_thread, drop_after_trigger
	)
