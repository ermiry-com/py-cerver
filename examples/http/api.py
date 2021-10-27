import os, signal, sys
import time
import random
import json

import ctypes

from cerver import *
from cerver.http import *

from users import *

web_service = None

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

# GET /api/users
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_users_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Users route works!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

# POST /api/users/register
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def users_register_handler (http_receive, request):
	body_values = http_request_get_body_values (request)
	name = http_query_pairs_get_value (body_values, b"name")
	username = http_query_pairs_get_value (body_values, b"username")
	password = http_query_pairs_get_value (body_values, b"password")

	if name is not None and username is not None and password is not None:
		user = User (
			str (random.randint (1, 1001)),
			int (time.time ()),
			name.contents.str,
			"common",
			username.contents.str
		)

		user.password = password.contents.str

		user_add (user)

		response = http_response_json_msg (
			HTTP_STATUS_OK, b"Created a new user!"
		)

		http_response_print (response)
		http_response_send (response, http_receive)
		http_response_delete (response)

	else:
		response = http_response_json_msg (
			HTTP_STATUS_BAD_REQUEST, b"Missing user values!"
		)

		http_response_print (response)
		http_response_send (response, http_receive)
		http_response_delete (response)

# POST /api/users/login
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def users_login_handler (http_receive, request):
	body_values = http_request_get_body_values (request)
	username = http_query_pairs_get_value (body_values, b"username")
	password = http_query_pairs_get_value (body_values, b"password")

	if username is not None and password is not None:
		user = user_get_by_username (username.contents.str)
		if user is not None:
			if user.password == password.contents.str:
				http_jwt = http_cerver_auth_jwt_new ();
				http_cerver_auth_jwt_add_value_int (http_jwt, b"iat", int (time.time ()))
				http_cerver_auth_jwt_add_value (http_jwt, b"id", user.id.encode ("utf-8"))
				http_cerver_auth_jwt_add_value (http_jwt, b"name", user.name)
				http_cerver_auth_jwt_add_value (http_jwt, b"username", user.username)
				http_cerver_auth_jwt_add_value (http_jwt, b"role", user.role.encode ("utf-8"))

				http_cerver_auth_generate_bearer_jwt_json (http_receive_get_cerver (http_receive), http_jwt)

				response = http_response_create (
					HTTP_STATUS_OK, http_jwt_get_json (http_jwt), http_jwt_get_json_len (http_jwt)
				)

				http_cerver_auth_jwt_delete (http_jwt)

				http_response_compile (response);
				http_response_print (response)
				http_response_send (response, http_receive)
				http_response_delete (response)
			else:
				response = http_response_json_msg (
					HTTP_STATUS_BAD_REQUEST, b"Wrong password!"
				)

				http_response_print (response)
				http_response_send (response, http_receive)
				http_response_delete (response)
		else:
			response = http_response_json_msg (
				HTTP_STATUS_NOT_FOUND, b"User not found!"
			)

			http_response_print (response)
			http_response_send (response, http_receive)
			http_response_delete (response)
	else:
		response = http_response_json_msg (
			HTTP_STATUS_BAD_REQUEST, b"Missing user values!"
		)

		http_response_print (response)
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /api/users/profile
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def users_profile_handler (http_receive, request):
	json_string = ctypes.cast (http_request_get_decoded_data (request), ctypes.c_char_p)
	user_dict = json.loads (json_string.value)
	user = User (**user_dict)

	message = "%s profile!" % (user.username)

	response = http_response_json_msg (
		HTTP_STATUS_OK, message.encode ("utf-8")
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)
		

def start ():
	global web_service
	web_service = cerver_create_web (
		b"api-cerver", 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (web_service, 4096);
	cerver_set_thpool_n_threads (web_service, 4);
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS);

	cerver_set_reusable_address_flags (web_service, True);

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	http_cerver_auth_set_jwt_algorithm (http_cerver, JWT_ALG_RS256)
	http_cerver_auth_set_jwt_priv_key_filename (http_cerver, b"keys/key.key")
	http_cerver_auth_set_jwt_pub_key_filename (http_cerver, b"keys/key.pub")

	# GET /api/users
	users_route = http_route_create (REQUEST_METHOD_GET, b"api/users", main_users_handler)
	http_cerver_route_register (http_cerver, users_route)

	# POST api/users/register
	users_register_route = http_route_create (REQUEST_METHOD_POST, b"register", users_register_handler)
	http_route_child_add (users_route, users_register_route)

	# POST api/users/login
	users_login_route = http_route_create (REQUEST_METHOD_POST, b"login", users_login_handler)
	http_route_child_add (users_route, users_login_route)

	# GET api/users/profile
	users_profile_route = http_route_create (REQUEST_METHOD_GET, b"profile", users_profile_handler)
	http_route_set_auth (users_profile_route, HTTP_ROUTE_AUTH_TYPE_BEARER);
	http_route_set_decode_data_into_json (users_profile_route);
	http_route_child_add (users_route, users_profile_route);

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
