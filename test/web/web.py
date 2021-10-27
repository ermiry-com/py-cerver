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

# GET /render
# test http_response_send_file ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_render_handler (http_receive, request):
	http_response_send_file (
		http_receive, HTTP_STATUS_OK,
		b"./web/public/index.html"
	)

# GET /render/text
# test http_response_render_text ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def text_render_handler (http_receive, request):
	text = b"<!DOCTYPE html><html><head><meta charset=\"utf-8\" /><title>Cerver</title></head><body><h2>text_handler () works!</h2></body></html>"
	text_len = len (text)

	http_response_render_text (
		http_receive, HTTP_STATUS_OK,
		text, text_len
	)

# GET /render/json
# test http_response_render_json ()
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_render_handler (http_receive, request):
	json = b"{\"msg\": \"okay\"}"
	json_len = len (json)

	http_response_render_json (
		http_receive, HTTP_STATUS_OK,
		json, json_len
	)

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

	http_cerver_static_path_add (http_cerver, b"./web/public")

	# GET /render
	render_route = http_route_create (REQUEST_METHOD_GET, b"render", main_render_handler);
	http_cerver_route_register (http_cerver, render_route);

	# GET /render/text
	render_text_route = http_route_create (REQUEST_METHOD_GET, b"render/text", text_render_handler);
	http_cerver_route_register (http_cerver, render_text_route);

	# GET /render/json
	render_json_route = http_route_create (REQUEST_METHOD_GET, b"render/json", json_render_handler);
	http_cerver_route_register (http_cerver, render_json_route);

	# start
	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	start ()
