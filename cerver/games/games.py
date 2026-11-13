"""The game cerver: its lobbies, its game types, its players and the requests of a game client.

A cerver of CERVER_TYPE_GAME keeps a GameCerver as its data. The callbacks (Action, Comparator
and LobbyIdGenerator) must be kept while cerver can call them (see cerver.callbacks).
"""

from ctypes import CFUNCTYPE
from ctypes import c_int, c_uint8, c_uint32, c_void_p
from typing import TypeAlias

from ..lib import lib_function

from ..core.cerver import Action

__all__ = [
	"GAME_DEFAULT_PLAYER_TIMEOUT", "GAME_DEFAULT_FPS",
	"GAME_DEFAULT_MIN_PLAYERS", "GAME_DEFAULT_MAX_PLAYERS",
	"Comparator", "LobbyIdGenerator",
	"game_cerver_stats_print", "game_new", "game_delete", "game_cerver_lock", "game_cerver_unlock",
	"game_set_cerver_reference", "lobby_default_id_generator", "game_set_lobby_id_generator",
	"game_set_player_comparator", "game_set_load_game_data", "game_set_final_action",
	"game_cerver_register_lobby", "game_cerver_unregister_lobby", "game_request_send"
]

GAME_DEFAULT_PLAYER_TIMEOUT = 30
GAME_DEFAULT_FPS = 20
GAME_DEFAULT_MIN_PLAYERS = 2
GAME_DEFAULT_MAX_PLAYERS = 4

# int (*) (const void *, const void *), returns 0 when both are equal
Comparator: TypeAlias = CFUNCTYPE (c_int, c_void_p, c_void_p) # type: ignore

# void *(*) (const void *), returns the id of a new lobby allocated with malloc ()
LobbyIdGenerator: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

game_cerver_stats_print = lib_function (
	"game_cerver_stats_print", [c_void_p], None,
	"""Prints the stats of the game cerver of a cerver.

	Args:
		cerver: The Cerver.
	"""
)

game_new = lib_function (
	"game_new", [], c_void_p,
	"""Allocates a game cerver.

	Returns:
		The GameCerver, released with game_delete ().
	"""
)

game_delete = lib_function (
	"game_delete", [c_void_p], None,
	"""Releases a game cerver.

	Args:
		game_ptr: The GameCerver.
	"""
)

game_cerver_lock = lib_function (
	"game_cerver_lock", [c_void_p], None,
	"""Takes the recursive lock of the game cerver of a cerver, None is safe.

	Args:
		cerver: The Cerver.
	"""
)

game_cerver_unlock = lib_function (
	"game_cerver_unlock", [c_void_p], None,
	"""Releases the lock of the game cerver of a cerver, None is safe.

	Args:
		cerver: The Cerver.
	"""
)

game_set_cerver_reference = lib_function (
	"game_set_cerver_reference", [c_void_p, c_void_p], None,
	"""Sets the cerver of a game cerver.

	Args:
		game_cerver: The GameCerver.
		cerver: The Cerver.
	"""
)

lobby_default_id_generator = lib_function (
	"lobby_default_id_generator", [c_void_p], c_void_p,
	"""The default id of a lobby: the hash of the creation time and a counter.

	Args:
		data_ptr: Not used.

	Returns:
		The id, allocated with malloc ().
	"""
)

game_set_lobby_id_generator = lib_function (
	"game_set_lobby_id_generator", [c_void_p, LobbyIdGenerator], None,
	"""Sets the function that creates the ids of the lobbies.

	Args:
		game_cerver: The GameCerver.
		lobby_id_generator: A kept LobbyIdGenerator.
	"""
)

game_set_player_comparator = lib_function (
	"game_set_player_comparator", [c_void_p, Comparator], None,
	"""Sets the comparator of the players of the lobbies.

	Args:
		game_cerver: The GameCerver.
		player_comparator: A kept Comparator.
	"""
)

game_set_load_game_data = lib_function (
	"game_set_load_game_data", [c_void_p, Action, Action], None,
	"""Sets the actions that load the game data when the cerver starts and delete it.

	Args:
		game_cerver: The GameCerver.
		load_game_data: A kept Action.
		delete_game_data: A kept Action.
	"""
)

game_set_final_action = lib_function (
	"game_set_final_action", [c_void_p, Action, c_void_p], None,
	"""Sets the action that runs right before the teardown of the game cerver.

	Args:
		game_cerver: The GameCerver.
		final_action: A kept Action.
		final_action_args: Its arguments.
	"""
)

game_cerver_register_lobby = lib_function (
	"game_cerver_register_lobby", [c_void_p, c_void_p], None,
	"""Registers a lobby in the game cerver.

	Args:
		game_cerver: The GameCerver.
		lobby: The Lobby.
	"""
)

game_cerver_unregister_lobby = lib_function (
	"game_cerver_unregister_lobby", [c_void_p, c_void_p], None,
	"""Unregisters a lobby of the game cerver.

	Args:
		game_cerver: The GameCerver.
		lobby: The Lobby.
	"""
)

game_request_send = lib_function (
	"game_request_send", [c_void_p, c_void_p, c_uint32, c_void_p, c_void_p], c_uint8,
	"""Sends a game request with its object to the game cerver of a connection.

	Args:
		client: The Client.
		connection: The Connection.
		request_type: A GAME_PACKET_TYPE_* value.
		schema: The address of the SerializerSchema of the object (serializer_schema ()).
		object: The address of the object, like byref () of a LobbyJoin.

	Returns:
		0 on success, 1 on error.
	"""
)
