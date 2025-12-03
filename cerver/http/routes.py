"""The routes of the first routes API, and the types of the handlers of every route."""

from ctypes import CFUNCTYPE, POINTER
from ctypes import c_void_p, c_int, c_uint, c_char_p, c_bool, c_double, c_size_t
from typing import TypeAlias

from ..lib import lib_function

from .requests.methods import RequestMethod

__all__ = [
	"HTTP_ROUTE_STATS_DURATION_BUCKETS", "HTTP_ROUTE_METHODS_STRING_SIZE",
	"HttpRouteModifier",
	"HTTP_ROUTE_MODIFIER_NONE", "HTTP_ROUTE_MODIFIER_MULTI_PART", "HTTP_ROUTE_MODIFIER_WEB_SOCKET",
	"HttpRouteAuthType",
	"HTTP_ROUTE_AUTH_TYPE_NONE", "HTTP_ROUTE_AUTH_TYPE_BEARER", "HTTP_ROUTE_AUTH_TYPE_CUSTOM",
	"HttpHandler", "HttpAuthenticationHandler",
	"HttpDecodeData", "HttpDeleteDecoded", "RouteDeleteCustom",
	"http_route_modifier_to_string", "http_route_modifier_description",
	"http_route_auth_type_to_string", "http_route_auth_type_description",
	"http_route_stats_duration_buckets",
	"http_route_new", "http_route_delete", "http_route_create", "http_route_set_handler",
	"http_route_child_add", "http_route_set_modifier", "http_route_set_auth",
	"http_route_set_decode_data", "http_route_set_decode_data_into_json",
	"http_route_set_authentication_handler", "http_route_set_authentication_with_body",
	"http_route_get_custom_data", "http_route_set_custom_data", "http_route_set_delete_custom_data",
	"http_route_print", "http_route_methods_string",
	"http_route_duration_buckets"
]

# the buckets of the histogram of the durations of a route, in seconds
HTTP_ROUTE_STATS_DURATION_BUCKETS = 11

HTTP_ROUTE_METHODS_STRING_SIZE = 128

HttpRouteModifier: TypeAlias = c_int # type: ignore

HTTP_ROUTE_MODIFIER_NONE = 0
HTTP_ROUTE_MODIFIER_MULTI_PART = 1
HTTP_ROUTE_MODIFIER_WEB_SOCKET = 2

HttpRouteAuthType: TypeAlias = c_int # type: ignore

HTTP_ROUTE_AUTH_TYPE_NONE = 0
HTTP_ROUTE_AUTH_TYPE_BEARER = 1
HTTP_ROUTE_AUTH_TYPE_CUSTOM = 2

# void (*) (const HttpReceive *, const HttpRequest *), the handler of a route
HttpHandler: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p) # type: ignore

# unsigned int (*) (const HttpReceive *, const HttpRequest *), returns 0 when the request is authenticated
HttpAuthenticationHandler: TypeAlias = CFUNCTYPE (c_uint, c_void_p, c_void_p) # type: ignore

# void *(*) (void *), creates the decoded data of a JWT from its values
HttpDecodeData: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore
HttpDeleteDecoded: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

# void (*) (void *), releases the custom data of a route
RouteDeleteCustom: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

http_route_modifier_to_string = lib_function (
	"http_route_modifier_to_string", [HttpRouteModifier], c_char_p,
	"""Returns the name of a route modifier.

	Args:
		modifier: An HTTP_ROUTE_MODIFIER_* value.

	Returns:
		The name, as bytes.
	"""
)

http_route_modifier_description = lib_function (
	"http_route_modifier_description", [HttpRouteModifier], c_char_p,
	"""Returns the description of a route modifier.

	Args:
		modifier: An HTTP_ROUTE_MODIFIER_* value.

	Returns:
		The description, as bytes.
	"""
)

