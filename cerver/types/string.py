"""The String of cerver, the type of most of the texts that it returns."""

from ctypes import POINTER, Structure, addressof, c_size_t, c_char_p, c_void_p, string_at
from typing import Any, TypeAlias

from ..lib import lib_function, lib_text

__all__ = [
	"String", "StringPointer",
	"str_new", "str_delete",
	"string_bytes", "string_text", "string_take_text"
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

def string_bytes (string: Any) -> bytes | None:
	"""Returns the bytes of a String of cerver, with its length (it may have NUL bytes).

	Args:
		string: A StringPointer, NULL (falsy) for a missing value.

	Returns:
		The bytes, None for a NULL String.
	"""
	result = None
	if (string):
		contents = string.contents

		# the address of the text itself, the field of c_char_p would stop at its first NUL
		text = c_void_p.from_address (addressof (contents) + String.str.offset).value
		result = string_at (text, contents.len) if (text) else b""

	return result

def string_text (string: Any) -> str | None:
	"""Returns the text of a String of cerver.

	Args:
		string: A StringPointer, NULL (falsy) for a missing value.

	Returns:
		The text, None for a NULL String or one that is not valid utf-8.
	"""
	return lib_text (string_bytes (string))

def string_take_text (string: Any) -> str | None:
	"""Returns the text of a String that cerver created for the caller and releases it.

	Args:
		string: A StringPointer, NULL (falsy) for a missing value.

	Returns:
		The text, None for a NULL String or one that is not valid utf-8.
	"""
	result = None
	if (string):
		result = string_text (string)
		str_delete (string)

	return result
