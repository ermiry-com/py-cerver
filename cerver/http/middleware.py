"""The middlewares that run before and after the handler of a route."""

from ctypes import CFUNCTYPE, c_void_p, c_int, c_char_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"HttpMiddlewareResult",
	"HTTP_MIDDLEWARE_RESULT_NONE", "HTTP_MIDDLEWARE_RESULT_CONTINUE", "HTTP_MIDDLEWARE_RESULT_STOP",
	"HttpBeforeMiddleware", "HttpAfterMiddleware",
	"http_middleware_result_to_string", "http_middleware_result_description"
]

HttpMiddlewareResult: TypeAlias = c_int # type: ignore

HTTP_MIDDLEWARE_RESULT_NONE = 0
HTTP_MIDDLEWARE_RESULT_CONTINUE = 1
HTTP_MIDDLEWARE_RESULT_STOP = 2

# runs before the route handler with (http_receive, request), a middleware that returns
# HTTP_MIDDLEWARE_RESULT_STOP must send the response, any other value lets the request continue
HttpBeforeMiddleware: TypeAlias = CFUNCTYPE (HttpMiddlewareResult, c_void_p, c_void_p) # type: ignore

# runs after the route handler with (http_receive, request), the response was already sent
HttpAfterMiddleware: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p) # type: ignore

http_middleware_result_to_string = lib_function (
	"http_middleware_result_to_string", [HttpMiddlewareResult], c_char_p,
	"""Returns the name of a middleware result.

	Args:
		result: An HTTP_MIDDLEWARE_RESULT_* value.

	Returns:
		The name, as bytes.
	"""
)

http_middleware_result_description = lib_function (
	"http_middleware_result_description", [HttpMiddlewareResult], c_char_p,
	"""Returns the description of a middleware result.

	Args:
		result: An HTTP_MIDDLEWARE_RESULT_* value.

	Returns:
		The description, as bytes.
	"""
)
