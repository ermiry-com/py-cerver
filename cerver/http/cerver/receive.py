"""The HttpReceive of a request: the connection, the cerver and the endpoint that handle it."""

from ctypes import c_void_p, c_char_p, c_int, c_bool
from typing import TypeAlias

from ...lib import lib_function

__all__ = [
	"HttpReceiveStatus",
	"HTTP_RECEIVE_STATUS_NONE", "HTTP_RECEIVE_STATUS_HEADERS", "HTTP_RECEIVE_STATUS_BODY",
	"HTTP_RECEIVE_STATUS_COMPLETED", "HTTP_RECEIVE_STATUS_INCOMPLETED", "HTTP_RECEIVE_STATUS_UNHANDLED",
	"HTTP_RECEIVE_STATUS_TIMEOUT", "HTTP_RECEIVE_STATUS_CLOSED", "HTTP_RECEIVE_STATUS_PARSER_ERROR",
	"HTTP_RECEIVE_STATUS_LIMIT", "HTTP_RECEIVE_STATUS_REJECTED", "HTTP_RECEIVE_STATUS_UPLOAD_ERROR",
	"http_receive_status_str",
	"http_receive_get_cerver_receive", "http_receive_get_sock_fd", "http_receive_get_cerver",
	"http_receive_get_endpoint", "http_receive_get_route_custom_data",
	"http_receive_get_cerver_custom_data", "http_receive_is_head", "http_receive_get_allow"
]

HttpReceiveStatus: TypeAlias = c_int # type: ignore

HTTP_RECEIVE_STATUS_NONE = 0
HTTP_RECEIVE_STATUS_HEADERS = 1
HTTP_RECEIVE_STATUS_BODY = 2
HTTP_RECEIVE_STATUS_COMPLETED = 3
HTTP_RECEIVE_STATUS_INCOMPLETED = 4
HTTP_RECEIVE_STATUS_UNHANDLED = 5
HTTP_RECEIVE_STATUS_TIMEOUT = 6
HTTP_RECEIVE_STATUS_CLOSED = 7
HTTP_RECEIVE_STATUS_PARSER_ERROR = 8
HTTP_RECEIVE_STATUS_LIMIT = 9
HTTP_RECEIVE_STATUS_REJECTED = 10
HTTP_RECEIVE_STATUS_UPLOAD_ERROR = 11

http_receive_status_str = lib_function (
	"http_receive_status_str", [HttpReceiveStatus], c_char_p,
	"""Returns the name of a receive status.

	Args:
		status: An HTTP_RECEIVE_STATUS_* value.

	Returns:
		The name, as bytes.
	"""
)

http_receive_get_cerver_receive = lib_function (
	"http_receive_get_cerver_receive", [c_void_p], c_void_p,
	"""Returns the CerverReceive of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The CerverReceive.
	"""
)

http_receive_get_sock_fd = lib_function (
	"http_receive_get_sock_fd", [c_void_p], c_int,
	"""Returns the socket of the connection of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The socket.
	"""
)

http_receive_get_cerver = lib_function (
	"http_receive_get_cerver", [c_void_p], c_void_p,
	"""Returns the HttpCerver that handles a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The HttpCerver.
	"""
)

http_receive_get_endpoint = lib_function (
	"http_receive_get_endpoint", [c_void_p], c_void_p,
	"""Returns the endpoint that handles a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The HttpEndpoint, None if no endpoint matched.
	"""
)

http_receive_get_route_custom_data = lib_function (
	"http_receive_get_route_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of the endpoint of a request (its own, its group's or its route's).

	Args:
		http_receive: The HttpReceive.

	Returns:
		The data, None if it has none.
	"""
)

http_receive_get_cerver_custom_data = lib_function (
	"http_receive_get_cerver_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of the HttpCerver of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The data, None if it has none.
	"""
)

http_receive_is_head = lib_function (
	"http_receive_is_head", [c_void_p], c_bool,
	"""Returns if a request is a HEAD handled by the GET handler, its responses are sent without body.

	Args:
		http_receive: The HttpReceive.

	Returns:
		True for a HEAD.
	"""
)

http_receive_get_allow = lib_function (
	"http_receive_get_allow", [c_void_p], c_char_p,
	"""Returns the value of the Allow header of the path of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The methods, as bytes.
	"""
)
