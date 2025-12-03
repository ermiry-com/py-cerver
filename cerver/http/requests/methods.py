"""The methods of a request."""

from ctypes import c_int, c_char_p, c_bool
from typing import TypeAlias

from ...lib import lib_function

__all__ = [
	"RequestMethod",
	"REQUEST_METHOD_DELETE", "REQUEST_METHOD_GET", "REQUEST_METHOD_HEAD", "REQUEST_METHOD_POST",
	"REQUEST_METHOD_PUT", "REQUEST_METHOD_CONNECT", "REQUEST_METHOD_OPTIONS", "REQUEST_METHOD_TRACE",
	"REQUEST_METHOD_PATCH", "REQUEST_METHOD_UNDEFINED", "REQUEST_METHOD_SIZE",
	"http_request_method_str", "http_request_method_is_valid", "http_method_str"
]

RequestMethod: TypeAlias = c_int # type: ignore

# the values are the ones of the HTTP parser
REQUEST_METHOD_DELETE = 0
REQUEST_METHOD_GET = 1
REQUEST_METHOD_HEAD = 2
REQUEST_METHOD_POST = 3
REQUEST_METHOD_PUT = 4
REQUEST_METHOD_CONNECT = 5
REQUEST_METHOD_OPTIONS = 6
REQUEST_METHOD_TRACE = 7
REQUEST_METHOD_PATCH = 28

# any other method of the parser is undefined
REQUEST_METHOD_UNDEFINED = 34

# the size of the tables indexed by a request method
REQUEST_METHOD_SIZE = 29

http_request_method_str = lib_function (
	"http_request_method_str", [RequestMethod], c_char_p,
	"""Returns the name of a request method.

	Args:
		request_method: A REQUEST_METHOD_* value.

	Returns:
		The name, as bytes, like b"GET".
	"""
)

http_request_method_is_valid = lib_function (
	"http_request_method_is_valid", [RequestMethod], c_bool,
	"""Returns if a request method is one that cerver handles.

	Args:
		request_method: A REQUEST_METHOD_* value.

	Returns:
		True if it is valid.
	"""
)

http_method_str = lib_function (
	"http_method_str", [c_int], c_char_p,
	"""Returns the name of a method of the HTTP parser.

	Args:
		m: A method of the parser, the REQUEST_METHOD_* values are among them.

	Returns:
		The name, as bytes.
	"""
)
