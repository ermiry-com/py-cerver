"""A part of a multipart/form-data request: a value or an uploaded file."""

from ctypes import c_void_p, c_char_p
from ctypes import c_int, c_uint, c_uint32, c_bool
from typing import TypeAlias

from ..lib import lib_function, lib_c_string

from ..types.string import StringPointer

__all__ = [
	"HTTP_MULTI_PART_DIRNAME_SIZE", "HTTP_MULTI_PART_FILENAME_SIZE",
	"HTTP_MULTI_PART_GENERATED_FILENAME_SIZE", "HTTP_MULTI_PART_SAVED_FILENAME_SIZE",
	"HTTP_MULTI_PART_VALUE_SIZE", "HTTP_MULTI_PART_DEFAULT_FILENAME",
	"MultiPartType", "MULTI_PART_TYPE_NONE", "MULTI_PART_TYPE_FILE", "MULTI_PART_TYPE_VALUE",
	"http_multi_part_is_not_empty", "http_multi_part_get_type",
	"http_multi_part_is_file", "http_multi_part_is_value", "http_multi_part_get_name",
	"http_multi_part_get_filename", "http_multi_part_get_filename_len",
	"http_multi_part_get_generated_filename", "http_multi_part_get_generated_filename_len",
	"http_multi_part_set_generated_filename_variadic", "http_multi_part_set_generated_filename",
	"http_multi_part_get_n_reads", "http_multi_part_get_total_wrote",
	"http_multi_part_get_saved_filename", "http_multi_part_get_saved_filename_len",
	"http_multi_part_get_moved_file", "http_multi_part_get_value", "http_multi_part_get_value_len",
	"http_multi_part_move_file",
	"http_multi_part_headers_print", "http_multi_part_print",
	"http_multi_part_get_file"
]

HTTP_MULTI_PART_DIRNAME_SIZE = 1024
HTTP_MULTI_PART_FILENAME_SIZE = 256
HTTP_MULTI_PART_GENERATED_FILENAME_SIZE = 512
HTTP_MULTI_PART_SAVED_FILENAME_SIZE = 1024
HTTP_MULTI_PART_VALUE_SIZE = 256

HTTP_MULTI_PART_DEFAULT_FILENAME = "file"

# the format that sets a value as it is
MULTI_PART_FORMAT = b"%s"

MultiPartType: TypeAlias = c_int # type: ignore

MULTI_PART_TYPE_NONE = 0
MULTI_PART_TYPE_FILE = 1
MULTI_PART_TYPE_VALUE = 2

http_multi_part_is_not_empty = lib_function (
	"http_multi_part_is_not_empty", [c_void_p], c_bool,
	"""Returns if a part has a value or a file.

	Args:
		multi_part: The MultiPart.

	Returns:
		True if it is not empty.
	"""
)

http_multi_part_get_type = lib_function (
	"http_multi_part_get_type", [c_void_p], MultiPartType,
	"""Returns the type of a part.

	Args:
		multi_part: The MultiPart.

	Returns:
		MULTI_PART_TYPE_FILE or MULTI_PART_TYPE_VALUE.
	"""
)

http_multi_part_is_file = lib_function (
	"http_multi_part_is_file", [c_void_p], c_bool,
	"""Returns if a part is a file.

	Args:
		multi_part: The MultiPart.

	Returns:
		True for a file.
	"""
)

http_multi_part_is_value = lib_function (
	"http_multi_part_is_value", [c_void_p], c_bool,
	"""Returns if a part is a value.

	Args:
		multi_part: The MultiPart.

	Returns:
		True for a value.
	"""
)

http_multi_part_get_name = lib_function (
	"http_multi_part_get_name", [c_void_p], StringPointer,
	"""Returns the name of a part.

	Args:
		multi_part: The MultiPart.

	Returns:
		A StringPointer.
	"""
)

http_multi_part_get_filename = lib_function (
	"http_multi_part_get_filename", [c_void_p], c_char_p,
	"""Returns the original filename of a file part, sanitized.

	Args:
		multi_part: The MultiPart.

	Returns:
		The filename, as bytes.
	"""
)

http_multi_part_get_filename_len = lib_function (
	"http_multi_part_get_filename_len", [c_void_p], c_int,
	"""Returns the length of the original filename of a file part.

	Args:
		multi_part: The MultiPart.

	Returns:
		The length.
	"""
)

