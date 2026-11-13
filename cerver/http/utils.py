"""The byte ranges of the Range header."""

from ctypes import Structure, POINTER, c_int, c_long, c_char_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"RangeType",
	"HTTP_RANGE_TYPE_NONE", "HTTP_RANGE_TYPE_EMPTY", "HTTP_RANGE_TYPE_FIRST", "HTTP_RANGE_TYPE_FULL",
	"HTTP_RANGE_TYPE_SUFFIX",
	"BytesRange", "BytesRangePointer",
	"http_range_type_string", "http_bytes_range_init", "http_bytes_range_print"
]

RangeType: TypeAlias = c_int # type: ignore

HTTP_RANGE_TYPE_NONE = 0
HTTP_RANGE_TYPE_EMPTY = 1
HTTP_RANGE_TYPE_FIRST = 2
HTTP_RANGE_TYPE_FULL = 3

# bytes=-N, the last N bytes of the file: N is the end of the range until it is resolved with the size of the file
HTTP_RANGE_TYPE_SUFFIX = 4

class BytesRange (Structure):
	"""The bytes of a Range header, ``BytesRange``.

	Attributes:
		file_size: The size of the file.
		type: An HTTP_RANGE_TYPE_* value.
		start: The first byte.
		end: The last byte.
		chunk_size: The bytes of the range.
	"""

	_fields_ = [
		("file_size", c_long),

		("type", RangeType),
		("start", c_long),
		("end", c_long),
		("chunk_size", c_long)
	]

BytesRangePointer: TypeAlias = POINTER (BytesRange) # type: ignore

http_range_type_string = lib_function (
	"http_range_type_string", [RangeType], c_char_p,
	"""Returns the name of a range type.

	Args:
		range_type: An HTTP_RANGE_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

http_bytes_range_init = lib_function (
	"http_bytes_range_init", [BytesRangePointer], None,
	"""Initializes a BytesRange.

	Args:
		bytes_range: The BytesRange.
	"""
)

http_bytes_range_print = lib_function (
	"http_bytes_range_print", [BytesRangePointer], None,
	"""Prints a BytesRange.

	Args:
		bytes_range: The BytesRange.
	"""
)
