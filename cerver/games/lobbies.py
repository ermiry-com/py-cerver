"""The lobbies of a game cerver and the objects of their requests, encoded by their schemas.

The objects (LobbyCreate, LobbyJoin, LobbyRequest and LobbySummary) are sent with
game_request_send () and read with serializer_decode_bytes (), with the schemas that
serializer_schema () returns by their names (like "lobby_join_request_schema").
"""

from ctypes import POINTER, Structure
from ctypes import c_bool, c_char, c_char_p, c_int, c_int64, c_long, c_uint, c_uint8, c_uint32, c_uint64
from ctypes import c_void_p, byref, cast
from typing import Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function

from ..client.events import ClientEventDataPointer, ClientEventWork
from ..client.events import client_event_data_delete, client_event_register
from ..core.cerver import Action
from ..core.serializers import serializer_schema

from .games import game_request_send

__all__ = [
	"LOBBY_DEFAULT_POLL_TIMEOUT", "LOBBY_DEFAULT_MAX_PLAYERS",
	"LOBBY_ID_SIZE", "LOBBY_GAME_TYPE_SIZE", "LOBBY_PLAYER_ID_SIZE",
	"LOBBY_SUMMARY_PLAYERS_MAX", "LOBBY_OBJECTS_VERSION",
	"LOBBY_CREATE_REQUEST_SCHEMA", "LOBBY_JOIN_REQUEST_SCHEMA", "LOBBY_REQUEST_SCHEMA",
	"LOBBY_PLAYER_SUMMARY_SCHEMA", "LOBBY_SETTINGS_SUMMARY_SCHEMA", "LOBBY_SUMMARY_SCHEMA",
	"LobbyCreate", "LobbyCreatePointer", "LobbyJoin", "LobbyJoinPointer",
	"LobbyRequest", "LobbyRequestPointer",
	"LobbyPlayerSummary", "LobbyPlayerSummaryPointer",
	"LobbySettingsSummary", "LobbySettingsSummaryPointer",
	"LobbySummary", "LobbySummaryPointer",
	"lobby_stats_set_threshold_time", "lobby_stats_print",
	"lobby_new", "lobby_delete", "lobby_reference", "lobby_release", "lobby_comparator",
	"lobby_set_poll_time_out", "lobby_set_handler", "lobby_set_packet_handler",
	"lobby_set_game_settings", "lobby_set_game_data", "lobby_set_update", "lobby_is_running",
	"lobby_get", "lobby_search_by_id", "lobby_teardown", "lobby_poll",
	"lobby_create", "lobby_join", "lobby_leave", "lobby_start", "lobby_player_of_client",
	"lobby_summary_set", "lobby_summary_packet_create", "lobby_send", "lobby_send_to_players",
	"lobby_request_send", "lobby_event_on"
]

LOBBY_DEFAULT_POLL_TIMEOUT = 2000
LOBBY_DEFAULT_MAX_PLAYERS = 4

# the sizes of the texts of the lobby objects, with their NUL
LOBBY_ID_SIZE = 80
LOBBY_GAME_TYPE_SIZE = 64
LOBBY_PLAYER_ID_SIZE = 64

# the players that a LobbySummary sends, a lobby can have more
LOBBY_SUMMARY_PLAYERS_MAX = 32

LOBBY_OBJECTS_VERSION = 1

# the names of the schemas in libcerver, for serializer_schema ()
LOBBY_CREATE_REQUEST_SCHEMA = "lobby_create_request_schema"
LOBBY_JOIN_REQUEST_SCHEMA = "lobby_join_request_schema"
LOBBY_REQUEST_SCHEMA = "lobby_request_schema"
LOBBY_PLAYER_SUMMARY_SCHEMA = "lobby_player_summary_schema"
LOBBY_SETTINGS_SUMMARY_SCHEMA = "lobby_settings_summary_schema"
LOBBY_SUMMARY_SCHEMA = "lobby_summary_schema"

class LobbyCreate (Structure):
	"""The request of a client that creates a lobby of a game type, ``LobbyCreate``."""

	_fields_ = [
		("game_type", c_char * LOBBY_GAME_TYPE_SIZE)
	]

LobbyCreatePointer: TypeAlias = POINTER (LobbyCreate) # type: ignore

