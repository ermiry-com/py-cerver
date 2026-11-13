"""The game bindings over the real libcerver: the scoreboards with the variadic constructor,
the objects of the lobbies encoded and decoded by their schemas, and the players.
"""

import cbor2
import pytest

from cerver.core import SERIALIZER_RESULT_NONE, SERIALIZER_RESULT_MISSING, SERIALIZER_VERSION_KEY
from cerver.core import serializer_schema, serializer_encode_bytes, serializer_decode_bytes
from cerver.games import LOBBY_JOIN_REQUEST_SCHEMA, LOBBY_OBJECTS_VERSION, LOBBY_SUMMARY_SCHEMA
from cerver.games import LobbyJoin, LobbySummary
from cerver.games import game_score_board, game_score_delete, game_score_add_player
from cerver.games import game_score_get, game_score_set, game_score_update, game_score_reset
from cerver.games import player_new, player_delete, player_set_id, player_comparator_by_id

pytestmark = [pytest.mark.unit]

SCORE_PLAYERS = 2
SCORE_TYPES = ["kills", "deaths"]
PLAYER = b"first"
MISSING = b"missing"
MISSING_SCORE = -1

KILLS = 5
DEATHS_DOWN = -9

LOBBY_ID = b"lobby-1"
GAME_TYPE = b"arcade"

# the keys of the fields of a LobbyJoin
JOIN_LOBBY_ID = 1
JOIN_GAME_TYPE = 2

class TestScores:

	def test_board_with_its_score_types (self):
		board = game_score_board (SCORE_PLAYERS, SCORE_TYPES)
		assert board

		try:
			assert game_score_add_player (board, PLAYER) == 0
			assert game_score_add_player (board, PLAYER) == 1

			game_score_set (board, PLAYER, b"kills", KILLS)
			assert game_score_get (board, PLAYER, b"kills") == KILLS

			# the scores are clamped to 0
			game_score_update (board, PLAYER, b"deaths", DEATHS_DOWN)
			assert game_score_get (board, PLAYER, b"deaths") == 0

			game_score_reset (board, PLAYER)
			assert game_score_get (board, PLAYER, b"kills") == 0

			assert game_score_get (board, MISSING, b"kills") == MISSING_SCORE

		finally:
			game_score_delete (board)

class TestLobbyObjects:

	def test_join_round_trip (self):
		schema = serializer_schema (LOBBY_JOIN_REQUEST_SCHEMA)

		data = serializer_encode_bytes (schema, LobbyJoin (lobby_id=LOBBY_ID, game_type=GAME_TYPE))
		assert data

		decoded = cbor2.loads (data)
		assert decoded[SERIALIZER_VERSION_KEY] == LOBBY_OBJECTS_VERSION
		assert (decoded[JOIN_LOBBY_ID], decoded[JOIN_GAME_TYPE]) == (LOBBY_ID.decode (), GAME_TYPE.decode ())

		join = LobbyJoin ()
		assert serializer_decode_bytes (schema, data, join) == SERIALIZER_RESULT_NONE
		assert (join.lobby_id, join.game_type) == (LOBBY_ID, GAME_TYPE)

	def test_join_without_its_game_type (self):
		schema = serializer_schema (LOBBY_JOIN_REQUEST_SCHEMA)

		data = cbor2.dumps ({SERIALIZER_VERSION_KEY: LOBBY_OBJECTS_VERSION, JOIN_LOBBY_ID: LOBBY_ID.decode ()})
		assert serializer_decode_bytes (schema, data, LobbyJoin ()) == SERIALIZER_RESULT_MISSING

	def test_summary_schema_exists (self):
		assert serializer_schema (LOBBY_SUMMARY_SCHEMA)

	def test_missing_schema (self):
		with pytest.raises (ValueError):
			serializer_schema ("missing_schema")

	def test_empty_summary_round_trip (self):
		schema = serializer_schema (LOBBY_SUMMARY_SCHEMA)

		summary = LobbySummary (id=LOBBY_ID)
		decoded = LobbySummary ()
		assert serializer_decode_bytes (schema, serializer_encode_bytes (schema, summary), decoded) == SERIALIZER_RESULT_NONE
		assert decoded.id == LOBBY_ID

class TestPlayers:

	def test_comparator_by_id (self):
		first, second = player_new (), player_new ()

		try:
			player_set_id (first, PLAYER)
			player_set_id (second, PLAYER)
			assert player_comparator_by_id (first, second) == 0

			player_set_id (second, MISSING)
			assert player_comparator_by_id (first, second) != 0

		finally:
			player_delete (first)
			player_delete (second)
