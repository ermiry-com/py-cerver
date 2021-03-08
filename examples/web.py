import os, signal, sys
import ctypes

import cerver

web_cerver = None

# end
def end (signum, frame):
	print ("Hola!")
	# cerver.cerver_stats_print (web_cerver, False, False)
	cerver.http_cerver_all_stats_print (web_cerver)
	cerver.cerver_teardown (web_cerver)
	cerver.cerver_end ()
	sys.exit ("Done!")

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	cerver.http_response_render_file (
		http_receive,
		"./examples/public/index.html".encode ('utf-8')
	)

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def hola_handler (http_receive, request):
	print ("Hola handler!")
	cerver.http_response_json_msg_send (http_receive, 200, "Hola handler!".encode ('utf-8'))

def start ():
	global web_cerver
	web_cerver = cerver.cerver_create_web (
		"web-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver.cerver_set_receive_buffer_size (web_cerver, 4096);
	cerver.cerver_set_thpool_n_threads (web_cerver, 4);
	cerver.cerver_set_handler_type (web_cerver, cerver.CERVER_HANDLER_TYPE_THREADS);

	cerver.cerver_set_reusable_address_flags (web_cerver, True);

	# HTTP configuration
	http_cerver = cerver.http_cerver_get (web_cerver)

	cerver.http_cerver_static_path_add (http_cerver, "./examples/public".encode ('utf-8'))

	# GET /
	main_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "/".encode ('utf-8'), main_handler)
	cerver.http_cerver_route_register (http_cerver, main_route)

	# GET /hola
	hola_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "hola".encode ('utf-8'), hola_handler)
	cerver.http_cerver_route_register (http_cerver, hola_route)

	# start
	cerver.cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver.cerver_init ()

	print ("\n")
	cerver.cerver_version_print_full ()
	print ("\n")

	start ()
