import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *

web_cerver = None

def end (signum, frame):
	http_cerver_all_stats_print (http_cerver_get (web_cerver))
	cerver_teardown (web_cerver)
	cerver_end ()
	sys.exit ("Done!")

# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, "Test route works!".encode ('utf-8')
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

def start ():
	global web_cerver
	web_cerver = cerver_create_web (
		"web-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver_set_thpool_n_threads (web_cerver, 4);
	cerver_set_handler_type (web_cerver, CERVER_HANDLER_TYPE_THREADS);

	# HTTP configuration
	http_cerver = http_cerver_get (web_cerver)

	# GET /test
	test_route = http_route_create (REQUEST_METHOD_GET, "test".encode ('utf-8'), test_handler)
	http_cerver_route_register (http_cerver, test_route)

	# start
	cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
