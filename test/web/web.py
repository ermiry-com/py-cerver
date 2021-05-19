import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *

web_cerver = None

# end
def end (signum, frame):
	# cerver_stats_print (web_cerver, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_cerver))
	cerver_teardown (web_cerver)
	cerver_end ()
	sys.exit ("Done!")

# GET /render
# test http_response_render_file ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_render_handler (http_receive, request):
	http_response_render_file (
		http_receive, HTTP_STATUS_OK,
		"./web/public/index.html".encode ('utf-8')
	)

# GET /render/text
# test http_response_render_text ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def text_render_handler (http_receive, request):
	text = "<!DOCTYPE html><html><head><meta charset=\"utf-8\" /><title>Cerver</title></head><body><h2>text_handler () works!</h2></body></html>".encode ('utf-8')
	text_len = len (text)

	http_response_render_text (
		http_receive, HTTP_STATUS_OK,
		text, text_len
	)

# GET /render/json
# test http_response_render_json ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_render_handler (http_receive, request):
	json =  "{\"msg\": \"okay\"}".encode ('utf-8')
	json_len = len (json)

	http_response_render_json (
		http_receive, HTTP_STATUS_OK,
		json, json_len
	)

# GET /json/create
# test http_response_create_json ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_create_handler (http_receive, request):
	json =  "{\"msg\": \"okay\"}".encode ('utf-8')
	json_len = len (json)

	res = http_response_create_json (
		HTTP_STATUS_OK, json, json_len
	)

	http_response_print (res)
	http_response_send (res, http_receive)
	http_response_delete (res)

# GET /json/create/key
# test http_response_create_json ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_create_key_value_handler (http_receive, request):
	res = http_response_create_json_key_value (
		HTTP_STATUS_OK, "msg".encode ('utf-8'), "okay".encode ('utf-8')
	)

	http_response_print (res)
	http_response_send (res, http_receive)
	http_response_delete (res)

# GET /json/create/message
# test http_response_json_msg ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_create_message_handler (http_receive, request):
	res = http_response_json_msg (
		HTTP_STATUS_OK, "okay".encode ('utf-8')
	)

	http_response_print (res)
	http_response_send (res, http_receive)
	http_response_delete (res)

# GET /json/send/message
# test http_response_json_msg_send ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_send_message_handler (http_receive, request):
	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, "okay".encode ('utf-8')
	)

# GET /json/create/error
# test http_response_json_error ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_create_error_handler (http_receive, request):
	res = http_response_json_error (
		HTTP_STATUS_BAD_REQUEST, "bad request".encode ('utf-8')
	)

	http_response_print (res)
	http_response_send (res, http_receive)
	http_response_delete (res)

# GET /json/send/error
# test http_response_json_msg_send ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_send_error_handler (http_receive, request):
	http_response_json_error_send (
		http_receive, HTTP_STATUS_BAD_REQUEST, "bad request".encode ('utf-8')
	)

def start ():
	global web_cerver
	web_cerver = cerver_create_web (
		"web-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (web_cerver, 4096);
	cerver_set_thpool_n_threads (web_cerver, 4);
	cerver_set_handler_type (web_cerver, CERVER_HANDLER_TYPE_THREADS);

	cerver_set_reusable_address_flags (web_cerver, True);

	# HTTP configuration
	http_cerver = http_cerver_get (web_cerver)

	http_cerver_static_path_add (http_cerver, "./web/public".encode ('utf-8'))

	# GET /render
	render_route = http_route_create (REQUEST_METHOD_GET, "render".encode ('utf-8'), main_render_handler);
	http_cerver_route_register (http_cerver, render_route);

	# GET /render/text
	render_text_route = http_route_create (REQUEST_METHOD_GET, "render/text".encode ('utf-8'), text_render_handler);
	http_cerver_route_register (http_cerver, render_text_route);

	# GET /render/json
	render_json_route = http_route_create (REQUEST_METHOD_GET, "render/json".encode ('utf-8'), json_render_handler);
	http_cerver_route_register (http_cerver, render_json_route);

	# GET /json/create
	json_create_route = http_route_create (REQUEST_METHOD_GET, "json/create".encode ('utf-8'), json_create_handler);
	http_cerver_route_register (http_cerver, json_create_route);

	# GET /json/create/key
	json_create_key_value_route = http_route_create (REQUEST_METHOD_GET, "json/create/key".encode ('utf-8'), json_create_key_value_handler);
	http_cerver_route_register (http_cerver, json_create_key_value_route);

	# GET /json/create/message
	json_create_message_route = http_route_create (REQUEST_METHOD_GET, "json/create/message".encode ('utf-8'), json_create_message_handler);
	http_cerver_route_register (http_cerver, json_create_message_route);

	# GET /json/send/message
	json_send_message_route = http_route_create (REQUEST_METHOD_GET, "json/send/message".encode ('utf-8'), json_send_message_handler);
	http_cerver_route_register (http_cerver, json_send_message_route);

	# GET /json/create/error
	json_create_error_route = http_route_create (REQUEST_METHOD_GET, "json/create/error".encode ('utf-8'), json_create_error_handler);
	http_cerver_route_register (http_cerver, json_create_error_route);

	# GET /json/send/error
	json_send_error_route = http_route_create (REQUEST_METHOD_GET, "json/send/error".encode ('utf-8'), json_send_error_handler);
	http_cerver_route_register (http_cerver, json_send_error_route);

	# start
	cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	start ()
