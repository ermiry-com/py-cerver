"""The admin routes of an HTTP cerver: info, stats, metrics, file systems and workers."""

from ctypes import c_void_p, c_char_p, c_bool

from ...lib import lib_function

from ..routes import HttpRouteAuthType

__all__ = [
	"HTTP_CERVER_DEFAULT_ENABLE_ADMIN", "HTTP_CERVER_DEFAULT_ENABLE_ADMIN_INFO",
	"HTTP_CERVER_DEFAULT_ENABLE_ADMIN_HEADS", "HTTP_CERVER_DEFAULT_ENABLE_ADMIN_OPTIONS",
	"HTTP_CERVER_DEFAULT_ENABLE_ADMIN_AUTH", "HTTP_CERVER_DEFAULT_ENABLE_ADMIN_CORS",
	"http_cerver_enable_admin_routes", "http_cerver_enable_admin_info_route",
	"http_cerver_enable_admin_head_handlers", "http_cerver_enable_admin_options_handlers",
	"http_cerver_enable_admin_routes_authentication",
	"http_cerver_admin_routes_auth_set_decode_data", "http_cerver_admin_routes_auth_decode_to_json",
	"http_cerver_admin_routes_set_authentication_handler",
	"http_cerver_admin_routes_set_custom_data", "http_cerver_admin_routes_set_delete_custom_data",
	"http_cerver_enable_admin_cors_headers", "http_cerver_admin_set_origin",
	"http_cerver_register_admin_file_system", "http_cerver_register_admin_worker"
]

HTTP_CERVER_DEFAULT_ENABLE_ADMIN = False
HTTP_CERVER_DEFAULT_ENABLE_ADMIN_INFO = True
HTTP_CERVER_DEFAULT_ENABLE_ADMIN_HEADS = False
HTTP_CERVER_DEFAULT_ENABLE_ADMIN_OPTIONS = False
HTTP_CERVER_DEFAULT_ENABLE_ADMIN_AUTH = False
HTTP_CERVER_DEFAULT_ENABLE_ADMIN_CORS = False

http_cerver_enable_admin_routes = lib_function (
	"http_cerver_enable_admin_routes", [c_void_p, c_bool], None,
	"""Enables the admin routes (/cerver/info, /cerver/stats, /cerver/metrics...).

	Args:
		http_cerver: The HttpCerver.
		enable: True to enable them.
	"""
)

http_cerver_enable_admin_info_route = lib_function (
	"http_cerver_enable_admin_info_route", [c_void_p, c_bool], None,
	"""Enables the info route of the admin routes.

	Args:
		http_cerver: The HttpCerver.
		enable: True (the default) to enable it.
	"""
)

http_cerver_enable_admin_head_handlers = lib_function (
	"http_cerver_enable_admin_head_handlers", [c_void_p, c_bool], None,
	"""Enables the HEAD handlers of the admin routes.

	Args:
		http_cerver: The HttpCerver.
		enable: True to enable them.
	"""
)

http_cerver_enable_admin_options_handlers = lib_function (
	"http_cerver_enable_admin_options_handlers", [c_void_p, c_bool], None,
	"""Enables the OPTIONS handlers of the admin routes.

	Args:
		http_cerver: The HttpCerver.
		enable: True to enable them.
	"""
)

http_cerver_enable_admin_routes_authentication = lib_function (
	"http_cerver_enable_admin_routes_authentication", [c_void_p, HttpRouteAuthType], None,
	"""Sets how the admin routes authenticate their requests.

	Args:
		http_cerver: The HttpCerver.
		auth_type: HTTP_ROUTE_AUTH_TYPE_BEARER or HTTP_ROUTE_AUTH_TYPE_CUSTOM.
	"""
)

http_cerver_admin_routes_auth_set_decode_data = lib_function (
	"http_cerver_admin_routes_auth_set_decode_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets how the bearer admin routes create the decoded data of the JWT.

	Args:
		http_cerver: The HttpCerver.
		decode_data: An HttpDecodeData kept by the caller.
		delete_decoded_data: An HttpDeleteDecoded kept by the caller, or None.
	"""
)

http_cerver_admin_routes_auth_decode_to_json = lib_function (
	"http_cerver_admin_routes_auth_decode_to_json", [c_void_p], None,
	"""Makes the bearer admin routes decode the values of the JWT into a JSON string.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_admin_routes_set_authentication_handler = lib_function (
	"http_cerver_admin_routes_set_authentication_handler", [c_void_p, c_void_p], None,
	"""Sets the handler that authenticates the requests of the custom admin routes.

	Args:
		http_cerver: The HttpCerver.
		authentication_handler: An HttpAuthenticationHandler kept by the caller, or the
			address of a C function.
	"""
)

http_cerver_admin_routes_set_custom_data = lib_function (
	"http_cerver_admin_routes_set_custom_data", [c_void_p, c_void_p], None,
	"""Sets the custom data of the admin routes.

	Args:
		http_cerver: The HttpCerver.
		custom_data: The data.
	"""
)

http_cerver_admin_routes_set_delete_custom_data = lib_function (
	"http_cerver_admin_routes_set_delete_custom_data", [c_void_p, c_void_p], None,
	"""Sets how the custom data of the admin routes is released.

	Args:
		http_cerver: The HttpCerver.
		delete_custom_data: A RouteDeleteCustom kept by the caller, the address of a C function, or None.
	"""
)

http_cerver_enable_admin_cors_headers = lib_function (
	"http_cerver_enable_admin_cors_headers", [c_void_p, c_bool], None,
	"""Adds the CORS headers to the responses of the admin routes.

	Args:
		http_cerver: The HttpCerver.
		enable: True to add them.
	"""
)

http_cerver_admin_set_origin = lib_function (
	"http_cerver_admin_set_origin", [c_void_p, c_char_p], None,
	"""Sets the origin of the CORS headers of the admin routes.

	Args:
		http_cerver: The HttpCerver.
		domain: The origin, as bytes.
	"""
)

http_cerver_register_admin_file_system = lib_function (
	"http_cerver_register_admin_file_system", [c_void_p, c_char_p], None,
	"""Adds a path whose disk usage the admin routes report.

	Args:
		http_cerver: The HttpCerver.
		path: The path, as bytes.
	"""
)

http_cerver_register_admin_worker = lib_function (
	"http_cerver_register_admin_worker", [c_void_p, c_void_p], None,
	"""Adds a worker whose state the admin routes report.

	Args:
		http_cerver: The HttpCerver.
		worker: The C worker, like Worker.worker.
	"""
)
