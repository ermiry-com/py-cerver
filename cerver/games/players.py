"""The players of the lobbies: a client in a lobby with its id and its data."""

from ctypes import c_char_p, c_int, c_int32, c_uint64, c_void_p

from ..lib import lib_function

from ..core.cerver import Action
from ..network.network import Protocol

__all__ = [
	"player_new", "player_delete", "player_set_id", "player_set_data",
	"player_comparator_by_id", "player_comparator_client_id",
	"player_activity_now", "player_activity_update",
	"player_get_from_lobby", "player_get_le_from_lobby", "player_get_by_sock_fd_list",
	"player_broadcast_to_all"
]

player_new = lib_function (
	"player_new", [], c_void_p,
	"""Allocates a player.

	Returns:
		The Player, released with player_delete ().
	"""
)

player_delete = lib_function (
	"player_delete", [c_void_p], None,
	"""Releases a player.

	Args:
		player_ptr: The Player.
	"""
)

player_set_id = lib_function (
	"player_set_id", [c_void_p, c_char_p], None,
	"""Sets the id of a player.

	Args:
		player: The Player.
		id: The id, as bytes.
	"""
)

player_set_data = lib_function (
	"player_set_data", [c_void_p, c_void_p, Action], None,
	"""Sets the data of a player and the action that deletes it.

	Args:
		player: The Player.
		data: The data.
		data_delete: A kept Action, or None.
	"""
)

player_comparator_by_id = lib_function (
	"player_comparator_by_id", [c_void_p, c_void_p], c_int,
	"""Compares two players by their ids.

	Args:
		a: The first Player.
		b: The second one.

	Returns:
		0 when their ids are equal.
	"""
)

player_comparator_client_id = lib_function (
	"player_comparator_client_id", [c_void_p, c_void_p], c_int,
	"""Compares two players by the ids of their clients.

	Args:
		a: The first Player.
		b: The second one.

	Returns:
		0 when the ids are equal.
	"""
)

player_activity_now = lib_function (
	"player_activity_now", [], c_uint64,
	"""Returns the milliseconds of the monotonic clock that the activity of the players uses."""
)

player_activity_update = lib_function (
	"player_activity_update", [c_void_p], None,
	"""Sets the last activity of a player to now.

	Args:
		player: The Player.
	"""
)

player_get_from_lobby = lib_function (
	"player_get_from_lobby", [c_void_p, c_void_p], c_void_p,
	"""Searches a player in a lobby with the comparator of the game cerver.

	Args:
		lobby: The Lobby.
		query: A Player with the values to search.

	Returns:
		The Player, None if there is none.
	"""
)

player_get_le_from_lobby = lib_function (
	"player_get_le_from_lobby", [c_void_p, c_void_p], c_void_p,
	"""Returns the element of the list of the players of a lobby that has a player.

	Args:
		lobby: The Lobby.
		player: The Player.

	Returns:
		The ListElement, None if the player is not in the lobby.
	"""
)

player_get_by_sock_fd_list = lib_function (
	"player_get_by_sock_fd_list", [c_void_p, c_int32], c_void_p,
	"""Returns the player of a lobby whose client has a socket.

	Args:
		lobby: The Lobby.
		sock_fd: The socket.

	Returns:
		The Player, None if there is none.
	"""
)

player_broadcast_to_all = lib_function (
	"player_broadcast_to_all", [c_void_p, c_void_p, c_void_p, Protocol, c_int], None,
	"""Sends a packet to every player of a lobby.

	Args:
		cerver: The Cerver.
		lobby: The Lobby.
		packet: The Packet.
		protocol: A PROTOCOL_* value.
		flags: The flags of the send.
	"""
)
