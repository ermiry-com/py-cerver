"""The WebSocket server of the e2e tier, every method in Python, started by the tests as a subprocess.

/ws/echo		every message comes back, with permessage-deflate
/ws/chat		"join:room" joins a room, "say:room:text" sends the text to the others of the room
/ws/upgrade		on_upgrade () rejects the requests with X-Reject (409), gives its data to the others,
				adds headers to their 101 and takes the protocol of X-Protocol; "query" answers its query
/ws/broken		a method that raises: the connection is closed with 1011, an upgrade with X-Raise is a 500
/ws/stats		"cerver" answers the stats of the cerver and "connection" the ones of the connection
/ws/stream		every message is answered in two pieces of one message
/ws/later		every message is answered from another thread, after its method returned
/ws/types		a binary message comes back as a bytearray and as a memoryview
/ws/deleted		answers how many connections of the endpoint had their data deleted
"""

import json
import sys
import threading
from ctypes import cast, c_char_p, c_void_p

from cerver import CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_create_web
from cerver import cerver_run
from cerver import cerver_set_handler_type
from cerver import cerver_set_reusable_address_flags
from cerver import cerver_set_thpool_n_threads
from cerver.http import HTTP_STATUS_CONFLICT
from cerver.http import http_cerver_get
from cerver.http import http_cerver_group_create
from cerver.http import http_request_get_custom_header
from cerver.http import websockets as ws

SERVER_NAME = b"pycerver-websockets"
SERVER_THREADS = 4
SERVER_CONNECTION_QUEUE = 16

REJECT_HEADER = b"X-Reject"
PROTOCOL_HEADER = b"X-Protocol"
RAISE_HEADER = b"X-Raise"

UPGRADE_DATA = b"python-data"

PROTOCOLS = ["chat", "chat.v2"]

# seconds before the answer of /ws/later, its method already returned
LATER_SECONDS = 0.05

def _echo (web_socket, opcode, data):
	ws.http_web_socket_send (web_socket, opcode, data, len (data))

def _chat (web_socket, opcode, data):
	text = data.decode ()
	if (text.startswith ("join:")):
		ws.http_web_socket_join (web_socket, text[len ("join:"):].encode ())
		ws.web_socket_send (web_socket, "joined")

	elif (text.startswith ("say:")):
		_, room, message = text.split (":", 2)
		encoded = message.encode ()
		ws.http_cerver_web_socket_broadcast (
			ws.http_web_socket_get_http_cerver (web_socket), room.encode (), web_socket,
			ws.HTTP_WEB_SOCKET_OPCODE_TEXT, encoded, len (encoded)
		)

# the data of the connections, kept by Python while they live
upgrade_data = c_char_p (UPGRADE_DATA)

def _on_upgrade (http_receive, request, upgrade):
	accepted = http_request_get_custom_header (request, REJECT_HEADER) is None
	if (accepted):
		upgrade.contents.data = cast (upgrade_data, c_void_p)

		ws.web_socket_upgrade_add_header (upgrade, "X-Python", "yes")
		ws.web_socket_upgrade_add_header (upgrade, "Set-Cookie", "first=1")
		ws.web_socket_upgrade_add_header (upgrade, "Set-Cookie", "second=2")

		# a protocol that is built in the method: its bytes are collected when it returns
		protocol = http_request_get_custom_header (request, PROTOCOL_HEADER)
		if (protocol is not None):
			ws.web_socket_upgrade_set_protocol (upgrade, (protocol.decode () + "").encode ())

	else:
		upgrade.contents.status = HTTP_STATUS_CONFLICT

	return accepted

def _upgrade_open (web_socket):
	data = cast (ws.http_web_socket_get_data (web_socket), c_char_p).value
	ws.web_socket_send (web_socket, data)

def _upgrade_message (web_socket, opcode, data):
	if (data == b"query"):
		ws.web_socket_send (web_socket, ws.web_socket_query (web_socket) or "none")

	else:
		_echo (web_socket, opcode, data)

