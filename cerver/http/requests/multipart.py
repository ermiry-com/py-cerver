"""The parts of a multipart/form-data request: its values and its uploaded files."""

from ctypes import c_void_p, c_char_p, c_int, c_uint8, c_bool

from ...lib import lib_function, lib_c_string

from ..multipart import http_multi_part_get_file

__all__ = [
	"http_request_get_current_mpart", "http_request_get_n_files", "http_request_get_n_values",
	"http_request_get_dirname_len", "http_request_get_dirname",
	"http_request_set_dirname_variadic", "http_request_set_dirname",
	"http_request_multi_parts_get", "http_request_multi_parts_get_value",
	"http_request_multi_parts_get_filename", "http_request_multi_parts_get_saved_filename",
	"http_request_multi_parts_iter_start", "http_request_multi_parts_iter_get_next",
	"http_request_multi_parts_get_all_filenames", "http_request_multi_parts_get_all_saved_filenames",
	"http_request_multi_parts_all_filenames_delete",
	"http_request_multi_part_keep_files", "http_request_multi_part_discard_files",
	"http_request_multi_parts_print", "http_request_multi_parts_files_print",
	"http_request_multi_parts_get_file", "http_request_multi_parts"
]

# the format that sets a directory as it is
DIRNAME_FORMAT = b"%s"

http_request_get_current_mpart = lib_function (
	"http_request_get_current_mpart", [c_void_p], c_void_p,
	"""Returns the part that is being parsed, in an uploads filename or dirname generator.

	Args:
		http_request: The request.

	Returns:
		The MultiPart.
	"""
)

http_request_get_n_files = lib_function (
	"http_request_get_n_files", [c_void_p], c_uint8,
	"""Returns how many files the request uploaded.

	Args:
		http_request: The request.

	Returns:
		The number of files.
	"""
)

http_request_get_n_values = lib_function (
	"http_request_get_n_values", [c_void_p], c_uint8,
	"""Returns how many values (parts without a file) the request has.

	Args:
		http_request: The request.

	Returns:
		The number of values.
	"""
)

http_request_get_dirname_len = lib_function (
	"http_request_get_dirname_len", [c_void_p], c_int,
	"""Returns the length of the directory where the files of the request are saved.

	Args:
		http_request: The request.

	Returns:
		The length, 0 if it has none.
	"""
)

http_request_get_dirname = lib_function (
	"http_request_get_dirname", [c_void_p], c_char_p,
	"""Returns the directory where the files of the request are saved.

	Args:
		http_request: The request.

	Returns:
		The directory, as bytes.
	"""
)

http_request_set_dirname_variadic = lib_function (
	"http_request_set_dirname", None, None,
	"""Sets the directory of the files of the request with a printf format (variadic).

	It is called from an uploads dirname generator.

	Args:
		http_request: The request, as c_void_p.
		format: The format, as bytes, followed by its arguments.
	"""
)

def http_request_set_dirname (request: int, dirname: str | bytes) -> None:
	"""Sets the directory of the files of the request, from an uploads dirname generator.

	Args:
		request: The request.
		dirname: The directory, relative to the uploads path.
	"""
	http_request_set_dirname_variadic (
		c_void_p (request), c_char_p (DIRNAME_FORMAT), c_char_p (lib_c_string (dirname))
	)

http_request_multi_parts_get = lib_function (
	"http_request_multi_parts_get", [c_void_p, c_char_p], c_void_p,
	"""Returns the part with a name.

	Args:
		http_request: The request.
		key: The name of the part, as bytes.

	Returns:
		The MultiPart, None if there is none.
	"""
)

http_request_multi_parts_get_value = lib_function (
	"http_request_multi_parts_get_value", [c_void_p, c_char_p], c_char_p,
	"""Returns the value of the part with a name.

	Args:
		http_request: The request.
		key: The name of the part, as bytes.

	Returns:
		The value, as bytes, None if there is none.
	"""
)

