"""The routes of an HTTP cerver: registration, the handlers of the requests without a route, and compilation."""

import json

from ctypes import c_void_p, c_char_p, c_bool, c_size_t, c_uint, c_uint8

from ...lib import lib_function, lib_take_c_string, lib_c_string

from ..routes import HttpHandler, HTTP_ROUTE_AUTH_TYPE_NONE
from ..routes import http_route_create, http_route_child_add, http_route_set_auth
from ..routes import http_route_set_decode_data_into_json
from ..tree import HttpTrailingSlash

__all__ = [
	"CatchAllHandler", "NotFoundHandler",
	"http_cerver_set_main_route", "http_cerver_route_register",
	"http_cerver_set_catch_all_route", "http_cerver_set_not_found_handler",
	"http_cerver_set_not_found_route",
	"http_cerver_set_method_not_allowed", "http_cerver_set_method_not_allowed_handler",
	"http_cerver_set_trailing_slash", "http_cerver_set_max_route_params",
	"http_cerver_register_param_validator", "http_cerver_add_before", "http_cerver_add_after",
	"http_cerver_routes_error", "http_cerver_routes_errors_count", "http_cerver_routes_compile",
	"http_cerver_routes_print", "http_cerver_routes_generate_json", "http_cerver_routes_json_delete",
	"http_cerver_routes_json", "http_create_route", "http_create_child_route"
]

# void (*) (const HttpReceive *, const HttpRequest *)
CatchAllHandler = HttpHandler
NotFoundHandler = HttpHandler

TEXT_ENCODING = "utf-8"

http_cerver_set_main_route = lib_function (
	"http_cerver_set_main_route", [c_void_p, c_void_p], None,
	"""Sets the route of "/" of the first routes API.

	Args:
		http_cerver: The HttpCerver.
		route: The HttpRoute.
	"""
)

http_cerver_route_register = lib_function (
	"http_cerver_route_register", [c_void_p, c_void_p], None,
	"""Registers a route of the first routes API, the cerver owns it after this call.

	Args:
		http_cerver: The HttpCerver.
		route: The HttpRoute.
	"""
)

http_cerver_set_catch_all_route = lib_function (
	"http_cerver_set_catch_all_route", [c_void_p, c_void_p], None,
	"""Sets the handler of every request that no route matched.

	Args:
		http_cerver: The HttpCerver.
		catch_all_route: An HttpHandler kept by the caller.
	"""
)

