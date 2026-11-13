"""The HttpCerver of a web cerver: its creation, its static paths, its data and its stats."""

from ctypes import c_void_p, c_char_p, c_uint8

from ...lib import lib_function, lib_c_string

from ...core.cerver import CERVER_DEFAULT_CONNECTION_QUEUE, CERVER_HANDLER_TYPE_THREADS
from ...core.cerver import cerver_create_web, cerver_set_alias, cerver_set_receive_buffer_size
from ...core.cerver import cerver_set_thpool_n_threads, cerver_set_handler_type
from ...core.cerver import cerver_set_reusable_address_flags

from ..headers import HttpHeaderType
from ..routes import HttpRouteAuthType, RouteDeleteCustom

__all__ = [
	"HTTP_CERVER_DEFAULT_PORT", "HTTP_CERVER_DEFAULT_BUFFER_SIZE", "HTTP_CERVER_DEFAULT_THREADS",
	"HttpDeleteCustom",
	"http_cerver_get", "http_cerver_configuration",
	"http_static_path_set_auth", "http_static_path_set_decode_data",
	"http_static_path_set_authentication_handler",
	"http_cerver_static_path_add", "http_receive_public_path_remove",
	"http_cerver_get_custom_data", "http_cerver_set_custom_data",
	"http_cerver_set_delete_custom_data", "http_cerver_set_default_delete_custom_data",
	"http_cerver_add_responses_header", "http_cerver_add_responses_header_by_name",
	"http_cerver_all_stats_print", "http_cerver_routes_stats_print", "http_cerver_route_stats_print"
]

HTTP_CERVER_DEFAULT_PORT = 8080
HTTP_CERVER_DEFAULT_BUFFER_SIZE = 4096
HTTP_CERVER_DEFAULT_THREADS = 4

# the suffix of the name of the cerver of http_cerver_configuration ()
HTTP_CERVER_NAME_SUFFIX = "-service"

# void (*) (void *), releases the custom data of an HTTP cerver
HttpDeleteCustom = RouteDeleteCustom

http_cerver_get = lib_function (
	"http_cerver_get", [c_void_p], c_void_p,
	"""Returns the HttpCerver of a web cerver.

	Args:
		cerver: The cerver of cerver_create_web ().

	Returns:
		The HttpCerver.
	"""
)

def http_cerver_configuration (
	name: str, port: int = HTTP_CERVER_DEFAULT_PORT,
	connection_queue: int = CERVER_DEFAULT_CONNECTION_QUEUE,
	buffer_size: int = HTTP_CERVER_DEFAULT_BUFFER_SIZE,
	n_threads: int = HTTP_CERVER_DEFAULT_THREADS,
	reusable_address_flags: bool = True
) -> int | None:
	"""Creates a web cerver with the configuration of a service.

	Its connections are handled by a thpool (CERVER_HANDLER_TYPE_THREADS).

	Args:
		name: The name of the service, its cerver is "<name>-service" and its alias the name.
		port: The port that it listens.
		connection_queue: The backlog of listen ().
		buffer_size: The size of the receive buffer.
		n_threads: The threads of the thpool, the requests that it handles at once.
		reusable_address_flags: True to set SO_REUSEADDR.

	Returns:
		The cerver, None on error.
	"""
	service = cerver_create_web (lib_c_string (f"{name}{HTTP_CERVER_NAME_SUFFIX}"), port, connection_queue)
	if (service):
		cerver_set_alias (service, lib_c_string (name))

		cerver_set_receive_buffer_size (service, buffer_size)
		cerver_set_thpool_n_threads (service, n_threads)
		cerver_set_handler_type (service, CERVER_HANDLER_TYPE_THREADS)
		cerver_set_reusable_address_flags (service, reusable_address_flags)

	return service

# public
http_static_path_set_auth = lib_function (
	"http_static_path_set_auth", [c_void_p, HttpRouteAuthType], None,
	"""Sets how the requests to a static path are authenticated.

	A request is authenticated with the static path that has its file, or with the first one
	that has authentication when none has it, so a file that does not exist is answered like
	a protected one; a request that fails it is answered with 401 before its file is looked for.

	Args:
		static_path: The HttpStaticPath.
		auth_type: An HTTP_ROUTE_AUTH_TYPE_* value.
	"""
)

