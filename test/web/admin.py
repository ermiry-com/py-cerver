import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *

web_service = None

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Admin HTTP cerver!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

def start ():
	global web_service
	web_service = cerver_create_web (
		b"web-service", 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (web_service, 4096);
	cerver_set_thpool_n_threads (web_service, 4);
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS);

	cerver_set_reusable_address_flags (web_service, True);

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	http_cerver_enable_admin_routes (http_cerver, True)

	# GET /
	main_route = http_route_create (REQUEST_METHOD_GET, b"/", main_handler)
	http_cerver_route_register (http_cerver, main_route)

	# start
	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	start ()
