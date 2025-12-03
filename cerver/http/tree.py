"""The routes tree: groups of endpoints with settings that their endpoints inherit."""

from ctypes import create_string_buffer
from ctypes import c_void_p, c_int, c_char_p, c_bool, c_size_t, c_uint8
from typing import TypeAlias

from ..lib import lib_function, lib_c_string, lib_text

from ..types.string import StringPointer

from .requests.methods import RequestMethod
from .routes import HttpRouteModifier, HttpRouteAuthType

__all__ = [
	"HTTP_TREE_DEFAULT_MAX_PARAMS", "HTTP_TREE_ERROR_SIZE",
	"HttpTrailingSlash",
	"HTTP_TRAILING_SLASH_NONE", "HTTP_TRAILING_SLASH_TOLERANT",
	"HTTP_TRAILING_SLASH_STRICT", "HTTP_TRAILING_SLASH_REDIRECT",
	"http_trailing_slash_to_string", "http_trailing_slash_description",
	"http_cerver_group_create", "http_group_create", "http_group_get_prefix",
	"http_group_route_add", "http_group_root_add",
	"http_group_get", "http_group_post", "http_group_put", "http_group_patch", "http_group_delete_route",
	"http_group_set_modifier", "http_group_set_auth", "http_group_set_decode_data",
	"http_group_set_decode_data_into_json", "http_group_set_authentication_handler",
	"http_group_set_authentication_with_body", "http_group_set_custom_data",
	"http_group_set_max_body_size", "http_group_set_cors", "http_group_set_etag",
	"http_group_set_compression", "http_group_add_before", "http_group_add_after",
	"http_endpoint_get_path", "http_endpoint_get_method",
	"http_endpoint_set_modifier", "http_endpoint_set_auth", "http_endpoint_set_decode_data",
	"http_endpoint_set_decode_data_into_json", "http_endpoint_set_authentication_handler",
	"http_endpoint_set_authentication_with_body", "http_endpoint_set_custom_data",
	"http_endpoint_get_custom_data", "http_endpoint_set_max_body_size", "http_endpoint_set_cors",
	"http_endpoint_set_etag", "http_endpoint_set_compression",
	"http_endpoint_add_before", "http_endpoint_add_after",
	"http_tree_path_validate", "http_tree_print", "http_tree_get_n_endpoints",
	"http_tree_path_error"
]

HTTP_TREE_DEFAULT_MAX_PARAMS = 16
HTTP_TREE_ERROR_SIZE = 256

HttpTrailingSlash: TypeAlias = c_int # type: ignore

HTTP_TRAILING_SLASH_NONE = 0
HTTP_TRAILING_SLASH_TOLERANT = 1
HTTP_TRAILING_SLASH_STRICT = 2
HTTP_TRAILING_SLASH_REDIRECT = 3

http_trailing_slash_to_string = lib_function (
	"http_trailing_slash_to_string", [HttpTrailingSlash], c_char_p,
	"""Returns the name of a trailing slash policy.

	Args:
		trailing_slash: An HTTP_TRAILING_SLASH_* value.

	Returns:
		The name, as bytes.
	"""
)

http_trailing_slash_description = lib_function (
	"http_trailing_slash_description", [HttpTrailingSlash], c_char_p,
	"""Returns the description of a trailing slash policy.

	Args:
		trailing_slash: An HTTP_TRAILING_SLASH_* value.

	Returns:
		The description, as bytes.
	"""
)

# groups
http_cerver_group_create = lib_function (
	"http_cerver_group_create", [c_void_p, c_char_p], c_void_p,
	"""Creates a top level group of an HTTP cerver.

	Args:
		http_cerver: The HttpCerver.
		prefix: The prefix of its paths, as bytes, None, b"" or b"/" for the root.

	Returns:
		The HttpGroup, None on error (the error is kept and the cerver does not start).
	"""
)

http_group_create = lib_function (
	"http_group_create", [c_void_p, c_char_p], c_void_p,
	"""Creates a group inside another one.

	Args:
		parent: The HttpGroup.
		prefix: The prefix relative to the parent, as bytes.

	Returns:
		The HttpGroup, None on error.
	"""
)

