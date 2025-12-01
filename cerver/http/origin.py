"""The origins of the CORS whitelist."""

from ctypes import Structure, POINTER
from ctypes import c_int, c_char, c_char_p, c_void_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"HTTP_ORIGINS_SIZE", "HTTP_ORIGIN_VALUE_SIZE",
	"HttpOrigin", "HttpOriginPointer",
	"http_origin_new", "http_origin_delete",
	"http_origin_get_len", "http_origin_get_value",
	"http_origin_print"
]

HTTP_ORIGINS_SIZE = 16
HTTP_ORIGIN_VALUE_SIZE = 256

class HttpOrigin (Structure):
	"""An origin of the whitelist, ``HttpOrigin``.

	Attributes:
		len: The length of the value.
		value: The origin, NUL terminated.
	"""

	_fields_ = [
		("len", c_int),
		("value", c_char * HTTP_ORIGIN_VALUE_SIZE)
	]

HttpOriginPointer: TypeAlias = POINTER (HttpOrigin) # type: ignore

http_origin_new = lib_function (
	"http_origin_new", [], HttpOriginPointer,
	"""Allocates an empty origin.

	Returns:
		The HttpOrigin, released with http_origin_delete ().
	"""
)

http_origin_delete = lib_function (
	"http_origin_delete", [c_void_p], None,
	"""Releases an origin.

	Args:
		origin_ptr: The HttpOrigin.
	"""
)

http_origin_get_len = lib_function (
	"http_origin_get_len", [HttpOriginPointer], c_int,
	"""Returns the length of the value of an origin.

	Args:
		origin: The HttpOrigin.

	Returns:
		The length.
	"""
)

http_origin_get_value = lib_function (
	"http_origin_get_value", [HttpOriginPointer], c_char_p,
	"""Returns the value of an origin.

	Args:
		origin: The HttpOrigin.

	Returns:
		The value, as bytes.
	"""
)

http_origin_print = lib_function (
	"http_origin_print", [HttpOriginPointer], None,
	"""Prints an origin.

	Args:
		origin: The HttpOrigin.
	"""
)
