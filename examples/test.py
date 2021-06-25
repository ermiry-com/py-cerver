import os, signal, sys
import ctypes

from cerver import *

APP_REQUEST_TEST_MSG = 0

my_cerver = None

# end
def end (signum, frame):
	cerver_stats_print (my_cerver, False, False)
	cerver_teardown (my_cerver)
	cerver_end ()
	sys.exit ("Done!")

@ctypes.CFUNCTYPE (None, ctypes.c_void_p)
def handler_method (packet_ptr):
	packet = ctypes.cast (packet_ptr, ctypes.POINTER (Packet))
	packet_send_request (
		PACKET_TYPE_APP, APP_REQUEST_TEST_MSG,
		packet.contents.cerver,
		packet.contents.client, packet.contents.connection,
		None
	)

def start ():
	global my_cerver
	my_cerver = cerver_create (
		CERVER_TYPE_CUSTOM,
		"my-cerver".encode ('utf-8'),
		7000,
		PROTOCOL_TCP,
		False,
		2
	)

	# main configuration
	cerver_set_receive_buffer_size (my_cerver, 4096);
	cerver_set_thpool_n_threads (my_cerver, 4);
	cerver_set_handler_type (my_cerver, CERVER_HANDLER_TYPE_THREADS);

	cerver_set_reusable_address_flags (my_cerver, True);

	app_handler = handler_create (handler_method)
	handler_set_direct_handle (app_handler, True)
	cerver_set_app_handlers (my_cerver, app_handler, None)

	# start
	cerver_start (my_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