http_multi_part_get_generated_filename = lib_function (
	"http_multi_part_get_generated_filename", [c_void_p], c_char_p,
	"""Returns the filename that the uploads filename generator gave to a file part.

	Args:
		multi_part: The MultiPart.

	Returns:
		The filename, as bytes, b"" without a generator.
	"""
)

http_multi_part_get_generated_filename_len = lib_function (
	"http_multi_part_get_generated_filename_len", [c_void_p], c_int,
	"""Returns the length of the generated filename of a file part.

	Args:
		multi_part: The MultiPart.

	Returns:
		The length.
	"""
)

http_multi_part_set_generated_filename_variadic = lib_function (
	"http_multi_part_set_generated_filename", None, None,
	"""Sets the generated filename of a file part with a printf format (variadic).

	Args:
		multi_part: The MultiPart, as c_void_p.
		format: The format, as bytes, followed by its arguments.
	"""
)

def http_multi_part_set_generated_filename (mpart: int, filename: str | bytes) -> None:
	"""Sets the filename of a file part, from an uploads filename generator.

	Args:
		mpart: The MultiPart.
		filename: The filename.
	"""
	http_multi_part_set_generated_filename_variadic (
		c_void_p (mpart), c_char_p (MULTI_PART_FORMAT), c_char_p (lib_c_string (filename))
	)

http_multi_part_get_n_reads = lib_function (
	"http_multi_part_get_n_reads", [c_void_p], c_uint32,
	"""Returns how many reads it took to receive a file part.

	Args:
		multi_part: The MultiPart.

	Returns:
		The number of reads.
	"""
)

http_multi_part_get_total_wrote = lib_function (
	"http_multi_part_get_total_wrote", [c_void_p], c_uint32,
	"""Returns the bytes of a file part that were written to its file.

	Args:
		multi_part: The MultiPart.

	Returns:
		The bytes.
	"""
)

http_multi_part_get_saved_filename = lib_function (
	"http_multi_part_get_saved_filename", [c_void_p], c_char_p,
	"""Returns the path where a file part was saved.

	Args:
		multi_part: The MultiPart.

	Returns:
		The path, as bytes.
	"""
)

http_multi_part_get_saved_filename_len = lib_function (
	"http_multi_part_get_saved_filename_len", [c_void_p], c_int,
	"""Returns the length of the path where a file part was saved.

	Args:
		multi_part: The MultiPart.

	Returns:
		The length.
	"""
)

http_multi_part_get_moved_file = lib_function (
	"http_multi_part_get_moved_file", [c_void_p], c_bool,
	"""Returns if the file of a part was moved with http_multi_part_move_file ().

	Args:
		multi_part: The MultiPart.

	Returns:
		True if it was moved.
	"""
)

http_multi_part_get_value = lib_function (
	"http_multi_part_get_value", [c_void_p], c_char_p,
	"""Returns the value of a value part.

	Args:
		multi_part: The MultiPart.

	Returns:
		The value, as bytes.
	"""
)

http_multi_part_get_value_len = lib_function (
	"http_multi_part_get_value_len", [c_void_p], c_int,
	"""Returns the length of the value of a value part.

	Args:
		multi_part: The MultiPart.

	Returns:
		The length.
	"""
)

http_multi_part_move_file = lib_function (
	"http_multi_part_move_file", [c_void_p, c_char_p], c_uint,
	"""Moves the saved file of a part, it is not deleted with the uploads of the request.

	Args:
		mpart: The MultiPart.
		destination_path: The new path, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_multi_part_headers_print = lib_function (
	"http_multi_part_headers_print", [c_void_p], None,
	"""Prints the headers of a part.

	Args:
		mpart: The MultiPart.
	"""
)

http_multi_part_print = lib_function (
	"http_multi_part_print", [c_void_p], None,
	"""Prints a part.

	Args:
		mpart: The MultiPart.
	"""
)

def http_multi_part_get_file (mpart: c_void_p) -> dict:
	values = dict ()

	if (http_multi_part_is_file (mpart)):
		original = http_multi_part_get_filename (mpart)
		values["original"] = original.decode ("utf-8")

		generated = http_multi_part_get_generated_filename (mpart)
		if (generated):
			values["generated"] = generated.decode ("utf-8")

		saved = http_multi_part_get_saved_filename (mpart)
		values["saved"] = saved.decode ("utf-8")

	return values