http_group_get_prefix = lib_function (
	"http_group_get_prefix", [c_void_p], StringPointer,
	"""Returns the complete prefix of a group.

	Args:
		group: The HttpGroup.

	Returns:
		A StringPointer.
	"""
)

http_group_route_add = lib_function (
	"http_group_route_add", [c_void_p, RequestMethod, c_char_p, c_void_p], c_void_p,
	"""Adds an endpoint to a group.

	The path is relative to the group: ":name" is a param, ":name<validator>" a param with a
	validator and "*name" (only in the last segment) matches the rest of the path.

	Args:
		group: The HttpGroup.
		method: A REQUEST_METHOD_* value.
		path: The path, as bytes.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error (the error is kept and the cerver does not start).
	"""
)

http_group_root_add = lib_function (
	"http_group_root_add", [c_void_p, RequestMethod, c_void_p], c_void_p,
	"""Adds the endpoint of a method in the path of the group itself, like GET /api/users.

	Args:
		group: The HttpGroup.
		method: A REQUEST_METHOD_* value.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error.
	"""
)

http_group_get = lib_function (
	"http_group_get", [c_void_p, c_char_p, c_void_p], c_void_p,
	"""Adds a GET endpoint to a group.

	Args:
		group: The HttpGroup.
		path: The path relative to the group, as bytes.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error.
	"""
)

http_group_post = lib_function (
	"http_group_post", [c_void_p, c_char_p, c_void_p], c_void_p,
	"""Adds a POST endpoint to a group.

	Args:
		group: The HttpGroup.
		path: The path relative to the group, as bytes.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error.
	"""
)

http_group_put = lib_function (
	"http_group_put", [c_void_p, c_char_p, c_void_p], c_void_p,
	"""Adds a PUT endpoint to a group.

	Args:
		group: The HttpGroup.
		path: The path relative to the group, as bytes.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error.
	"""
)

http_group_patch = lib_function (
	"http_group_patch", [c_void_p, c_char_p, c_void_p], c_void_p,
	"""Adds a PATCH endpoint to a group.

	Args:
		group: The HttpGroup.
		path: The path relative to the group, as bytes.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error.
	"""
)

http_group_delete_route = lib_function (
	"http_group_delete_route", [c_void_p, c_char_p, c_void_p], c_void_p,
	"""Adds a DELETE endpoint to a group.

	Args:
		group: The HttpGroup.
		path: The path relative to the group, as bytes.
		handler: An HttpHandler kept by the caller.

	Returns:
		The HttpEndpoint, None on error.
	"""
)

http_group_set_modifier = lib_function (
	"http_group_set_modifier", [c_void_p, HttpRouteModifier], None,
	"""Sets the modifier that the endpoints of a group inherit.

	Args:
		group: The HttpGroup.
		modifier: An HTTP_ROUTE_MODIFIER_* value.
	"""
)

http_group_set_auth = lib_function (
	"http_group_set_auth", [c_void_p, HttpRouteAuthType], None,
	"""Sets the auth type that the endpoints of a group inherit.

	Args:
		group: The HttpGroup.
		auth_type: An HTTP_ROUTE_AUTH_TYPE_* value.
	"""
)

http_group_set_decode_data = lib_function (
	"http_group_set_decode_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets how the bearer endpoints of a group create the decoded data of the JWT.

	Args:
		group: The HttpGroup.
		decode_data: An HttpDecodeData kept by the caller.
		delete_decoded_data: An HttpDeleteDecoded kept by the caller, or None.
	"""
)

http_group_set_decode_data_into_json = lib_function (
	"http_group_set_decode_data_into_json", [c_void_p], None,
	"""Makes the bearer endpoints of a group decode the values of the JWT into a JSON string.

	Args:
		group: The HttpGroup.
	"""
)

http_group_set_authentication_handler = lib_function (
	"http_group_set_authentication_handler", [c_void_p, c_void_p], None,
	"""Sets the authentication handler that the custom endpoints of a group inherit.

	Args:
		group: The HttpGroup.
		authentication_handler: An HttpAuthenticationHandler kept by the caller, or the
			address of a C function.
	"""
)

http_group_set_authentication_with_body = lib_function (
	"http_group_set_authentication_with_body", [c_void_p, c_bool], None,
	"""Authenticates the requests of the endpoints of a group after their body was received.

	Args:
		group: The HttpGroup.
		authentication_with_body: True when the authentication handler needs the body.
	"""
)

http_group_set_custom_data = lib_function (
	"http_group_set_custom_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets the custom data that the endpoints of a group inherit, the group owns it.

	Args:
		group: The HttpGroup.
		custom_data: The data.
		delete_custom_data: A RouteDeleteCustom kept by the caller, the address of a C
			function, or None to never release it.
	"""
)

