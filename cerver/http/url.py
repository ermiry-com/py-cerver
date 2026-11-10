"""The percent-encoding of urls."""

from ctypes import c_void_p, c_char_p, c_size_t

from ..lib import lib_function, lib_take_c_string

__all__ = [
	"http_url_encode_c_string", "http_url_decode_c_string", "http_url_decode_path",
	"http_url_encode", "http_url_decode"
]

http_url_encode_c_string = lib_function (
	"http_url_encode", [c_char_p], c_void_p,
	"""Returns a url-encoded copy of a string in a new C string, use http_url_encode ().

	Args:
		str: The string, as bytes.

	Returns:
		The address of the copy that the caller frees, None on error.
	"""
)

http_url_decode_c_string = lib_function (
	"http_url_decode", [c_char_p], c_void_p,
	"""Returns a url-decoded copy of a string in a new C string, use http_url_decode ().

	Args:
		str: The string, as bytes.

	Returns:
		The address of the copy that the caller frees, None on error.
	"""
)

http_url_decode_path = lib_function (
	"http_url_decode_path", [c_void_p, c_char_p, c_size_t], c_size_t,
	"""Decodes the percent escapes of a path into a buffer, a '+' stays a '+'.

	Args:
		destination: A writable buffer of at least length + 1 bytes.
		source: The path, as bytes.
		length: The length of the path.

	Returns:
		The length of the decoded path.
	"""
)

def http_url_encode (value: bytes) -> bytes | None:
	"""Returns a url-encoded copy of a value.

	Args:
		value: The bytes to encode.

	Returns:
		The encoded bytes, None on error.
	"""
	return lib_take_c_string (http_url_encode_c_string (value))

def http_url_decode (value: bytes) -> bytes | None:
	"""Returns a url-decoded copy of a value.

	Args:
		value: The bytes to decode.

	Returns:
		The decoded bytes, None on error.
	"""
	return lib_take_c_string (http_url_decode_c_string (value))