http_request_multi_parts_get_filename = lib_function (
	"http_request_multi_parts_get_filename", [c_void_p, c_char_p], c_char_p,
	"""Returns the original filename of the file part with a name.

	Args:
		http_request: The request.
		key: The name of the part, as bytes.

	Returns:
		The filename, as bytes, None if there is none.
	"""
)

http_request_multi_parts_get_saved_filename = lib_function (
	"http_request_multi_parts_get_saved_filename", [c_void_p, c_char_p], c_char_p,
	"""Returns the path where the file part with a name was saved.

	Args:
		http_request: The request.
		key: The name of the part, as bytes.

	Returns:
		The path, as bytes, None if there is none.
	"""
)

http_request_multi_parts_iter_start = lib_function (
	"http_request_multi_parts_iter_start", [c_void_p], c_bool,
	"""Starts to iterate the parts of the request.

	Args:
		http_request: The request.

	Returns:
		True if the request has parts.
	"""
)

http_request_multi_parts_iter_get_next = lib_function (
	"http_request_multi_parts_iter_get_next", [c_void_p], c_void_p,
	"""Returns the next part of the iteration.

	Args:
		http_request: The request.

	Returns:
		The MultiPart, None after the last one.
	"""
)

http_request_multi_parts_get_all_filenames = lib_function (
	"http_request_multi_parts_get_all_filenames", [c_void_p], c_void_p,
	"""Returns a list with the original filenames of the request.

	Args:
		http_request: The request.

	Returns:
		The list, released with http_request_multi_parts_all_filenames_delete ().
	"""
)

http_request_multi_parts_get_all_saved_filenames = lib_function (
	"http_request_multi_parts_get_all_saved_filenames", [c_void_p], c_void_p,
	"""Returns a list with the saved filenames of the request.

	Args:
		http_request: The request.

	Returns:
		The list, released with http_request_multi_parts_all_filenames_delete ().
	"""
)

http_request_multi_parts_all_filenames_delete = lib_function (
	"http_request_multi_parts_all_filenames_delete", [c_void_p], None,
	"""Releases a list of filenames.

	Args:
		all_filenames: The list.
	"""
)

http_request_multi_part_keep_files = lib_function (
	"http_request_multi_part_keep_files", [c_void_p], None,
	"""Keeps the files of the request when the cerver deletes the uploads after each request.

	Args:
		http_request: The request.
	"""
)

http_request_multi_part_discard_files = lib_function (
	"http_request_multi_part_discard_files", [c_void_p], None,
	"""Deletes the saved files of the request.

	Args:
		http_request: The request.
	"""
)

http_request_multi_parts_print = lib_function (
	"http_request_multi_parts_print", [c_void_p], None,
	"""Prints the parts of the request.

	Args:
		http_request: The request.
	"""
)

http_request_multi_parts_files_print = lib_function (
	"http_request_multi_parts_files_print", [c_void_p], None,
	"""Prints the file parts of the request.

	Args:
		http_request: The request.
	"""
)

def http_request_multi_parts_get_file (request: int, value: str) -> dict | None:
	"""Returns the filenames of the file part with a name.

	Args:
		request: The request.
		value: The name of the part.

	Returns:
		A dict with "original", "saved" and "generated" (when there is one), empty for a
		part that is not a file, None if there is no part with that name.
	"""
	result = None

	mpart = http_request_multi_parts_get (request, lib_c_string (value))
	if (mpart):
		result = http_multi_part_get_file (mpart)

	return result

def http_request_multi_parts (request: int) -> list:
	"""Returns every part of the request.

	Args:
		request: The request.

	Returns:
		The MultiPart of each part, in order.
	"""
	parts = []

	if (http_request_multi_parts_iter_start (request)):
		mpart = http_request_multi_parts_iter_get_next (request)
		while (mpart):
			parts.append (mpart)
			mpart = http_request_multi_parts_iter_get_next (request)

	return parts
