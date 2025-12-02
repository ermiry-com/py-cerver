"""The entity tags of the responses and the conditional requests (304 Not Modified)."""

from ctypes import create_string_buffer
from ctypes import c_bool, c_char_p, c_long, c_size_t, c_void_p

from ..lib import lib_function, lib_text

__all__ = [
	"HTTP_ETAG_SIZE",
	"http_etag_from_data", "http_etag_from_file", "http_etag_none_match",
	"http_conditional_not_modified",
	"http_etag"
]

# the longest entity tag that cerver generates and its NUL
HTTP_ETAG_SIZE = 48

http_etag_from_data = lib_function (
	"http_etag_from_data", [c_void_p, c_size_t, c_bool, c_void_p], c_size_t,
	"""Writes the strong entity tag of a body, the FNV-1a of its bytes.

	Args:
		data: The body.
		length: Its length.
		compressed: True to add the suffix of a body that is sent compressed.
		etag: A writable buffer of at least HTTP_ETAG_SIZE bytes.

	Returns:
		The length of the entity tag, 0 on error.
	"""
)

http_etag_from_file = lib_function (
	"http_etag_from_file", [c_void_p, c_void_p], c_size_t,
	"""Writes the weak entity tag of a file, from its size and its modification time.

	Args:
		file_status: The struct stat of the file.
		etag: A writable buffer of at least HTTP_ETAG_SIZE bytes.

	Returns:
		The length of the entity tag, 0 on error.
	"""
)

http_etag_none_match = lib_function (
	"http_etag_none_match", [c_char_p, c_size_t, c_char_p, c_size_t], c_bool,
	"""Returns if an If-None-Match value matches an entity tag with the weak comparison.

	Args:
		if_none_match: The value of the header, "*" or a list of entity tags, as bytes.
		if_none_match_length: Its length.
		etag: The entity tag, as bytes.
		etag_length: Its length.

	Returns:
		True if it matches.
	"""
)

http_conditional_not_modified = lib_function (
	"http_conditional_not_modified", [c_void_p, c_char_p, c_size_t, c_long], c_bool,
	"""Returns if a GET or a HEAD request can be answered with 304 Not Modified.

	Args:
		request: The request.
		etag: The entity tag of the response, as bytes.
		etag_length: Its length.
		last_modified: The last modification in seconds since the epoch.

	Returns:
		True when it can be answered with 304.
	"""
)

def http_etag (data: bytes, compressed: bool = False) -> str | None:
	"""Returns the strong entity tag that cerver generates for a body.

	Args:
		data: The body.
		compressed: True for a body that is sent compressed.

	Returns:
		The entity tag, with its quotes, None on error.
	"""
	result = None

	buffer = create_string_buffer (HTTP_ETAG_SIZE)
	if (http_etag_from_data (data, len (data), compressed, buffer)):
		result = lib_text (buffer.value)

	return result
