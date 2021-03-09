import os, signal, sys
import ctypes

import cerver

api_cerver = None

# end
def end (signum, frame):
	# cerver.cerver_stats_print (api_cerver, False, False)
	cerver.http_cerver_all_stats_print (cerver.http_cerver_get (api_cerver))
	cerver.cerver_teardown (api_cerver)
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

def start ():
	global api_cerver
	api_cerver = cerver.cerver_create_web (
		"api-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver.cerver_set_receive_buffer_size (api_cerver, 4096);
	cerver.cerver_set_thpool_n_threads (api_cerver, 4);
	cerver.cerver_set_handler_type (api_cerver, cerver.CERVER_HANDLER_TYPE_THREADS);

	cerver.cerver_set_reusable_address_flags (api_cerver, True);

	# HTTP configuration
	http_cerver = cerver.http_cerver_get (api_cerver)

	cerver.http_cerver_auth_set_jwt_algorithm (http_cerver, JWT_ALG_RS256)
	cerver.http_cerver_auth_set_jwt_priv_key_filename (http_cerver, "keys/key.key".encode ('utf-8'))
	cerver.http_cerver_auth_set_jwt_pub_key_filename (http_cerver, "keys/key.key.pub".encode ('utf-8'))

	# GET /api/users
	users_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "/api/users".encode ('utf-8'), main_users_handler)
	cerver.http_cerver_route_register (http_cerver, users_route)

	# POST api/users/login
	users_login_route = cerver.http_route_create (cerver.REQUEST_METHOD_POST, "login".encode ('utf-8'), users_login_handler)
	cerver.http_route_child_add (users_route, users_login_route)

	# POST api/users/register
	users_register_route = cerver.http_route_create (cerver.REQUEST_METHOD_POST, "register".encode ('utf-8'), users_register_handler)
	cerver.http_route_child_add (users_route, users_register_route)

	# GET api/users/profile
	users_profile_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "profile".encode ('utf-8'), users_profile_handler)
	cerver.http_route_set_auth (users_profile_route, cerver.HTTP_ROUTE_AUTH_TYPE_BEARER);
	cerver.http_route_set_decode_data (users_profile_route, user_parse_from_json, user_delete);
	cerver.http_route_child_add (users_route, users_profile_route);

	# start
	cerver.cerver_start (api_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver.cerver_init ()

	cerver.cerver_version_print_full ()

	start ()