http_route_auth_type_to_string = lib_function (
	"http_route_auth_type_to_string", [HttpRouteAuthType], c_char_p,
	"""Returns the name of a route auth type.

	Args:
		type: An HTTP_ROUTE_AUTH_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

http_route_auth_type_description = lib_function (
	"http_route_auth_type_description", [HttpRouteAuthType], c_char_p,
	"""Returns the description of a route auth type.

	Args:
		type: An HTTP_ROUTE_AUTH_TYPE_* value.

	Returns:
		The description, as bytes.
	"""
)

http_route_stats_duration_buckets = lib_function (
	"http_route_stats_duration_buckets", [], POINTER (c_double),
	"""Returns the upper bounds of the buckets of the durations of the routes, use http_route_duration_buckets ().

	Returns:
		A pointer to HTTP_ROUTE_STATS_DURATION_BUCKETS doubles, in seconds.
	"""
)

http_route_new = lib_function (
	"http_route_new", [], c_void_p,
	"""Allocates an empty route.

	Returns:
		The HttpRoute, released with http_route_delete ().
	"""
)

http_route_delete = lib_function (
	"http_route_delete", [c_void_p], None,
	"""Releases a route that was never registered.

	Args:
		route_ptr: The HttpRoute.
	"""
)

http_route_create = lib_function (
	"http_route_create", [RequestMethod, c_char_p, c_void_p], c_void_p,
	"""Creates a route of the first routes API.

	Args:
		method: A REQUEST_METHOD_* value.
		actual_route: The path, as bytes, like b"api/users/:id".
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpRoute, owned by the cerver once it is registered.
	"""
)

http_route_set_handler = lib_function (
	"http_route_set_handler", [c_void_p, RequestMethod, c_void_p], None,
	"""Sets the handler of another method of a route.

	Args:
		route: The HttpRoute.
		method: A REQUEST_METHOD_* value.
		handler: An HttpHandler kept by the caller.
	"""
)

http_route_child_add = lib_function (
	"http_route_child_add", [c_void_p, c_void_p], None,
	"""Adds a child to a route, its path is relative to the parent.

	Args:
		parent: The HttpRoute.
		child: The child HttpRoute.
	"""
)

http_route_set_modifier = lib_function (
	"http_route_set_modifier", [c_void_p, HttpRouteModifier], None,
	"""Sets the modifier of a route.

	Args:
		route: The HttpRoute.
		modifier: HTTP_ROUTE_MODIFIER_MULTI_PART to receive uploads.
	"""
)

http_route_set_auth = lib_function (
	"http_route_set_auth", [c_void_p, HttpRouteAuthType], None,
	"""Sets how a route authenticates its requests.

	Args:
		route: The HttpRoute.
		auth_type: HTTP_ROUTE_AUTH_TYPE_BEARER (a JWT) or HTTP_ROUTE_AUTH_TYPE_CUSTOM.
	"""
)

http_route_set_decode_data = lib_function (
	"http_route_set_decode_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets how a bearer route creates the decoded data of the JWT.

	Args:
		route: The HttpRoute.
		decode_data: An HttpDecodeData kept by the caller.
		delete_decoded_data: An HttpDeleteDecoded kept by the caller, or None.
	"""
)

http_route_set_decode_data_into_json = lib_function (
	"http_route_set_decode_data_into_json", [c_void_p], None,
	"""Makes a bearer route decode the values of the JWT into a JSON string.

	Args:
		route: The HttpRoute.
	"""
)

http_route_set_authentication_handler = lib_function (
	"http_route_set_authentication_handler", [c_void_p, c_void_p], None,
	"""Sets the handler that authenticates the requests of a custom route.

	Args:
		route: The HttpRoute.
		authentication_handler: An HttpAuthenticationHandler kept by the caller.
	"""
)

http_route_set_authentication_with_body = lib_function (
	"http_route_set_authentication_with_body", [c_void_p, c_bool], None,
	"""Authenticates the requests of a route after their body was received.

	Args:
		route: The HttpRoute.
		authentication_with_body: True when the authentication handler needs the body.
	"""
)

http_route_get_custom_data = lib_function (
	"http_route_get_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of a route.

	Args:
		route: The HttpRoute.

	Returns:
		The data, None if it has none.
	"""
)

http_route_set_custom_data = lib_function (
	"http_route_set_custom_data", [c_void_p, c_void_p], None,
	"""Sets the custom data of a route.

	Args:
		route: The HttpRoute.
		custom_data: The data.
	"""
)

http_route_set_delete_custom_data = lib_function (
	"http_route_set_delete_custom_data", [c_void_p, c_void_p], None,
	"""Sets how the custom data of a route is released.

	Args:
		route: The HttpRoute.
		delete_custom_data: A RouteDeleteCustom kept by the caller, or the address of a C function.
	"""
)

http_route_print = lib_function (
	"http_route_print", [c_void_p], None,
	"""Prints a route.

	Args:
		route: The HttpRoute.
	"""
)

http_route_methods_string = lib_function (
	"http_route_methods_string", [c_void_p, c_void_p, c_size_t], c_size_t,
	"""Writes the methods that have a handler in an array of handlers, like the value of Allow.

	Args:
		handlers: The array of REQUEST_METHOD_SIZE handlers.
		buffer: A writable buffer.
		buffer_size: Its size, HTTP_ROUTE_METHODS_STRING_SIZE is enough.

	Returns:
		The length that was written.
	"""
)

def http_route_duration_buckets () -> list:
	"""Returns the upper bounds of the buckets of the durations of the routes.

	Returns:
		The bounds in seconds.
	"""
	buckets = http_route_stats_duration_buckets ()
	return [buckets[index] for index in range (HTTP_ROUTE_STATS_DURATION_BUCKETS)]
