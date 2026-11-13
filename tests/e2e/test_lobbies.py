"""Clients of pycerver against the game cerver of clients/game.c: one creates a lobby of its game type
and another one joins it by its id, both get the LobbySummary of their lobby event.
"""

import pytest
import threading
from pathlib import Path

from cerver.client import client_create, client_connection_create, client_connect_and_start
from cerver.client import client_connection_end, client_set_name, client_teardown
from cerver.client import CLIENT_EVENT_LOBBY_CREATE, CLIENT_EVENT_LOBBY_JOIN
from cerver.core import GAME_PACKET_TYPE_LOBBY_CREATE, GAME_PACKET_TYPE_LOBBY_JOIN
from cerver.games import LobbyCreate, LobbyJoin, LobbySummary
from cerver.games import lobby_event_on, lobby_request_send
from cerver.network import PROTOCOL_TCP

from e2e.conftest import output, start, stop, wait_listening

pytestmark = [pytest.mark.e2e]

GAME_SERVER = Path ("/opt/pycerver/clients/server/game")

GAME_ADDRESS = "127.0.0.1"
GAME_PORT = 8098

# the game type and the players of the lobbies of clients/game.c
GAME_TYPE = b"pycerver"
GAME_MAX_PLAYERS = 2

EVENT_SECONDS = 8

class GameClient:
	"""A client of pycerver that keeps the summaries of its lobby events."""

	def __init__ (self, name: bytes):
		self.summaries = {}
		self.received = threading.Condition ()

		self.client = client_create ()
		client_set_name (self.client, name)

		for event in (CLIENT_EVENT_LOBBY_CREATE, CLIENT_EVENT_LOBBY_JOIN):
			assert lobby_event_on (self.client, event, self.event (event)) == 0

		self.connection = client_connection_create (self.client, GAME_ADDRESS.encode ("utf-8"), GAME_PORT, PROTOCOL_TCP, False)

	def event (self, event_type: int):
		def receive (client: int, connection: int | None, summary: LobbySummary) -> None:
			with self.received:
				self.summaries[event_type] = summary
				self.received.notify_all ()

		return receive

	def connect (self) -> int:
		return client_connect_and_start (self.client, self.connection)

	def wait (self, event_type: int) -> LobbySummary | None:
		with self.received:
			self.received.wait_for (lambda: event_type in self.summaries, EVENT_SECONDS)
			return self.summaries.get (event_type)

	def end (self) -> None:
		client_connection_end (self.client, self.connection)
		client_teardown (self.client)

@pytest.fixture
def game ():
	server = start ([str (GAME_SERVER), str (GAME_PORT)])
	assert wait_listening (server, GAME_PORT), output (server)

	yield server

	assert stop (server) == 0, output (server)

def test_create_and_join_a_lobby (game):
	owner, guest = GameClient (b"pycerver-owner"), GameClient (b"pycerver-guest")

	try:
		assert owner.connect () == 0, output (game)
		assert guest.connect () == 0, output (game)

		create = LobbyCreate (game_type=GAME_TYPE)
		assert lobby_request_send (owner.client, owner.connection, GAME_PACKET_TYPE_LOBBY_CREATE, create) == 0

		created = owner.wait (CLIENT_EVENT_LOBBY_CREATE)
		assert created is not None, output (game)
		assert created.id
		assert created.created
		assert created.game_type == GAME_TYPE
		assert (created.n_players, created.max_players) == (1, GAME_MAX_PLAYERS)
		assert created.players_count == 1
		assert created.players[0].owner
		assert created.settings.max_players == GAME_MAX_PLAYERS

		join = LobbyJoin (lobby_id=created.id, game_type=GAME_TYPE)
		assert lobby_request_send (guest.client, guest.connection, GAME_PACKET_TYPE_LOBBY_JOIN, join) == 0

		joined = guest.wait (CLIENT_EVENT_LOBBY_JOIN)
		assert joined is not None, output (game)
		assert joined.id == created.id
		assert not joined.created
		assert joined.n_players == GAME_MAX_PLAYERS
		assert joined.owner_client_id == created.owner_client_id

	finally:
		guest.end ()
		owner.end ()

def test_request_that_is_not_a_lobby_object ():
	with pytest.raises (TypeError):
		lobby_request_send (None, None, GAME_PACKET_TYPE_LOBBY_CREATE, LobbySummary ())