def _broken_upgrade (http_receive, request, upgrade):
	if (http_request_get_custom_header (request, RAISE_HEADER) is not None):
		raise RuntimeError ("on_upgrade () failed")

	return True

def _broken_message (web_socket, opcode, data):
	raise RuntimeError ("on_message () failed")

def _stats (web_socket, opcode, data):
	stats = ws.web_socket_stats (web_socket=web_socket) if (data == b"connection") \
		else ws.web_socket_stats (http_cerver=ws.http_web_socket_get_http_cerver (web_socket))

	ws.web_socket_send (web_socket, json.dumps ({
		"connections": stats.n_connections,
		"opened": stats.n_opened,
		"messages_received": stats.n_messages_received,
		"bytes_received": stats.n_bytes_received,
		"rejected": list (stats.n_rejected)
	}))

def _stream (web_socket, opcode, data):
	with ws.web_socket_stream (web_socket) as write:
		write ("one ")
		write (b"two")

def _later_send (reference):
	with reference:
		reference.send ("later")

def _later (web_socket, opcode, data):
	threading.Timer (LATER_SECONDS, _later_send, [ws.web_socket_keep (web_socket)]).start ()

def _types (web_socket, opcode, data):
	ws.web_socket_send (web_socket, bytearray (data))
	ws.web_socket_send (web_socket, memoryview (data))

# the connections of /ws/deleted whose data was deleted by cerver
deleted = []

def _deleted_data (data):
	deleted.append (data)

delete_data = ws.web_socket_delete_data (_deleted_data)

def _deleted_upgrade (http_receive, request, upgrade):
	upgrade.contents.data = cast (upgrade_data, c_void_p)
	upgrade.contents.delete_data = delete_data

	return True

def _deleted_message (web_socket, opcode, data):
	ws.web_socket_send (web_socket, str (len (deleted)))

def _routes (http_cerver):
	group = http_cerver_group_create (http_cerver, b"ws")

	echo = ws.http_group_web_socket_add (group, b"echo", ws.web_socket_handlers (on_message=_echo))
	ws.http_endpoint_set_web_socket_compression (echo, True)

	ws.http_group_web_socket_add (group, b"chat", ws.web_socket_handlers (on_message=_chat))

	upgrade = ws.http_group_web_socket_add (
		group, b"upgrade",
		ws.web_socket_handlers (on_upgrade=_on_upgrade, on_open=_upgrade_open, on_message=_upgrade_message)
	)

	ws.http_endpoint_set_web_socket_protocols (upgrade, *ws.web_socket_protocols (PROTOCOLS))

	ws.http_group_web_socket_add (
		group, b"broken", ws.web_socket_handlers (on_upgrade=_broken_upgrade, on_message=_broken_message)
	)

	ws.http_group_web_socket_add (group, b"stats", ws.web_socket_handlers (on_message=_stats))
	ws.http_group_web_socket_add (group, b"stream", ws.web_socket_handlers (on_message=_stream))
	ws.http_group_web_socket_add (group, b"later", ws.web_socket_handlers (on_message=_later))
	ws.http_group_web_socket_add (group, b"types", ws.web_socket_handlers (on_message=_types))

	ws.http_group_web_socket_add (
		group, b"deleted", ws.web_socket_handlers (on_upgrade=_deleted_upgrade, on_message=_deleted_message)
	)

def main (port: int) -> int:
	cerver = cerver_create_web (SERVER_NAME, port, SERVER_CONNECTION_QUEUE)
	cerver_set_handler_type (cerver, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_thpool_n_threads (cerver, SERVER_THREADS)
	cerver_set_reusable_address_flags (cerver, True)

	_routes (http_cerver_get (cerver))

	return cerver_run (cerver)

if __name__ == "__main__":
	sys.exit (main (int (sys.argv[1])))
