"""The gzip compression of the responses."""

from ctypes import c_bool, c_char_p, c_int, c_size_t, c_void_p

from ..lib import lib_function

__all__ = [
	"HTTP_COMPRESSION_DEFAULT_MIN_SIZE", "HTTP_COMPRESSION_DEFAULT_LEVEL",
	"HTTP_COMPRESSION_MIN_LEVEL", "HTTP_COMPRESSION_MAX_LEVEL", "HTTP_COMPRESSION_ENCODING",
	"http_compression_available", "http_compression_accepts_gzip", "http_compression_is_compressible",
	"http_cerver_set_compression_min_size", "http_cerver_set_compression_level"
]

# the smallest body that is compressed
HTTP_COMPRESSION_DEFAULT_MIN_SIZE = 1 << 10

# the zlib level, from 1 (fastest) to 9 (smallest)
HTTP_COMPRESSION_DEFAULT_LEVEL = 6
HTTP_COMPRESSION_MIN_LEVEL = 1
HTTP_COMPRESSION_MAX_LEVEL = 9

# the only content coding that cerver uses
HTTP_COMPRESSION_ENCODING = "gzip"

http_compression_available = lib_function (
	"http_compression_available", [], c_bool,
	"""Returns if libcerver was compiled with zlib (ZLIB=1).

	Without it, the compression settings are accepted but nothing is compressed.

	Returns:
		True if it can compress.
	"""
)

http_compression_accepts_gzip = lib_function (
	"http_compression_accepts_gzip", [c_char_p, c_size_t], c_bool,
	"""Returns if an Accept-Encoding value accepts gzip, by name or with "*", with a quality bigger than 0.

	Args:
		accept_encoding: The value, as bytes.
		length: Its length.

	Returns:
		True if it accepts gzip.
	"""
)

http_compression_is_compressible = lib_function (
	"http_compression_is_compressible", [c_char_p, c_size_t], c_bool,
	"""Returns if a body of a content type is worth compressing: text, JSON, JavaScript, XML and SVG.

	Args:
		content_type: The value of the Content-Type, as bytes.
		length: Its length.

	Returns:
		True if it is compressible.
	"""
)

http_cerver_set_compression_min_size = lib_function (
	"http_cerver_set_compression_min_size", [c_void_p, c_size_t], None,
	"""Sets the smallest body that the endpoints with compression compress.

	Args:
		http_cerver: The HttpCerver.
		min_size: The size in bytes, HTTP_COMPRESSION_DEFAULT_MIN_SIZE by default.
	"""
)

http_cerver_set_compression_level = lib_function (
	"http_cerver_set_compression_level", [c_void_p, c_int], None,
	"""Sets the zlib level of the compression.

	Args:
		http_cerver: The HttpCerver.
		level: HTTP_COMPRESSION_MIN_LEVEL to HTTP_COMPRESSION_MAX_LEVEL.
	"""
)
