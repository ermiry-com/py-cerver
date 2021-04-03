import os, signal, sys
import ctypes

import cerver

web_cerver = None

# end
def end (signum, frame):
	# cerver.cerver_stats_print (web_cerver, False, False)
	cerver.http_cerver_all_stats_print (cerver.http_cerver_get (web_cerver))
	cerver.cerver_teardown (web_cerver)
	cerver.cerver_end ()
	sys.exit ("Done!")

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	cerver.http_response_render_file (
		http_receive,
		"./examples/public/index.html".encode ('utf-8')
	)

# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	response = cerver.http_response_json_msg (
		cerver.HTTP_STATUS_OK, "Test route works!".encode ('utf-8')
	)

	cerver.http_response_print (response)
	cerver.http_response_send (response, http_receive)
	cerver.http_response_delete (response)

# GET /text
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def text_handler (http_receive, request):
	text = "<!DOCTYPE html><html><head><meta charset=\"utf-8\" /><title>Cerver</title></head><body><h2>text_handler () works!</h2></body></html>".encode ('utf-8')
	text_len = len (text)

	cerver.http_response_render_text (http_receive, text, text_len)

# GET /json
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_handler (http_receive, request):
	json =  "{\"msg\": \"okay\"}".encode ('utf-8')
	json_len = len (json)

	cerver.http_response_render_json (http_receive, json, json_len)

# GET /hola
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def hola_handler (http_receive, request):
	cerver.http_response_json_msg_send (
		http_receive, 200, "Hola handler!".encode ('utf-8')
	)

# GET /adios
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def adios_handler (http_receive, request):
	cerver.http_response_json_msg_send (
		http_receive, 200, "Adios handler!".encode ('utf-8')
	)

# GET /key
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def key_handler (http_receive, request):
	cerver.http_response_json_key_value_send (
		http_receive, cerver.HTTP_STATUS_OK,
		"key".encode ('utf-8'), "value".encode ('utf-8')
	)

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

	# GET /test
	test_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "test".encode ('utf-8'), test_handler)
	cerver.http_cerver_route_register (http_cerver, test_route)

	# GET /text
	text_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "text".encode ('utf-8'), text_handler)
	cerver.http_cerver_route_register (http_cerver, text_route)

	# GET /json
	json_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "json".encode ('utf-8'), json_handler)
	cerver.http_cerver_route_register (http_cerver, json_route)

	# GET /hola
	hola_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "hola".encode ('utf-8'), hola_handler)
	cerver.http_cerver_route_register (http_cerver, hola_route)

	# GET /adios
	adios_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "adios".encode ('utf-8'), adios_handler)
	cerver.http_cerver_route_register (http_cerver, adios_route)

	# GET /key
	key_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "key".encode ('utf-8'), key_handler)
	cerver.http_cerver_route_register (http_cerver, key_route)

	# start
	cerver.cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver.cerver_init ()

	cerver.cerver_version_print_full ()

	cerver.pycerver_version_print_full ()

	start ()
