import json

from ctypes import CFUNCTYPE, POINTER, cast, c_void_p
from ctypes import c_int, c_uint, c_uint8, c_char_p, c_bool, c_size_t

from ..lib import lib

from ..types.string import String

from ..cerver import CERVER_HANDLER_TYPE_THREADS, cerver_set_alias, cerver_create_web
from ..cerver import cerver_set_receive_buffer_size, cerver_set_thpool_n_threads
from ..cerver import cerver_set_handler_type, cerver_set_reusable_address_flags

from .alg import jwt_alg_t, JWT_ALG_NONE
from .headers import http_header
from .request import RequestMethod, http_request_get_decoded_data
from .response import http_response_json_custom_reference_send
from .route import HttpHandler, HttpRouteAuthType, HTTP_ROUTE_AUTH_TYPE_NONE
from .route import HttpDecodeData, HttpDeleteDecoded, AuthenticationHandler
from .route import http_route_create, http_route_child_add, http_route_set_auth
from .route import http_route_set_decode_data_into_json
from .status import http_status, HTTP_STATUS_OK

# types
CatchAllHandler = CFUNCTYPE (None, c_void_p, c_void_p)
NotFoundHandler = CFUNCTYPE (None, c_void_p, c_void_p)
UploadsFilenameGenerator = CFUNCTYPE (None, c_void_p, c_void_p)
UploadsDirnameGenerator = CFUNCTYPE (None, c_void_p, c_void_p)
HttpDeleteCustom = CFUNCTYPE (None, c_void_p)

# main
http_cerver_get = lib.http_cerver_get
http_cerver_get.argtypes = [c_void_p]
http_cerver_get.restype = c_void_p

