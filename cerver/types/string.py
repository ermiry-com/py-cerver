"""The String of cerver, the type of most of the texts that it returns."""

from ctypes import POINTER, Structure, c_size_t, c_char_p, c_void_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"String", "StringPointer",
	"str_new", "str_delete"
]

class String (Structure):
	"""A text of cerver with its length, ``struct _String``.

	Attributes:
		max_len: The size of its buffer.
		len: The length of the text, without the NUL.
		str: The text.
	"""

	_fields_ = [
		("max_len", c_size_t),
		("len", c_size_t),
		("str", c_char_p),
	]

StringPointer: TypeAlias = POINTER (String) # type: ignore

str_new = lib_function (
	"str_new", [c_char_p], StringPointer,
	"""Creates a String with a copy of a text.

	Args:
		str: The text, as bytes, or None for an empty one.

	Returns:
		The StringPointer, released with str_delete ().
	"""
)

str_delete = lib_function (
	"str_delete", [c_void_p], None,
	"""Releases a String that cerver created for the caller.

	Args:
		str_ptr: The StringPointer.
	"""
)
