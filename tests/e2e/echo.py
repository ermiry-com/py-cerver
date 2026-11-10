"""An echo cerver of the e2e tier: it answers every app packet with the same data.

Usage: echo.py <tcp|udp> <address> <port>
"""

import sys
from ctypes import POINTER, cast

from cerver import CERVER_TYPE_CUSTOM, CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_create, cerver_run, cerver_set_bind_address, cerver_set_app_handlers
from cerver import cerver_set_handler_type, cerver_set_reusable_address_flags, cerver_set_thpool_n_threads
from cerver import cerver_init, cerver_end
from cerver import handler_create, handler_set_direct_handle, HandlerMethod
from cerver.callbacks import callback_wrap
from cerver.core import Packet, PACKET_TYPE_APP, packet_send_data, packet_data
from cerver.network import PROTOCOL_TCP, PROTOCOL_UDP

ECHO_NAME = b"pycerver-echo"
ECHO_THREADS = 2
ECHO_CONNECTION_QUEUE = 16

PROTOCOLS = {"tcp": PROTOCOL_TCP, "udp": PROTOCOL_UDP}

# the request type of the answers
ECHO_REQUEST = 7

def echo (packet_ptr: int) -> None:
	"""Sends the data of an app packet back to its connection."""
	packet = cast (packet_ptr, POINTER (Packet))
	values = packet.contents

	packet_send_data (
		PACKET_TYPE_APP, ECHO_REQUEST, packet_data (packet),
		values.cerver, values.client, values.connection
	)

def main () -> int:
	protocol, address, port = sys.argv[1], sys.argv[2], int (sys.argv[3])

	cerver_init ()

	cerver = cerver_create (
		CERVER_TYPE_CUSTOM, ECHO_NAME, port, PROTOCOLS[protocol], ":" in address, ECHO_CONNECTION_QUEUE
	)

	cerver_set_bind_address (cerver, address.encode ("utf-8"))
	cerver_set_thpool_n_threads (cerver, ECHO_THREADS)
	cerver_set_handler_type (cerver, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_reusable_address_flags (cerver, True)

	handler = handler_create (callback_wrap (echo, HandlerMethod))
	handler_set_direct_handle (handler, True)
	cerver_set_app_handlers (cerver, handler, None)

	result = cerver_run (cerver)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