class LobbyJoin (Structure):
	"""The request of a client that joins a lobby, ``LobbyJoin``.

	Attributes:
		lobby_id: The lobby, empty to join one of the game type (it is created when none has a place).
		game_type: The game type, required.
	"""

	_fields_ = [
		("lobby_id", c_char * LOBBY_ID_SIZE),
		("game_type", c_char * LOBBY_GAME_TYPE_SIZE)
	]

LobbyJoinPointer: TypeAlias = POINTER (LobbyJoin) # type: ignore

class LobbyRequest (Structure):
	"""A request of a client about a lobby: init, start, leave, update and destroy, ``LobbyRequest``."""

	_fields_ = [
		("lobby_id", c_char * LOBBY_ID_SIZE)
	]

LobbyRequestPointer: TypeAlias = POINTER (LobbyRequest) # type: ignore

class LobbyPlayerSummary (Structure):
	"""A player of a lobby, ``LobbyPlayerSummary``.

	Attributes:
		client_id: The id of its client.
		player_id: Its id, empty if it has none.
		owner: True for the owner of the lobby.
	"""

	_fields_ = [
		("client_id", c_uint64),
		("player_id", c_char * LOBBY_PLAYER_ID_SIZE),
		("owner", c_bool)
	]

LobbyPlayerSummaryPointer: TypeAlias = POINTER (LobbyPlayerSummary) # type: ignore

class LobbySettingsSummary (Structure):
	"""The settings of the game type of a lobby, ``LobbySettingsSummary``."""

	_fields_ = [
		("max_players", c_uint32),
		("player_timeout", c_uint32),
		("fps", c_uint32)
	]

LobbySettingsSummaryPointer: TypeAlias = POINTER (LobbySettingsSummary) # type: ignore

class LobbySummary (Structure):
	"""The state of a lobby that the cerver sends to its players, ``LobbySummary``.

	Attributes:
		created: True when it answers the LOBBY_CREATE that created the lobby.
		players: The first LOBBY_SUMMARY_PLAYERS_MAX players, players_count of them.
	"""

	_fields_ = [
		("id", c_char * LOBBY_ID_SIZE),
		("creation", c_int64),
		("game_type", c_char * LOBBY_GAME_TYPE_SIZE),
		("created", c_bool),
		("running", c_bool),
		("in_game", c_bool),
		("max_players", c_uint32),
		("n_players", c_uint32),
		("owner_client_id", c_uint64),
		("players", LobbyPlayerSummary * LOBBY_SUMMARY_PLAYERS_MAX),
		("players_count", c_uint32),
		("settings", LobbySettingsSummary)
	]

LobbySummaryPointer: TypeAlias = POINTER (LobbySummary) # type: ignore

lobby_stats_set_threshold_time = lib_function (
	"lobby_stats_set_threshold_time", [c_void_p, c_long], None,
	"""Sets how often the stats of a lobby are reset.

	Args:
		lobby: The Lobby.
		threshold_time: The seconds.
	"""
)

lobby_stats_print = lib_function (
	"lobby_stats_print", [c_void_p], None,
	"""Prints the stats of a lobby.

	Args:
		lobby: The Lobby.
	"""
)

lobby_new = lib_function (
	"lobby_new", [], c_void_p,
	"""Allocates a lobby.

	Returns:
		The Lobby, released with lobby_delete () or lobby_release ().
	"""
)

lobby_delete = lib_function (
	"lobby_delete", [c_void_p], None,
	"""Releases a lobby right away, use lobby_release () for a lobby with references.

	Args:
		lobby_ptr: The Lobby.
	"""
)

lobby_reference = lib_function (
	"lobby_reference", [c_void_p], c_void_p,
	"""Takes a reference to a lobby, None is safe.

	Args:
		lobby: The Lobby.

	Returns:
		The same lobby.
	"""
)

lobby_release = lib_function (
	"lobby_release", [c_void_p], None,
	"""Releases a reference to a lobby, the last one deletes it, None is safe.

	Args:
		lobby: The Lobby.
	"""
)

lobby_comparator = lib_function (
	"lobby_comparator", [c_void_p, c_void_p], c_int,
	"""Compares two lobbies by their ids.

	Args:
		one: The first Lobby.
		two: The second one.

	Returns:
		0 when their ids are equal.
	"""
)

lobby_set_poll_time_out = lib_function (
	"lobby_set_poll_time_out", [c_void_p, c_uint], None,
	"""Sets how often the lobby checks for new packets.

	Args:
		lobby: The Lobby.
		timeout: The milliseconds.
	"""
)

