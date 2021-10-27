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
	http_response_send_file (
		http_receive, HTTP_STATUS_OK,
		b"./examples/http/public/index.html"
	)

# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Test route works!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

# GET /text
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def text_handler (http_receive, request):
	text = b"<!DOCTYPE html><html><head><meta charset=\"utf-8\" /><title>Cerver</title></head><body><h2>text_handler () works!</h2></body></html>"
	text_len = len (text)

	http_response_render_text (
		http_receive, HTTP_STATUS_OK,
		text, text_len
	)

# GET /json
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_handler (http_receive, request):
	json =  b"{\"msg\": \"okay\"}"
	json_len = len (json)

	http_response_render_json (
		http_receive, HTTP_STATUS_OK,
		json, json_len
	)

# GET /hola
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def hola_handler (http_receive, request):
	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, b"Hola handler!"
	)

# GET /adios
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def adios_handler (http_receive, request):
	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, b"Adios handler!"
	)

def start ():
	global web_service
	web_service = cerver_create_web (
		b"web-service", 8080, 10
	)

	# main configuration
	cerver_set_alias (web_service, b"web")

	cerver_set_receive_buffer_size (web_service, 4096)
	cerver_set_thpool_n_threads (web_service, 4)
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (web_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	http_cerver_static_path_add (http_cerver, b"./examples/http/public")

	# GET /
	main_route = http_route_create (REQUEST_METHOD_GET, b"/", main_handler)
	http_cerver_route_register (http_cerver, main_route)

	# GET /test
	test_route = http_route_create (REQUEST_METHOD_GET, b"test", test_handler)
	http_cerver_route_register (http_cerver, test_route)

	# GET /text
	text_route = http_route_create (REQUEST_METHOD_GET, b"text", text_handler)
	http_cerver_route_register (http_cerver, text_route)

	# GET /json
	json_route = http_route_create (REQUEST_METHOD_GET, b"json", json_handler)
	http_cerver_route_register (http_cerver, json_route)

	# GET /hola
	hola_route = http_route_create (REQUEST_METHOD_GET, b"hola", hola_handler)
	http_cerver_route_register (http_cerver, hola_route)

	# GET /adios
	adios_route = http_route_create (REQUEST_METHOD_GET, b"adios", adios_handler)
	http_cerver_route_register (http_cerver, adios_route)

	# start
	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