http_group_set_max_body_size = lib_function (
	"http_group_set_max_body_size", [c_void_p, c_size_t], None,
	"""Sets the biggest body that the endpoints of a group accept (413 after it).

	Args:
		group: The HttpGroup.
		max_body_size: The size in bytes.
	"""
)

http_group_set_cors = lib_function (
	"http_group_set_cors", [c_void_p, c_bool], None,
	"""Adds Access-Control-Allow-Origin (from the whitelist) to the responses of the endpoints of a group.

	Args:
		group: The HttpGroup.
		cors: True to add it.
	"""
)

http_group_set_etag = lib_function (
	"http_group_set_etag", [c_void_p, c_bool], None,
	"""Adds a strong ETag to the responses of the endpoints of a group, and answers 304 when it matches.

	Args:
		group: The HttpGroup.
		etag: True to add it.
	"""
)

http_group_set_compression = lib_function (
	"http_group_set_compression", [c_void_p, c_bool], None,
	"""Compresses with gzip the responses of the endpoints of a group when the client accepts it.

	Args:
		group: The HttpGroup.
		compression: True to compress them.
	"""
)

http_group_add_before = lib_function (
	"http_group_add_before", [c_void_p, c_void_p], c_uint8,
	"""Adds a middleware that runs before the handlers of the endpoints of a group.

	Args:
		group: The HttpGroup.
		middleware: An HttpBeforeMiddleware kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

http_group_add_after = lib_function (
	"http_group_add_after", [c_void_p, c_void_p], c_uint8,
	"""Adds a middleware that runs after the handlers of the endpoints of a group.

	Args:
		group: The HttpGroup.
		middleware: An HttpAfterMiddleware kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

# endpoints
http_endpoint_get_path = lib_function (
	"http_endpoint_get_path", [c_void_p], StringPointer,
	"""Returns the complete path of an endpoint.

	Args:
		endpoint: The HttpEndpoint.

	Returns:
		A StringPointer.
	"""
)

http_endpoint_get_method = lib_function (
	"http_endpoint_get_method", [c_void_p], RequestMethod,
	"""Returns the method of an endpoint.

	Args:
		endpoint: The HttpEndpoint.

	Returns:
		A REQUEST_METHOD_* value.
	"""
)

http_endpoint_set_modifier = lib_function (
	"http_endpoint_set_modifier", [c_void_p, HttpRouteModifier], None,
	"""Sets the modifier of an endpoint.

	Args:
		endpoint: The HttpEndpoint.
		modifier: An HTTP_ROUTE_MODIFIER_* value.
	"""
)

http_endpoint_set_auth = lib_function (
	"http_endpoint_set_auth", [c_void_p, HttpRouteAuthType], None,
	"""Sets the auth type of an endpoint.

	Args:
		endpoint: The HttpEndpoint.
		auth_type: An HTTP_ROUTE_AUTH_TYPE_* value.
	"""
)

http_endpoint_set_decode_data = lib_function (
	"http_endpoint_set_decode_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets how a bearer endpoint creates the decoded data of the JWT.

	Args:
		endpoint: The HttpEndpoint.
		decode_data: An HttpDecodeData kept by the caller.
		delete_decoded_data: An HttpDeleteDecoded kept by the caller, or None.
	"""
)

http_endpoint_set_decode_data_into_json = lib_function (
	"http_endpoint_set_decode_data_into_json", [c_void_p], None,
	"""Makes a bearer endpoint decode the values of the JWT into a JSON string.

	Args:
		endpoint: The HttpEndpoint.
	"""
)

http_endpoint_set_authentication_handler = lib_function (
	"http_endpoint_set_authentication_handler", [c_void_p, c_void_p], None,
	"""Sets the authentication handler of a custom endpoint.

	Args:
		endpoint: The HttpEndpoint.
		authentication_handler: An HttpAuthenticationHandler kept by the caller, or the
			address of a C function.
	"""
)

http_endpoint_set_authentication_with_body = lib_function (
	"http_endpoint_set_authentication_with_body", [c_void_p, c_bool], None,
	"""Authenticates the requests of an endpoint after their body was received.

	Args:
		endpoint: The HttpEndpoint.
		authentication_with_body: True when the authentication handler needs the body.
	"""
)

http_endpoint_set_custom_data = lib_function (
	"http_endpoint_set_custom_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets the custom data of an endpoint, the endpoint owns it.

	Args:
		endpoint: The HttpEndpoint.
		custom_data: The data.
		delete_custom_data: A RouteDeleteCustom kept by the caller, the address of a C
			function, or None to never release it.
	"""
)

http_endpoint_get_custom_data = lib_function (
	"http_endpoint_get_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of an endpoint or the one that it inherits from its groups.

	Args:
		endpoint: The HttpEndpoint.

	Returns:
		The data, None if it has none.
	"""
)

http_endpoint_set_max_body_size = lib_function (
	"http_endpoint_set_max_body_size", [c_void_p, c_size_t], None,
	"""Sets the biggest body that an endpoint accepts (413 after it).

	Args:
		endpoint: The HttpEndpoint.
		max_body_size: The size in bytes.
	"""
)

http_endpoint_set_cors = lib_function (
	"http_endpoint_set_cors", [c_void_p, c_bool], None,
	"""Adds Access-Control-Allow-Origin (from the whitelist) to the responses of an endpoint.

	Args:
		endpoint: The HttpEndpoint.
		cors: True to add it.
	"""
)

http_endpoint_set_etag = lib_function (
	"http_endpoint_set_etag", [c_void_p, c_bool], None,
	"""Adds a strong ETag to the responses of an endpoint, and answers 304 when it matches.

	Args:
		endpoint: The HttpEndpoint.
		etag: True to add it.
	"""
)

http_endpoint_set_compression = lib_function (
	"http_endpoint_set_compression", [c_void_p, c_bool], None,
	"""Compresses with gzip the responses of an endpoint when the client accepts it.

	Args:
		endpoint: The HttpEndpoint.
		compression: True to compress them.
	"""
)

http_endpoint_add_before = lib_function (
	"http_endpoint_add_before", [c_void_p, c_void_p], c_uint8,
	"""Adds a middleware that runs before the handler of an endpoint.

	Args:
		endpoint: The HttpEndpoint.
		middleware: An HttpBeforeMiddleware kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

http_endpoint_add_after = lib_function (
	"http_endpoint_add_after", [c_void_p, c_void_p], c_uint8,
	"""Adds a middleware that runs after the handler of an endpoint.

	Args:
		endpoint: The HttpEndpoint.
		middleware: An HttpAfterMiddleware kept by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

# tree
http_tree_path_validate = lib_function (
	"http_tree_path_validate", [c_char_p, c_void_p, c_size_t], c_uint8,
	"""Validates the path of an endpoint, use http_tree_path_error () for the message.

	Args:
		path: The path, as bytes.
		error: A writable buffer that gets the error, or None.
		error_size: Its size, HTTP_TREE_ERROR_SIZE is enough.

	Returns:
		0 when it is valid, 1 on error.
	"""
)

http_tree_print = lib_function (
	"http_tree_print", [c_void_p], None,
	"""Prints a routes tree.

	Args:
		tree: The HttpTree.
	"""
)

http_tree_get_n_endpoints = lib_function (
	"http_tree_get_n_endpoints", [c_void_p], c_size_t,
	"""Returns how many endpoints a routes tree has.

	Args:
		tree: The HttpTree.

	Returns:
		The number of endpoints.
	"""
)

def http_tree_path_error (path: str | bytes) -> str | None:
	"""Validates the path of an endpoint.

	Args:
		path: The path, like "/users/:id<objectid>".

	Returns:
		The error, None when the path is valid.
	"""
	result = None

	buffer = create_string_buffer (HTTP_TREE_ERROR_SIZE)
	if (http_tree_path_validate (lib_c_string (path), buffer, HTTP_TREE_ERROR_SIZE)):
		result = lib_text (buffer.value)

	return result