http_static_path_set_decode_data = lib_function (
	"http_static_path_set_decode_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets how a bearer static path (HTTP_ROUTE_AUTH_TYPE_BEARER) creates the decoded data of the JWT.

	Args:
		static_path: The HttpStaticPath.
		decode_data: An HttpDecodeData kept by the caller.
		delete_decoded_data: An HttpDeleteDecoded kept by the caller that deletes it after the request, or None.
	"""
)

http_static_path_set_authentication_handler = lib_function (
	"http_static_path_set_authentication_handler", [c_void_p, c_void_p], None,
	"""Sets the method that authenticates the requests of a static path with HTTP_ROUTE_AUTH_TYPE_CUSTOM.

	Args:
		static_path: The HttpStaticPath.
		authentication_handler: An HttpAuthenticationHandler kept by the caller, it returns 0 on success
			and 1 on error.
	"""
)

http_cerver_static_path_add = lib_function (
	"http_cerver_static_path_add", [c_void_p, c_char_p], c_void_p,
	"""Adds a directory whose files are served when no endpoint matches.

	Args:
		http_cerver: The HttpCerver.
		static_path: The directory, as bytes.

	Returns:
		The HttpStaticPath, None on error.
	"""
)

http_receive_public_path_remove = lib_function (
	"http_receive_public_path_remove", [c_void_p, c_char_p], c_uint8,
	"""Removes a static path.

	Args:
		http_cerver: The HttpCerver.
		static_path: The directory, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

# data
http_cerver_get_custom_data = lib_function (
	"http_cerver_get_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of an HTTP cerver.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		The data, None if it has none.
	"""
)

http_cerver_set_custom_data = lib_function (
	"http_cerver_set_custom_data", [c_void_p, c_void_p], None,
	"""Sets the custom data of an HTTP cerver, the handlers get it with http_receive_get_cerver_custom_data ().

	Args:
		http_cerver: The HttpCerver.
		custom_data: The data.
	"""
)

http_cerver_set_delete_custom_data = lib_function (
	"http_cerver_set_delete_custom_data", [c_void_p, c_void_p], None,
	"""Sets how the custom data of an HTTP cerver is released.

	Args:
		http_cerver: The HttpCerver.
		delete_custom_data: An HttpDeleteCustom kept by the caller, or None.
	"""
)

http_cerver_set_default_delete_custom_data = lib_function (
	"http_cerver_set_default_delete_custom_data", [c_void_p], None,
	"""Releases the custom data of an HTTP cerver with free ().

	Args:
		http_cerver: The HttpCerver.
	"""
)

# responses
http_cerver_add_responses_header = lib_function (
	"http_cerver_add_responses_header", [c_void_p, HttpHeaderType, c_char_p], c_uint8,
	"""Adds a header to every response of an HTTP cerver that does not have it.

	Args:
		http_cerver: The HttpCerver.
		type: An HTTP_HEADER_* value.
		actual_header: The value, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_add_responses_header_by_name = lib_function (
	"http_cerver_add_responses_header_by_name", [c_void_p, c_char_p, c_char_p], c_uint8,
	"""Adds a header with any name to every response of an HTTP cerver that does not have it.

	Args:
		http_cerver: The HttpCerver.
		name: The name, as bytes, like b"X-Frame-Options".
		value: The value, as bytes, without a CR, a LF or a NUL.

	Returns:
		0 on success, 1 on error.
	"""
)

# stats
http_cerver_all_stats_print = lib_function (
	"http_cerver_all_stats_print", [c_void_p], None,
	"""Prints the stats of an HTTP cerver and of its routes.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_routes_stats_print = lib_function (
	"http_cerver_routes_stats_print", [c_void_p], None,
	"""Prints the stats of every route of an HTTP cerver.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_route_stats_print = lib_function (
	"http_cerver_route_stats_print", [c_void_p], None,
	"""Prints the stats of a route.

	Args:
		route: The HttpRoute.
	"""
)