http_cerver_set_not_found_handler = lib_function (
	"http_cerver_set_not_found_handler", [c_void_p], None,
	"""Answers the requests that no route matched with the default 404.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_set_not_found_route = lib_function (
	"http_cerver_set_not_found_route", [c_void_p, c_void_p], None,
	"""Sets the handler of the requests that no route matched.

	Args:
		http_cerver: The HttpCerver.
		not_found: An HttpHandler kept by the caller.
	"""
)

http_cerver_set_method_not_allowed = lib_function (
	"http_cerver_set_method_not_allowed", [c_void_p, c_bool], None,
	"""Answers a path without a handler for the method with 405 and Allow, instead of 404.

	Args:
		http_cerver: The HttpCerver.
		method_not_allowed: True to answer 405.
	"""
)

http_cerver_set_method_not_allowed_handler = lib_function (
	"http_cerver_set_method_not_allowed_handler", [c_void_p, c_void_p], None,
	"""Sets the handler of a path without a handler for the method.

	Args:
		http_cerver: The HttpCerver.
		handler: An HttpHandler kept by the caller, http_receive_get_allow () gives the methods.
	"""
)

http_cerver_set_trailing_slash = lib_function (
	"http_cerver_set_trailing_slash", [c_void_p, HttpTrailingSlash], None,
	"""Sets how a path with a trailing slash matches.

	Args:
		http_cerver: The HttpCerver.
		trailing_slash: HTTP_TRAILING_SLASH_TOLERANT (the default), _STRICT or _REDIRECT.
	"""
)

http_cerver_set_max_route_params = lib_function (
	"http_cerver_set_max_route_params", [c_void_p, c_uint], None,
	"""Sets the most params that a route can have.

	Args:
		http_cerver: The HttpCerver.
		max_params: The number of params, HTTP_TREE_DEFAULT_MAX_PARAMS by default.
	"""
)

http_cerver_register_param_validator = lib_function (
	"http_cerver_register_param_validator", [c_void_p, c_char_p, c_void_p], c_uint8,
	"""Registers a validator of params by its name, used in the routes as ":name<validator>".

	Args:
		http_cerver: The HttpCerver.
		name: The name, as bytes.
		validate: An HttpParamValidate kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_add_before = lib_function (
	"http_cerver_add_before", [c_void_p, c_void_p], c_uint8,
	"""Adds a middleware that runs before the handler of every endpoint.

	Args:
		http_cerver: The HttpCerver.
		middleware: An HttpBeforeMiddleware kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_add_after = lib_function (
	"http_cerver_add_after", [c_void_p, c_void_p], c_uint8,
	"""Adds a middleware that runs after the handler of every endpoint.

	Args:
		http_cerver: The HttpCerver.
		middleware: An HttpAfterMiddleware kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_routes_error = lib_function (
	"http_cerver_routes_error", [c_void_p], c_char_p,
	"""Returns the first error of the registration of the routes.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		The error, as bytes, None if there is none.
	"""
)

http_cerver_routes_errors_count = lib_function (
	"http_cerver_routes_errors_count", [c_void_p], c_size_t,
	"""Returns how many errors the registration of the routes had.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		The number of errors, the cerver does not start with any.
	"""
)

http_cerver_routes_compile = lib_function (
	"http_cerver_routes_compile", [c_void_p], c_uint8,
	"""Compiles the routes tree, cerver_start () does it if it was not done.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_routes_print = lib_function (
	"http_cerver_routes_print", [c_void_p], None,
	"""Prints the compiled routes of an HTTP cerver.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_routes_generate_json = lib_function (
	"http_cerver_routes_generate_json", [c_void_p], c_void_p,
	"""Returns the compiled endpoints as a JSON string, use http_cerver_routes_json ().

	Args:
		http_cerver: The HttpCerver.

	Returns:
		The address of the JSON, released with http_cerver_routes_json_delete ().
	"""
)

http_cerver_routes_json_delete = lib_function (
	"http_cerver_routes_json_delete", [c_void_p], None,
	"""Releases the JSON of http_cerver_routes_generate_json ().

	Args:
		json: The address of the JSON.
	"""
)

def http_cerver_routes_json (http_cerver: int) -> dict:
	"""Returns the compiled routes tree.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		{"n_endpoints": N, "endpoints": [...]}, each endpoint with its method, path, auth,
		modifier and if it comes from the first routes API; empty if the routes were not compiled.
	"""
	routes = dict ()

	routes_json = lib_take_c_string (http_cerver_routes_generate_json (http_cerver))
	if (routes_json):
		routes = json.loads (routes_json.decode (TEXT_ENCODING))

	return routes

def http_create_route (
	http_cerver: int, request_method: int, route_path: str, handler,
	auth_method: int = HTTP_ROUTE_AUTH_TYPE_NONE
) -> int:
	"""Creates and registers a route of the first routes API.

	Args:
		http_cerver: The HttpCerver.
		request_method: A REQUEST_METHOD_* value.
		route_path: The path.
		handler: An HttpHandler kept by the caller.
		auth_method: An HTTP_ROUTE_AUTH_TYPE_*, a bearer route decodes its JWT into JSON.

	Returns:
		The registered HttpRoute.
	"""
	route = http_route_create (request_method, lib_c_string (route_path), handler)

	if (auth_method != HTTP_ROUTE_AUTH_TYPE_NONE):
		http_route_set_auth (route, auth_method)
		http_route_set_decode_data_into_json (route)

	http_cerver_route_register (http_cerver, route)

	return route

def http_create_child_route (
	parent: int, request_method: int, route_path: str, handler,
	auth_method: int = HTTP_ROUTE_AUTH_TYPE_NONE
) -> int:
	"""Creates a route of the first routes API and adds it as a child of another one.

	Args:
		parent: The parent HttpRoute.
		request_method: A REQUEST_METHOD_* value.
		route_path: The path relative to the parent.
		handler: An HttpHandler kept by the caller.
		auth_method: An HTTP_ROUTE_AUTH_TYPE_*, a bearer route decodes its JWT into JSON.

	Returns:
		The child HttpRoute.
	"""
	child = http_route_create (request_method, lib_c_string (route_path), handler)

	if (auth_method != HTTP_ROUTE_AUTH_TYPE_NONE):
		http_route_set_auth (child, auth_method)
		http_route_set_decode_data_into_json (child)

	http_route_child_add (parent, child)

	return child
