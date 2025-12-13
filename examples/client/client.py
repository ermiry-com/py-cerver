"""A client of a cerver: it connects (resolving the host and trying each address), receives in
its own thread, sends app packets, gets the answers in its handler, and reconnects when the
cerver ends the connection.

	python3 examples/client/server.py tcp &
	python3 examples/client/client.py tcp localhost
"""

import os
import sys
import threading
from ctypes import POINTER, cast

from cerver import cerver_init, cerver_end
from cerver import handler_create, handler_set_direct_handle, HandlerMethod
from cerver import Packet, PACKET_TYPE_APP, packet_data, packet_send_data
from cerver import connection_set_attempt_reconnect, connection_set_connect_timeout
from cerver.callbacks import callback_wrap
from cerver.client import client_create, client_set_name, client_set_app_handlers
from cerver.client import client_connection_create, client_connect_and_start, client_connection_end
from cerver.client import client_teardown, client_event_on, CLIENT_EVENT_CONNECTED, CLIENT_EVENT_DISCONNECTED
from cerver.network import PROTOCOL_TCP, PROTOCOL_UDP, network_resolve
from cerver.utils import cerver_log_success, cerver_log_error

SERVER_PORT = int (os.environ.get ("PORT", 7000))

PROTOCOLS = {"tcp": PROTOCOL_TCP, "udp": PROTOCOL_UDP}

MESSAGES = ("first", "second", "third")

# the seconds between the attempts to reconnect
RECONNECT_SECONDS = 4

# the milliseconds that a connect to each address can take
CONNECT_TIMEOUT = 2048

ANSWERS_SECONDS = 8

answers = []
answered = threading.Condition ()

def receive (packet_ptr: int) -> None:
	"""The handler of the app packets of the client, it runs in the thread of the connection."""
	with answered:
		answers.append (packet_data (cast (packet_ptr, POINTER (Packet))).decode ("utf-8"))
		answered.notify_all ()

def main () -> int:
	protocol = sys.argv[1] if (len (sys.argv) > 1) else "tcp"
	host = sys.argv[2] if (len (sys.argv) > 2) else "localhost"

	cerver_init ()

	cerver_log_success (f"{host} resolves to {network_resolve (host, SERVER_PORT, protocol=PROTOCOLS[protocol])}")

	client = client_create ()
	client_set_name (client, b"echo-client")

	handler = handler_create (callback_wrap (receive, HandlerMethod))
	handler_set_direct_handle (handler, True)
	client_set_app_handlers (client, handler, None)

	client_event_on (client, CLIENT_EVENT_CONNECTED, lambda client, connection: cerver_log_success ("Connected!"))
	client_event_on (client, CLIENT_EVENT_DISCONNECTED, lambda client, connection: cerver_log_error ("Disconnected!"))

	connection = client_connection_create (client, host.encode ("utf-8"), SERVER_PORT, PROTOCOLS[protocol], False)
	connection_set_connect_timeout (connection, CONNECT_TIMEOUT)
	connection_set_attempt_reconnect (connection, RECONNECT_SECONDS)

	result = 1
	if (not client_connect_and_start (client, connection)):
		for message in MESSAGES:
			packet_send_data (PACKET_TYPE_APP, 0, message.encode ("utf-8"), None, client, connection)

		with answered:
			answered.wait_for (lambda: len (answers) == len (MESSAGES), ANSWERS_SECONDS)

		cerver_log_success (f"Answers: {answers}")
		result = 0 if (sorted (answers) == sorted (MESSAGES)) else 1

		client_connection_end (client, connection)

	client_teardown (client)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