lobby_set_handler = lib_function (
	"lobby_set_handler", [c_void_p, Action], None,
	"""Sets the handler of a lobby.

	Args:
		lobby: The Lobby.
		handler: A kept Action.
	"""
)

lobby_set_packet_handler = lib_function (
	"lobby_set_packet_handler", [c_void_p, Action], None,
	"""Sets the handler of the app packets of the players while the lobby runs.

	It gets the packet, which is released after it.

	Args:
		lobby: The Lobby.
		packet_handler: A kept Action.
	"""
)

lobby_set_game_settings = lib_function (
	"lobby_set_game_settings", [c_void_p, c_void_p, Action], None,
	"""Sets the game settings of a lobby and the action that deletes them.

	Args:
		lobby: The Lobby.
		game_settings: The settings.
		game_settings_delete: A kept Action, or None.
	"""
)

lobby_set_game_data = lib_function (
	"lobby_set_game_data", [c_void_p, c_void_p, Action], None,
	"""Sets the game data of a lobby and the action that deletes it.

	Args:
		lobby: The Lobby.
		game_data: The data.
		game_data_delete: A kept Action, or None.
	"""
)

lobby_set_update = lib_function (
	"lobby_set_update", [c_void_p, Action], None,
	"""Sets the update of a lobby, called every frame with a CerverLobby while it runs.

	Args:
		lobby: The Lobby.
		update: A kept Action.
	"""
)

lobby_is_running = lib_function (
	"lobby_is_running", [c_void_p], c_bool,
	"""Returns True while a lobby runs.

	Args:
		lobby: The Lobby.
	"""
)

lobby_get = lib_function (
	"lobby_get", [c_void_p, c_void_p], c_void_p,
	"""Searches a lobby in the game cerver.

	Args:
		game_cerver: The GameCerver.
		query: A Lobby with the id to search.

	Returns:
		A reference to the Lobby (lobby_release ()), None if there is none.
	"""
)

lobby_search_by_id = lib_function (
	"lobby_search_by_id", [c_void_p, c_char_p], c_void_p,
	"""Searches a lobby by its id, with the lock of the game cerver.

	Args:
		cerver: The Cerver.
		id: The id, as bytes.

	Returns:
		The Lobby, None if there is none.
	"""
)

lobby_teardown = lib_function (
	"lobby_teardown", [c_void_p, c_void_p], c_int,
	"""Destroys the game data of a lobby and releases the reference of the game cerver.

	Args:
		game_cerver: The GameCerver.
		lobby: The Lobby.

	Returns:
		0 on success, 1 on error.
	"""
)

lobby_poll = lib_function (
	"lobby_poll", [c_void_p], None,
	"""The default handler of a lobby, it receives the packets of the players while the lobby runs.

	Args:
		ptr: The CerverLobby.
	"""
)

lobby_create = lib_function (
	"lobby_create", [c_void_p, c_void_p, c_bool, Action, c_uint32], c_void_p,
	"""Creates a lobby with a player of the client as its owner.

	Args:
		cerver: The Cerver.
		client: The Client.
		use_default_handler: True to handle its packets with the default handler.
		custom_handler: A kept Action used when use_default_handler is False, or None.
		max_players: The players, 0 takes LOBBY_DEFAULT_MAX_PLAYERS.

	Returns:
		The Lobby, None on error.
	"""
)

lobby_join = lib_function (
	"lobby_join", [c_void_p, c_void_p, c_void_p], c_uint8,
	"""Creates a player of a client in a lobby.

	A full lobby, a lobby in game, a lobby that ended, or a client that already is in it fail.

	Args:
		cerver: The Cerver.
		client: The Client.
		lobby: The Lobby.

	Returns:
		0 on success, 1 on error.
	"""
)

lobby_leave = lib_function (
	"lobby_leave", [c_void_p, c_void_p, c_void_p], c_uint8,
	"""Releases a player that leaves a lobby.

	The owner is given to the next player, and the last player destroys the lobby.

	Args:
		cerver: The Cerver.
		lobby: The Lobby.
		player: The Player.

	Returns:
		0 on success, 1 on error.
	"""
)

lobby_start = lib_function (
	"lobby_start", [c_void_p, c_void_p], c_uint8,
	"""Starts the handler and the update threads of a lobby.

	Args:
		cerver: The Cerver.
		lobby: The Lobby.

	Returns:
		0 on success, 1 on error or if it was already started.
	"""
)