def http_cerver_configuration (
	name: str, port=8080, connection_queue=10,
	buffer_size=4096, n_threads=4,
	reusable_address_flags=True
) -> c_void_p:
	"""
	Creates a HTTP cerver with custom configuration
	# Parameters
	------------
	### name: str
		The name of the HTTP service, used for internal values.
	### port: int, optional
		Port where service will be exposed. Defaults to 8080.
	### connection_queue: int, optional
		Defaults to 10.
	### buffer_size: int, optional
		Defaults to 4096.
	### n_threads: int, optional
		Number of concurrent requests that service will be able to handle
		Defaults to 4.
	### reusable_address_flags: bool, optional
		Defaults to True.
	# Returns
	------------
	Reference to the created Cerver instance
	"""
	service_name = f"{name}-service"
	service = cerver_create_web (
		service_name.encode ("utf-8"), port, connection_queue
	)

	cerver_set_alias (service, name.encode ("utf-8"))

	cerver_set_receive_buffer_size (service, buffer_size)
	cerver_set_thpool_n_threads (service, n_threads)
	cerver_set_handler_type (service, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_reusable_address_flags (service, reusable_address_flags)

	return service

# public
http_static_path_set_auth = lib.http_static_path_set_auth
http_static_path_set_auth.argtypes = [c_void_p, HttpRouteAuthType]

http_cerver_static_path_add = lib.http_cerver_static_path_add
http_cerver_static_path_add.argtypes = [c_void_p, c_char_p]
http_cerver_static_path_add.restype = c_void_p

http_receive_public_path_remove = lib.http_receive_public_path_remove
http_receive_public_path_remove.argtypes = [c_void_p, c_char_p]
http_receive_public_path_remove.restype = c_uint8

# routes
http_cerver_set_main_route = lib.http_cerver_set_main_route
http_cerver_set_main_route.argtypes = [c_void_p, c_void_p]

http_cerver_route_register = lib.http_cerver_route_register
http_cerver_route_register.argtypes = [c_void_p, c_void_p]

http_cerver_set_catch_all_route = lib.http_cerver_set_catch_all_route
http_cerver_set_catch_all_route.argtypes = [c_void_p, CatchAllHandler]

http_cerver_set_not_found_handler = lib.http_cerver_set_not_found_handler
http_cerver_set_not_found_handler.argtypes = [c_void_p]

http_cerver_set_not_found_route = lib.http_cerver_set_not_found_route
http_cerver_set_not_found_route.argtypes = [c_void_p, NotFoundHandler]

def http_create_route (
	http_cerver: c_void_p, request_method: RequestMethod,
	route_path: str, handler: HttpHandler,
	auth_method=HTTP_ROUTE_AUTH_TYPE_NONE
) -> c_void_p:
	"""
	Creates and registers a new HTTP route
	# Parameters
	------------
	### http_cerver: HttpCerver
		Reference to a HttpCerver instance.
	### request_method: RequestMethod
		The method this route will handle (GET, POST, ...)
	### route_path: str
		The actual route path.
	### handler: CFUNCTYPE (None, c_void_p, c_void_p)
		The callback handler method.
	### auth_method: HttpRouteAuthType, optional
		How the route will handle authentication.
	# Returns
	------------
	Reference to the registered HttpRoute instance
	"""
	route = http_route_create (
		request_method, route_path.encode ("utf-8"), handler
	)

	if (auth_method != HTTP_ROUTE_AUTH_TYPE_NONE):
		http_route_set_auth (route, auth_method)
		http_route_set_decode_data_into_json (route)

	# register main route to HTTP cerver
	http_cerver_route_register (http_cerver, route)

	return route

def http_create_child_route (
	parent: c_void_p, request_method: RequestMethod,
	route_path: str, handler: HttpHandler,
	auth_method=HTTP_ROUTE_AUTH_TYPE_NONE
) -> c_void_p:
	"""
	Creates and registers a child route to a parent
	# Parameters
	------------
	### parent: HttpRoute
		The parent HTTP route instance
	### request_method: RequestMethod.
		The method this route will handler (GET, POST, ...)
	### route_path: str
		The actual route path.
	### handler: CFUNCTYPE (None, c_void_p, c_void_p)
		The callback handler method.
	### auth_method: HttpRouteAuthType, optional
		How the route will handle authentication.
	# Returns
	------------
	Reference to the child HttpRoute instance
	"""
	child = http_route_create (
		request_method, route_path.encode ("utf-8"), handler
	)
	
	if (auth_method != HTTP_ROUTE_AUTH_TYPE_NONE):
		http_route_set_auth (child, auth_method)
		http_route_set_decode_data_into_json (child)

	# register child route to its parent
	http_route_child_add (parent, child)

	return child

# uploads
http_cerver_set_uploads_path = lib.http_cerver_set_uploads_path
http_cerver_set_uploads_path.argtypes = [c_void_p, c_char_p]

http_cerver_generate_uploads_path = lib.http_cerver_generate_uploads_path

http_cerver_set_uploads_file_mode = lib.http_cerver_set_uploads_file_mode
http_cerver_set_uploads_file_mode.argtypes = [c_void_p, c_uint]

http_cerver_set_uploads_filename_generator = lib.http_cerver_set_uploads_filename_generator
http_cerver_set_uploads_filename_generator.argtypes = [c_void_p, UploadsFilenameGenerator]

http_cerver_set_default_uploads_filename_generator = lib.http_cerver_set_default_uploads_filename_generator
http_cerver_set_default_uploads_filename_generator.argtypes = [c_void_p]

http_cerver_set_uploads_dir_mode = lib.http_cerver_set_uploads_dir_mode
http_cerver_set_uploads_dir_mode.argtypes = [c_void_p, c_uint]

http_cerver_set_uploads_dirname_generator = lib.http_cerver_set_uploads_dirname_generator
http_cerver_set_uploads_dirname_generator.argtypes = [c_void_p, UploadsDirnameGenerator]

http_cerver_set_default_uploads_dirname_generator = lib.http_cerver_set_default_uploads_dirname_generator
http_cerver_set_default_uploads_dirname_generator.argtypes = [c_void_p]

http_cerver_set_uploads_delete_when_done = lib.http_cerver_set_uploads_delete_when_done
http_cerver_set_uploads_delete_when_done.argtypes = [c_void_p, c_bool]

# auth
http_jwt_get_bearer = lib.http_jwt_get_bearer
http_jwt_get_bearer.argtypes = [c_void_p]
http_jwt_get_bearer.restype = c_char_p

http_jwt_get_bearer_len = lib.http_jwt_get_bearer_len
http_jwt_get_bearer_len.argtypes = [c_void_p]
http_jwt_get_bearer_len.restype = c_size_t

http_jwt_get_json = lib.http_jwt_get_json
http_jwt_get_json.argtypes = [c_void_p]
http_jwt_get_json.restype = c_char_p

http_jwt_get_json_len = lib.http_jwt_get_json_len
http_jwt_get_json_len.argtypes = [c_void_p]
http_jwt_get_json_len.restype = c_size_t

# sets the jwt algorithm used for encoding & decoding jwt tokens
# the default value is JWT_ALG_HS256
http_cerver_auth_set_jwt_algorithm = lib.http_cerver_auth_set_jwt_algorithm
http_cerver_auth_set_jwt_algorithm.argtypes = [c_void_p, jwt_alg_t]

# sets the filename from where the jwt private key will be loaded
http_cerver_auth_set_jwt_priv_key_filename = lib.http_cerver_auth_set_jwt_priv_key_filename
http_cerver_auth_set_jwt_priv_key_filename.argtypes = [c_void_p, c_char_p]

# sets the filename from where the jwt public key will be loaded
http_cerver_auth_set_jwt_pub_key_filename = lib.http_cerver_auth_set_jwt_pub_key_filename
http_cerver_auth_set_jwt_pub_key_filename.argtypes = [c_void_p, c_char_p]

http_cerver_auth_jwt_new = lib.http_cerver_auth_jwt_new
http_cerver_auth_jwt_new.restype = c_void_p

http_cerver_auth_jwt_delete = lib.http_cerver_auth_jwt_delete
http_cerver_auth_jwt_delete.argtypes = [c_void_p]

http_cerver_auth_jwt_add_value = lib.http_cerver_auth_jwt_add_value
http_cerver_auth_jwt_add_value.argtypes = [c_void_p, c_char_p, c_char_p]

http_cerver_auth_jwt_add_value_bool = lib.http_cerver_auth_jwt_add_value_bool
http_cerver_auth_jwt_add_value_bool.argtypes = [c_void_p, c_char_p, c_bool]

http_cerver_auth_jwt_add_value_int = lib.http_cerver_auth_jwt_add_value_int
http_cerver_auth_jwt_add_value_int.argtypes = [c_void_p, c_char_p, c_int]

http_cerver_auth_generate_bearer_jwt_json = lib.http_cerver_auth_generate_bearer_jwt_json
http_cerver_auth_generate_bearer_jwt_json.argtypes = [c_void_p, c_void_p]
http_cerver_auth_generate_bearer_jwt_json.restype = c_uint8

http_cerver_auth_generate_bearer_jwt_json_with_value = lib.http_cerver_auth_generate_bearer_jwt_json_with_value
http_cerver_auth_generate_bearer_jwt_json_with_value.argtypes = [c_void_p, c_void_p, c_char_p, c_char_p]
http_cerver_auth_generate_bearer_jwt_json_with_value.restype = c_uint8

def http_cerver_auth_configuration (
	http_cerver: c_void_p, jwt_algorithm=JWT_ALG_NONE,
	priv_key_filename=None, pub_key_filename=None
):
	"""
	Configurates the HTTP service's auth JWT algorithm and keys
	# Parameters
	------------
	### http_cerver: HttpCerver
		Reference to a HttpCerver instance.
	### jwt_algorithm: jwt_alg_t, optional
		The algorithm that will be used to manage JWTs.
		Must be the same as the one used to create the keys.
		Defaults to JWT_ALG_NONE.
	### priv_key_filename: string, optional.
		The private key filename.
	### pub_key_filename: string, optional.
		The public key filename.
	"""
	http_cerver_auth_set_jwt_algorithm (http_cerver, jwt_algorithm)
	if (jwt_algorithm != JWT_ALG_NONE):
		if (priv_key_filename):
			http_cerver_auth_set_jwt_priv_key_filename (
				http_cerver, priv_key_filename.encode ("utf-8")
			)

		if (pub_key_filename):
			http_cerver_auth_set_jwt_pub_key_filename (
				http_cerver, pub_key_filename.encode ("utf-8")
			)

def http_jwt_create (values={}):
	"""
	Creates a HttpJwt instance with custom values.
	Must be deleted with http_cerver_auth_jwt_delete () to avoid memory leaks
	# Parameters
	------------
	### values: dict, optional
		The actual Bearer JWT values. Defaults to {}.
	# Returns
	------------
	Reference to a HttpJwt instance
	"""
	http_jwt = http_cerver_auth_jwt_new ()
	for key in values:
		if (type (values[key]) == int):
			http_cerver_auth_jwt_add_value_int (
				http_jwt, key.encode ("utf-8"), values[key]
			)
		elif (type (values[key]) == bool):
			http_cerver_auth_jwt_add_value_bool (
				http_jwt, key.encode ("utf-8"), values[key]
			)
		elif (type (values[key]) == str):
			http_cerver_auth_jwt_add_value (
				http_jwt, key.encode ("utf-8"), values[key].encode ("utf-8")
			)

	return http_jwt


def http_jwt_create_and_send (
	http_receive: c_void_p,
	status_code=HTTP_STATUS_OK,
	values={}
):
	"""
	Creates and sends a Bearer JWT
	# Parameters
	------------
	### http_receive: HttpReceive
		Reference to a HttpReceive instance.
	### status_code: http_status, optional
		The HTTP response's status code. Defaults to HTTP_STATUS_OK.
	### values : dict, optional
		The actual Bearer JWT values. Defaults to {}.
	"""
	http_jwt = http_jwt_create (values)
	http_cerver_auth_generate_bearer_jwt_json (
		http_receive_get_cerver (http_receive), http_jwt
	)

	http_response_json_custom_reference_send (
		http_receive, status_code,
		http_jwt_get_json (http_jwt),
		http_jwt_get_json_len (http_jwt)
	)

	http_cerver_auth_jwt_delete (http_jwt)

def http_jwt_token_decode (request: c_void_p):
	"""
	Loads the decoded data from a JWT into a dict
	# Parameters
	------------
	### request: HttpRequest
		Reference to a HTTP request instance
	# Returns
	------------
	The JWT decoded data as a dict
	"""
	json_string = cast (http_request_get_decoded_data (request), c_char_p)
	return json.loads (json_string.value.decode ("utf-8"))

# origins
http_cerver_add_origin_to_whitelist = lib.http_cerver_add_origin_to_whitelist
http_cerver_add_origin_to_whitelist.argtypes = [c_void_p, c_char_p]
http_cerver_add_origin_to_whitelist.restype = c_uint8

http_cerver_print_origins_whitelist = lib.http_cerver_print_origins_whitelist
http_cerver_print_origins_whitelist.argtypes = [c_void_p]

# data
http_cerver_get_custom_data = lib.http_cerver_get_custom_data
http_cerver_get_custom_data.argtypes = [c_void_p]
http_cerver_get_custom_data.restype = c_void_p

http_cerver_set_custom_data = lib.http_cerver_set_custom_data
http_cerver_set_custom_data.argtypes = [c_void_p, c_void_p]

http_cerver_set_delete_custom_data = lib.http_cerver_set_delete_custom_data
http_cerver_set_delete_custom_data.argtypes = [c_void_p, HttpDeleteCustom]

http_cerver_set_default_delete_custom_data = lib.http_cerver_set_default_delete_custom_data
http_cerver_set_default_delete_custom_data.argtypes = [c_void_p]

# responses
http_cerver_add_responses_header = lib.http_cerver_add_responses_header
http_cerver_add_responses_header.argtypes = [c_void_p, http_header, c_char_p]
http_cerver_add_responses_header.restype = c_uint8

# stats
http_cerver_all_stats_print = lib.http_cerver_all_stats_print
http_cerver_all_stats_print.argtypes = [c_void_p]

# admin
http_cerver_enable_admin_routes = lib.http_cerver_enable_admin_routes
http_cerver_enable_admin_routes.argtypes = [c_void_p, c_bool]

http_cerver_enable_admin_info_route = lib.http_cerver_enable_admin_info_route
http_cerver_enable_admin_info_route.argtypes = [c_void_p, c_bool]

http_cerver_enable_admin_head_handlers = lib.http_cerver_enable_admin_head_handlers
http_cerver_enable_admin_head_handlers.argtypes = [c_void_p, c_bool]

http_cerver_enable_admin_options_handlers = lib.http_cerver_enable_admin_options_handlers
http_cerver_enable_admin_options_handlers.argtypes = [c_void_p, c_bool]

http_cerver_enable_admin_routes_authentication = lib.http_cerver_enable_admin_routes_authentication
http_cerver_enable_admin_routes_authentication.argtypes = [c_void_p, HttpRouteAuthType]

http_cerver_admin_routes_auth_set_decode_data = lib.http_cerver_admin_routes_auth_set_decode_data
http_cerver_admin_routes_auth_set_decode_data.argtypes = [c_void_p, HttpDecodeData, HttpDeleteDecoded]

http_cerver_admin_routes_auth_decode_to_json = lib.http_cerver_admin_routes_auth_decode_to_json
http_cerver_admin_routes_auth_decode_to_json.argtypes = [c_void_p]

http_cerver_admin_routes_set_authentication_handler = lib.http_cerver_admin_routes_set_authentication_handler
http_cerver_admin_routes_set_authentication_handler.argtypes = [c_void_p, AuthenticationHandler]

http_cerver_enable_admin_cors_headers = lib.http_cerver_enable_admin_cors_headers
http_cerver_enable_admin_cors_headers.argtypes = [c_void_p, c_bool]

http_cerver_admin_set_origin = lib.http_cerver_admin_set_origin
http_cerver_admin_set_origin.argtypes = [c_void_p, c_char_p]

http_cerver_register_admin_file_system = lib.http_cerver_register_admin_file_system
http_cerver_register_admin_file_system.argtypes = [c_void_p, c_char_p]

http_cerver_register_admin_worker = lib.http_cerver_register_admin_worker
http_cerver_register_admin_worker.argtypes = [c_void_p, c_void_p]

# handler
http_receive_get_cerver_receive = lib.http_receive_get_cerver_receive
http_receive_get_cerver_receive.argtypes = [c_void_p]
http_receive_get_cerver_receive.restype = c_void_p

http_receive_get_sock_fd = lib.http_receive_get_sock_fd
http_receive_get_sock_fd.argtypes = [c_void_p]
http_receive_get_sock_fd.restype = c_int

http_receive_get_cerver = lib.http_receive_get_cerver
http_receive_get_cerver.argtypes = [c_void_p]
http_receive_get_cerver.restype = c_void_p
