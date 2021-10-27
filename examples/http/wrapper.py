import os, sys
import json

import ctypes

from cerver import *
from cerver.http import *

web_service = None

# end
def end (signum, frame):
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	http_send_response (
		http_receive, HTTP_STATUS_OK, { "oki": "doki!" }
	)

# GET /echo
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def echo_handler (http_receive, request):
	body_values = http_request_get_query_params (request)
	value = http_request_get_query_value (body_values, "value")
	http_send_response (
		http_receive, HTTP_STATUS_OK,
		{ "echo": f"Values received: {value}" }
	)

# POST /data
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def data_handler (http_receive, request):
	body = http_request_get_body_json (request)
	http_send_response (http_receive, HTTP_STATUS_OK, { "echo": body })

# POST /token
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def token_handler (http_receive, request):
	body = http_request_get_body_json (request)
	http_jwt_create_and_send (http_receive, HTTP_STATUS_OK, body)

# GET /auth
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def auth_handler (http_receive, request):
	token_values = http_jwt_token_decode (request)
	http_send_response (
		http_receive, HTTP_STATUS_OK, {
		"oki": "doki",
		"values": token_values
	})

# GET /parent
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def parent_handler (http_receive, request):
	pass

# GET /child
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def child_handler (http_receive, request):
	pass

def start ():
	global web_service

	web_service = http_cerver_configuration ("web")
	http_cerver = http_cerver_get (web_service)

	http_cerver_auth_configuration (
		http_cerver, JWT_ALG_RS256, "keys/key.key", "keys/key.pub"
	)

	# GET /
	main_route = http_create_route (
		http_cerver, REQUEST_METHOD_GET, "/", main_handler
	)

	# GET /echo
	echo_route = http_create_route (
		http_cerver, REQUEST_METHOD_GET, "echo", echo_handler
	)

	# POST /data
	data_route = http_create_route (
		http_cerver, REQUEST_METHOD_POST, "data", data_handler
	)

	# POST /token
	token_route = http_create_route (
		http_cerver, REQUEST_METHOD_POST, "token", token_handler
	)

	# GET /auth
	auth_route = http_create_route (
		http_cerver, REQUEST_METHOD_GET, "auth",
		auth_handler, HTTP_ROUTE_AUTH_TYPE_BEARER
	)

	# GET /parent
	parent_route = http_create_route (
		http_cerver, REQUEST_METHOD_GET, "parent",
		parent_handler, HTTP_ROUTE_AUTH_TYPE_BEARER
	)

	# GET /parent/child
	auth_route = http_create_child_route (
		parent_route, REQUEST_METHOD_GET, "child",
		child_handler, HTTP_ROUTE_AUTH_TYPE_BEARER
	)

	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
