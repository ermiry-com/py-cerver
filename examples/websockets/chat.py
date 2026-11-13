"""A chat with rooms: on_upgrade () takes the name of the query (400 without one) and gives it to the
connection, every connection starts in the lobby, "/join <room>" moves it to another room and each
text goes to everyone in its room with a broadcast.

	python3 examples/websockets/chat.py
	python3 -m websockets "ws://localhost:8080/ws/chat?name=ana"
	python3 -m websockets "ws://localhost:8080/ws/chat?name=luis"
	curl http://localhost:8080/api/rooms/lobby
"""

import os
import sys
import threading
from ctypes import cast, c_char_p, c_void_p

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_BAD_REQUEST
from cerver.http import http_cerver_configuration, http_cerver_get, http_group, http_cerver_group_create
from cerver.http import http_receive_get_cerver, http_response_json_send
from cerver.http import http_request_get_query_params, http_request_get_query_value
from cerver.http import http_request_get_named_param_string
from cerver.http import HTTP_WEB_SOCKET_OPCODE_TEXT, HTTP_WEB_SOCKET_ROOM_NAME_SIZE
from cerver.http import http_group_web_socket_add, http_cerver_web_socket_broadcast, http_cerver_web_socket_count
from cerver.http import http_web_socket_join, http_web_socket_leave, http_web_socket_get_id
from cerver.http import http_web_socket_get_data, http_web_socket_get_http_cerver
from cerver.http import web_socket_handlers, web_socket_send

SERVICE_NAME = "chat"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

LOBBY = "lobby"
JOIN = "/join "

NAME_MAXIMUM = 32

# the names of the connections, kept by Python while their connections live (their data points to them)
names_lock = threading.Lock ()
names = {}

# the room of each connection, by its id
rooms = {}

def name_of (web_socket) -> str:
	return cast (http_web_socket_get_data (web_socket), c_char_p).value.decode ()

def broadcast (web_socket, room: str, text: str) -> None:
	"""Sends the text to everyone in the room, the sender included."""
	encoded = text.encode ()
	http_cerver_web_socket_broadcast (
		http_web_socket_get_http_cerver (web_socket), room.encode (), None,
		HTTP_WEB_SOCKET_OPCODE_TEXT, encoded, len (encoded)
	)

def on_upgrade (http_receive, request, upgrade):
	"""Runs in the thread of the request, before the 101: a connection without a valid name is rejected."""
	name = http_request_get_query_value (http_request_get_query_params (request), "name")
	accepted = bool (name) and (len (name) <= NAME_MAXIMUM)
	if (accepted):
		data = c_char_p (name.encode ())
		with names_lock:
			names[cast (data, c_void_p).value] = data

		upgrade.contents.data = cast (data, c_void_p)

	else:
		upgrade.contents.status = HTTP_STATUS_BAD_REQUEST

	return accepted

def on_open (web_socket):
	rooms[http_web_socket_get_id (web_socket)] = LOBBY
	http_web_socket_join (web_socket, LOBBY.encode ())
	broadcast (web_socket, LOBBY, f"{name_of (web_socket)} joined {LOBBY}")

def join (web_socket, room: str) -> None:
	"""Moves the connection from its room to another one."""
	if (room and (len (room) < HTTP_WEB_SOCKET_ROOM_NAME_SIZE)):
		identifier = http_web_socket_get_id (web_socket)
		http_web_socket_leave (web_socket, rooms[identifier].encode ())
		broadcast (web_socket, rooms[identifier], f"{name_of (web_socket)} left to {room}")

		rooms[identifier] = room
		http_web_socket_join (web_socket, room.encode ())
		broadcast (web_socket, room, f"{name_of (web_socket)} joined {room}")

	else:
		web_socket_send (web_socket, "Invalid room!")

def on_message (web_socket, opcode, data):
	text = data.decode ()
	if (text.startswith (JOIN)):
		join (web_socket, text[len (JOIN):].strip ())

	else:
		broadcast (web_socket, rooms[http_web_socket_get_id (web_socket)], f"{name_of (web_socket)}: {text}")

def on_close (web_socket, code, reason):
	"""The connection already left its rooms, the others are told that it is gone."""
	room = rooms.pop (http_web_socket_get_id (web_socket), LOBBY)
	broadcast (web_socket, room, f"{name_of (web_socket)} left")

	with names_lock:
		names.pop (http_web_socket_get_data (web_socket), None)

HANDLERS = web_socket_handlers (on_upgrade=on_upgrade, on_open=on_open, on_message=on_message, on_close=on_close)

def register (http_cerver: int) -> None:
	http_group_web_socket_add (http_cerver_group_create (http_cerver, b"ws"), b"chat", HANDLERS)

	api = http_group (http_cerver, "api/rooms")

	@api.get ("/:room")
	def room_get (http_receive, request):
		room = http_request_get_named_param_string (request, "room")
		http_response_json_send (http_receive, HTTP_STATUS_OK, {
			"room": room, "connections": http_cerver_web_socket_count (http_receive_get_cerver (http_receive), room.encode ())
		})

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	register (http_cerver_get (service))

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
