"""The scoreboards of the games: the scores of each player by score type, clamped to 0."""

from ctypes import c_char_p, c_int32, c_uint, c_uint8, c_void_p

from ..lib import lib_function, lib_c_string

__all__ = [
	"SCORE_DEFAULT_SIZE",
	"game_score_new", "game_score_create", "game_score_delete",
	"game_score_add_scoreType", "game_score_add_lobby_players", "game_score_remove_scoreType",
	"game_score_add_player", "game_score_remove_player",
	"game_score_set", "game_score_get", "game_score_update", "game_score_reset",
	"game_score_board"
]

# the players that a scoreboard has room for when it is created
SCORE_DEFAULT_SIZE = 5

game_score_new = lib_function (
	"game_score_new", [], c_void_p,
	"""Allocates an empty scoreboard.

	Returns:
		The ScoreBoard, released with game_score_delete ().
	"""
)

game_score_create = lib_function (
	"game_score_create", None, c_void_p,
	"""Creates a scoreboard with its score types as the variable arguments.

	It is variadic, so its arguments must be ctypes values: c_uint (players), c_uint (scores)
	and a c_char_p for each score type; game_score_board () converts them.

	Returns:
		The ScoreBoard, released with game_score_delete ().
	"""
)

game_score_delete = lib_function (
	"game_score_delete", [c_void_p], None,
	"""Releases a scoreboard.

	Args:
		sb: The ScoreBoard.
	"""
)

game_score_add_scoreType = lib_function (
	"game_score_add_scoreType", [c_void_p, c_char_p], None,
	"""Adds a score type with 0 to every player, an existing one is ignored.

	Args:
		sb: The ScoreBoard.
		newScore: The score type, as bytes.
	"""
)

game_score_add_lobby_players = lib_function (
	"game_score_add_lobby_players", [c_void_p, c_void_p], None,
	"""Adds the players of a lobby by their ids, the players without an id are skipped.

	Args:
		sb: The ScoreBoard.
		lobby: The Lobby.
	"""
)

game_score_remove_scoreType = lib_function (
	"game_score_remove_scoreType", [c_void_p, c_char_p], c_uint8,
	"""Removes a score type from every player.

	Args:
		sb: The ScoreBoard.
		oldScore: The score type, as bytes.

	Returns:
		0 on success, 1 if the score type does not exist.
	"""
)

game_score_add_player = lib_function (
	"game_score_add_player", [c_void_p, c_char_p], c_uint8,
	"""Adds a player with every score type in 0.

	Args:
		sb: The ScoreBoard.
		playerName: The name of the player, as bytes.

	Returns:
		0 on success, 1 if the player already exists.
	"""
)

game_score_remove_player = lib_function (
	"game_score_remove_player", [c_void_p, c_char_p], c_uint8,
	"""Removes a player.

	Args:
		sb: The ScoreBoard.
		playerName: The name of the player, as bytes.

	Returns:
		0 on success, 1 if the player does not exist.
	"""
)

game_score_set = lib_function (
	"game_score_set", [c_void_p, c_char_p, c_char_p, c_int32], None,
	"""Sets the value of a score, a negative one is set as 0.

	Args:
		sb: The ScoreBoard.
		playerName: The name of the player, as bytes.
		scoreType: The score type, as bytes.
		value: The value.
	"""
)

game_score_get = lib_function (
	"game_score_get", [c_void_p, c_char_p, c_char_p], c_int32,
	"""Returns the value of a score of a player.

	Args:
		sb: The ScoreBoard.
		playerName: The name of the player, as bytes.
		scoreType: The score type, as bytes.

	Returns:
		The value, -1 if the player or the score type does not exist.
	"""
)

game_score_update = lib_function (
	"game_score_update", [c_void_p, c_char_p, c_char_p, c_int32], None,
	"""Adds a value, that can be negative, to a score, the result is clamped to 0.

	Args:
		sb: The ScoreBoard.
		playerName: The name of the player, as bytes.
		scoreType: The score type, as bytes.
		value: The value to add.
	"""
)

game_score_reset = lib_function (
	"game_score_reset", [c_void_p, c_char_p], None,
	"""Sets every score of a player to 0.

	Args:
		sb: The ScoreBoard.
		playerName: The name of the player, as bytes.
	"""
)

def game_score_board (players: int, score_types: list) -> int | None:
	"""Creates a scoreboard with its score types.

	Args:
		players: The players that it has room for.
		score_types: The names of the score types, as str or bytes.

	Returns:
		The ScoreBoard, released with game_score_delete (), None on error.
	"""
	types = [c_char_p (lib_c_string (score_type)) for score_type in score_types]

	return game_score_create (c_uint (players), c_uint (len (types)), *types)
