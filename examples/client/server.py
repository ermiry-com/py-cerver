"""An echo cerver of app packets, over TCP or UDP, for examples/client/client.py.

	python3 examples/client/server.py tcp
	python3 examples/client/server.py udp
"""

import os
import sys
from ctypes import POINTER, cast

from cerver import CERVER_TYPE_CUSTOM, CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_init, cerver_end, cerver_run, cerver_create
from cerver import cerver_set_app_handlers, cerver_set_handler_type, cerver_set_thpool_n_threads
from cerver import cerver_set_reusable_address_flags
from cerver import cerver_event_on, CERVER_EVENT_CLIENT_CONNECTED, CERVER_EVENT_CLIENT_DISCONNECTED
from cerver import handler_create, handler_set_direct_handle, HandlerMethod
from cerver import Packet, PACKET_TYPE_APP, packet_data, packet_send_data
from cerver.callbacks import callback_wrap
from cerver.network import PROTOCOL_TCP, PROTOCOL_UDP
from cerver.utils import cerver_log_success

SERVER_NAME = b"echo-server"
SERVER_PORT = int (os.environ.get ("PORT", 7000))
SERVER_THREADS = 2
SERVER_CONNECTION_QUEUE = 16

PROTOCOLS = {"tcp": PROTOCOL_TCP, "udp": PROTOCOL_UDP}

# the request type of the answers
ECHO_REQUEST = 1

def echo (packet_ptr: int) -> None:
	"""Answers an app packet with its data, its connection is in the packet."""
	packet = cast (packet_ptr, POINTER (Packet))
	values = packet.contents

	packet_send_data (
		PACKET_TYPE_APP, ECHO_REQUEST, packet_data (packet),
		values.cerver, values.client, values.connection
	)

def main () -> int:
	protocol = sys.argv[1] if (len (sys.argv) > 1) else "tcp"

	cerver_init ()

	server = cerver_create (
		CERVER_TYPE_CUSTOM, SERVER_NAME, SERVER_PORT, PROTOCOLS[protocol], False, SERVER_CONNECTION_QUEUE
	)

	cerver_set_handler_type (server, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_thpool_n_threads (server, SERVER_THREADS)
	cerver_set_reusable_address_flags (server, True)

	handler = handler_create (callback_wrap (echo, HandlerMethod))
	handler_set_direct_handle (handler, True)
	cerver_set_app_handlers (server, handler, None)

	cerver_event_on (server, CERVER_EVENT_CLIENT_CONNECTED, lambda cerver, client, connection: cerver_log_success ("A client connected"))
	cerver_event_on (server, CERVER_EVENT_CLIENT_DISCONNECTED, lambda cerver, client, connection: cerver_log_success ("A client disconnected"))

	result = cerver_run (server)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
