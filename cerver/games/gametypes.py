"""The game types of a game cerver: their lobby settings and the actions of their lobbies."""

from ctypes import CFUNCTYPE
from ctypes import c_bool, c_char_p, c_int, c_uint32, c_void_p
from typing import TypeAlias

from ..lib import lib_function

from ..core.cerver import Action

__all__ = [
	"GAME_TYPE_DEFAULT_PLAYER_TIMEOUT", "GAME_TYPE_DEFAULT_FPS",
	"GameTypeWork",
	"game_type_new", "game_type_create", "game_type_delete", "game_type_add_lobby_config",
	"game_type_set_on_lobby_join", "game_type_set_on_lobby_leave", "game_type_set_init",
	"game_type_set_player_timeout", "game_type_set_fps",
	"game_type_register", "game_type_unregister", "game_type_get_by_name"
]

GAME_TYPE_DEFAULT_PLAYER_TIMEOUT = 0
GAME_TYPE_DEFAULT_FPS = 20

# void *(*) (void *), the start and the end of a game
GameTypeWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

game_type_new = lib_function (
	"game_type_new", [], c_void_p,
	"""Allocates an empty game type.

	Returns:
		The GameType, released with game_type_delete ().
	"""
)

game_type_create = lib_function (
	"game_type_create", [c_char_p, c_void_p, Action, GameTypeWork, GameTypeWork], c_void_p,
	"""Creates a game type.

	Args:
		name: Its name, as bytes, required.
		data: Its data.
		delete_data: A kept Action that deletes the data, None uses free ().
		start: A kept GameTypeWork that starts a game, or None.
		end: A kept GameTypeWork that ends a game, or None.

	Returns:
		The GameType, None on error.
	"""
)

game_type_delete = lib_function (
	"game_type_delete", [c_void_p], None,
	"""Releases a game type.

	Args:
		ptr: The GameType.
	"""
)

game_type_add_lobby_config = lib_function (
	"game_type_add_lobby_config", [c_void_p, c_bool, Action, c_uint32], c_int,
	"""Adds the configuration that creates the lobbies of the game type.

	Args:
		game_type: The GameType.
		use_default_handler: True to handle the packets of the lobbies with the default handler.
		custom_handler: A kept Action used when use_default_handler is False, or None.
		max_players: The players of a lobby, 0 takes LOBBY_DEFAULT_MAX_PLAYERS.

	Returns:
		0 on success, 1 on error.
	"""
)

game_type_set_on_lobby_join = lib_function (
	"game_type_set_on_lobby_join", [c_void_p, Action], None,
	"""Sets the action that runs when a player joins a lobby, it gets a LobbyPlayer.

	Args:
		game_type: The GameType.
		on_lobby_join: A kept Action.
	"""
)

game_type_set_on_lobby_leave = lib_function (
	"game_type_set_on_lobby_leave", [c_void_p, Action], None,
	"""Sets the action that runs when a player leaves a lobby, it gets a LobbyPlayer.

	Args:
		game_type: The GameType.
		on_lobby_leave: A kept Action.
	"""
)

game_type_set_init = lib_function (
	"game_type_set_init", [c_void_p, Action], None,
	"""Sets the action that runs when the owner of a lobby requests GAME_INIT, it gets a LobbyPlayer.

	Args:
		game_type: The GameType.
		init: A kept Action.
	"""
)

game_type_set_player_timeout = lib_function (
	"game_type_set_player_timeout", [c_void_p, c_uint32], None,
	"""Sets the seconds without packets after which a player leaves its lobby, 0 never.

	Args:
		game_type: The GameType.
		player_timeout: The seconds, GAME_TYPE_DEFAULT_PLAYER_TIMEOUT by default.
	"""
)

game_type_set_fps = lib_function (
	"game_type_set_fps", [c_void_p, c_uint32], None,
	"""Sets the frames per second of the update of the lobbies of the game type, 0 is ignored.

	Args:
		game_type: The GameType.
		fps: The frames per second, GAME_TYPE_DEFAULT_FPS by default.
	"""
)

game_type_register = lib_function (
	"game_type_register", [c_void_p, c_void_p], c_int,
	"""Registers a game type.

	Args:
		game_types: The DoubleList of the game types of the GameCerver.
		game_type: The GameType.

	Returns:
		0 on success, 1 on error.
	"""
)

game_type_unregister = lib_function (
	"game_type_unregister", [c_void_p, c_char_p], c_int,
	"""Unregisters a game type by its name.

	Args:
		game_types: The DoubleList of the game types.
		name: The name, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

game_type_get_by_name = lib_function (
	"game_type_get_by_name", [c_void_p, c_char_p], c_void_p,
	"""Returns a registered game type by its name.

	Args:
		game_types: The DoubleList of the game types.
		name: The name, as bytes.

	Returns:
		The GameType, None if there is none with that name.
	"""
)
