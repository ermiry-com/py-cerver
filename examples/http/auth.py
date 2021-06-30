import signal, sys

import json
import random
import time

import ctypes

from cerver import *
from cerver.http import *

from users import *

auth_cerver = None

# end
def end (signum, frame):
	# cerver_stats_print (auth_cerver, False, False)
	http_cerver_all_stats_print (http_cerver_get (auth_cerver))
	cerver_teardown (auth_cerver)
	cerver_end ()
	sys.exit ("Done!")

# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Test route works!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

# GET /auth/token
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def auth_token_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Token auth route works!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

# POST /auth/custom
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def auth_custom_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Custom auth route works!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

@ctypes.CFUNCTYPE (ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p)
def custom_authentication_handler (http_receive, request):
	result = 1

	http_request_multi_parts_print (request)

	key = http_request_multi_parts_get_value (request, "key".encode ('utf-8'))
	if (key == "okay".encode ('utf-8')):
		cerver.utils.cerver_log_success (b"Success auth!")

		result = 0

	else:
		cerver.utils.cerver_log_error (b"Failed auth!")

	return result

def start ():
	global auth_cerver
	auth_cerver = cerver_create_web (
		"auth-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (auth_cerver, 4096)
	cerver_set_thpool_n_threads (auth_cerver, 4)
	cerver_set_handler_type (auth_cerver, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (auth_cerver, True)

	# HTTP configuration
	http_cerver = http_cerver_get (auth_cerver)

	http_cerver_auth_set_jwt_algorithm (http_cerver, JWT_ALG_RS256)
	http_cerver_auth_set_jwt_priv_key_filename (http_cerver, b"keys/key.key")
	http_cerver_auth_set_jwt_pub_key_filename (http_cerver, b"keys/key.pub")

	# GET /test
	test_route = http_route_create (REQUEST_METHOD_GET, b"test", test_handler)
	http_cerver_route_register (http_cerver, test_route)

	# GET /auth/token
	auth_token_route = http_route_create (REQUEST_METHOD_GET, b"auth/token", auth_token_handler)
	http_route_set_auth (auth_token_route, HTTP_ROUTE_AUTH_TYPE_BEARER)
	http_route_set_decode_data_into_json (auth_token_route)
	http_cerver_route_register (http_cerver, auth_token_route)

	# GET /auth/custom
	auth_custom_route = http_route_create (REQUEST_METHOD_POST, b"auth/custom", auth_custom_handler)
	http_route_set_auth (auth_custom_route, HTTP_ROUTE_AUTH_TYPE_CUSTOM)
	http_route_set_authentication_handler (auth_custom_route, custom_authentication_handler)
	http_cerver_route_register (http_cerver, auth_custom_route)

	# start
	cerver_start (auth_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
