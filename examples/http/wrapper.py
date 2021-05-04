import os, sys
import json

import ctypes

from cerver import *
from cerver.http import *

api_cerver = None

# end
def end (signum, frame):
	http_cerver_all_stats_print (http_cerver_get (api_cerver))
	cerver_teardown (api_cerver)
	cerver_end ()
	sys.exit ("Done!")

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	http_send_response (http_receive, HTTP_STATUS_OK, { "msg": "Wrapper works!" })

# GET /echo
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def echo_handler (http_receive, request):
	body_values = http_request_get_query_params (request)
	value = http_request_get_query_value (body_values, "value")
	http_send_response (http_receive, HTTP_STATUS_OK, { "echo_says": f"Wrapper received: {value}" })

# POST /data
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def data_handler (http_receive, request):
	body = http_request_get_body_json (request)
	http_send_response (http_receive, HTTP_STATUS_OK, { "echo": body })

# POST /token
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def token_handler (http_receive, request):
	body = http_request_get_body_json (request)
	http_jwt_sign_and_send (http_receive, HTTP_STATUS_OK, body)

# GET /auth
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def auth_handler (http_receive, request):
	token_values = http_jwt_token_decode (request)
	http_send_response (
		http_receive, HTTP_STATUS_OK, {
		"msg": "is authenticated",
		"token_values": token_values
	})

def start ():
	global api_cerver

	api_cerver = cerver_main_http_configuration ()
	http_cerver = http_cerver_get (api_cerver)
	cerver_auth_http_configuration (http_cerver, JWT_ALG_RS256, "keys/key.key", "keys/key.pub")

	# GET /
	main_route = http_create_route (REQUEST_METHOD_GET, "/", main_handler, http_cerver = http_cerver)

	# GET /echo
	echo_route = http_create_route (REQUEST_METHOD_GET, "echo", echo_handler, main_route)

	# POST /data
	data_route = http_create_route (REQUEST_METHOD_POST, "data", data_handler, main_route)

	# POST /token
	token_route = http_create_route (REQUEST_METHOD_POST, "token", token_handler, main_route)

	# GET /auth
	auth_route = http_create_secure_route (REQUEST_METHOD_GET, "auth", auth_handler, main_route)

	cerver_start (api_cerver)

if __name__ == "__main__":
	cerver_initialize(end, True)

	start()