lobby_player_of_client = lib_function (
	"lobby_player_of_client", [c_void_p, c_void_p], c_void_p,
	"""Returns the player of a client in a lobby, with the lock of the game cerver.

	Args:
		lobby: The Lobby.
		client: The Client.

	Returns:
		The Player, None if the client is not in the lobby.
	"""
)

lobby_summary_set = lib_function (
	"lobby_summary_set", [LobbySummaryPointer, c_void_p, c_bool], None,
	"""Fills a summary with the current state of a lobby, with the lock of the game cerver.

	Args:
		summary: The LobbySummary that gets the values.
		lobby: The Lobby.
		created: True when it answers the LOBBY_CREATE that created the lobby.
	"""
)

lobby_summary_packet_create = lib_function (
	"lobby_summary_packet_create", [c_void_p, c_uint32, c_bool], c_void_p,
	"""Creates a GAME packet of a request type with the summary of a lobby.

	Args:
		lobby: The Lobby.
		request_type: A GAME_PACKET_TYPE_* value.
		created: True when it answers the LOBBY_CREATE that created the lobby.

	Returns:
		The Packet, None on error.
	"""
)

lobby_send = lib_function (
	"lobby_send", [c_void_p, c_bool, c_void_p, c_void_p, c_void_p], None,
	"""Sends a lobby to a client, as the response of LOBBY_CREATE or of LOBBY_JOIN.

	Args:
		lobby: The Lobby.
		created: True when it answers the LOBBY_CREATE that created the lobby.
		cerver: The Cerver.
		client: The Client.
		connection: The Connection.
	"""
)

lobby_send_to_players = lib_function (
	"lobby_send_to_players", [c_void_p, c_uint32], None,
	"""Sends the summary of a lobby to every one of its players.

	Args:
		lobby: The Lobby.
		request_type: A GAME_PACKET_TYPE_* value.
	"""
)

# the schema of each request object
LOBBY_REQUEST_SCHEMAS = {
	LobbyCreate: LOBBY_CREATE_REQUEST_SCHEMA,
	LobbyJoin: LOBBY_JOIN_REQUEST_SCHEMA,
	LobbyRequest: LOBBY_REQUEST_SCHEMA
}

def lobby_request_send (client: int, connection: int, request_type: int, request) -> int:
	"""Sends a game request of a client with its object.

	Args:
		client: The Client.
		connection: The Connection to the game cerver.
		request_type: A GAME_PACKET_TYPE_* value.
		request: A LobbyCreate, a LobbyJoin or a LobbyRequest.

	Returns:
		0 on success, 1 on error.

	Raises:
		TypeError: The request is not a lobby request object.
	"""
	name = LOBBY_REQUEST_SCHEMAS.get (type (request))
	if (name is None):
		raise TypeError (f"{type (request).__name__} is not a lobby request")

	return game_request_send (client, connection, request_type, serializer_schema (name), byref (request))

def lobby_event_on (
	client: int, event_type: int,
	method: Callable [[int, int | None, LobbySummary], None],
	create_thread: bool = False, drop_after_trigger: bool = False
) -> int:
	"""Registers a Python method that runs when a client gets a lobby event, like CLIENT_EVENT_LOBBY_JOIN.

	The method gets the client, the connection and a copy of the LobbySummary of the event,
	and the ClientEventData is released after it returns.

	Args:
		client: The Client.
		event_type: A CLIENT_EVENT_LOBBY_* value or CLIENT_EVENT_GAME_INIT.
		method: Called with (client, connection, summary).
		create_thread: True to run the method in a new detached thread.
		drop_after_trigger: True to run the method only the first time.

	Returns:
		0 on success, 1 on error.
	"""
	def work (event_data_ptr: int) -> None:
		event_data = cast (event_data_ptr, ClientEventDataPointer).contents

		try:
			summary = LobbySummary ()
			if (event_data.response_data):
				summary = LobbySummary.from_buffer_copy (cast (event_data.response_data, LobbySummaryPointer).contents)

			method (event_data.client, event_data.connection, summary)

		finally:
			client_event_data_delete (event_data_ptr)

	return client_event_register (
		client, event_type, callback_wrap (work, ClientEventWork), None, None,
		create_thread, drop_after_trigger
	)
