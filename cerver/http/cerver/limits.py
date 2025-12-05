"""The limits and the timeouts of the requests of an HTTP cerver."""

from ctypes import c_void_p, c_size_t, c_uint

from ...lib import lib_function

__all__ = [
	"HTTP_CERVER_DEFAULT_MAX_BODY_SIZE", "HTTP_CERVER_DEFAULT_MAX_URL_SIZE",
	"HTTP_CERVER_DEFAULT_MAX_HEADER_SIZE", "HTTP_CERVER_DEFAULT_MAX_HEADERS",
	"HTTP_CERVER_DEFAULT_MAX_MULTIPART_PARTS", "HTTP_CERVER_DEFAULT_MAX_FILE_SIZE",
	"HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT", "HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT",
	"http_cerver_set_max_body_size", "http_cerver_set_max_url_size",
	"http_cerver_set_max_header_size", "http_cerver_set_max_headers",
	"http_cerver_set_max_multipart_parts", "http_cerver_set_max_file_size",
	"http_cerver_set_headers_timeout", "http_cerver_set_request_timeout"
]

# a request that exceeds a limit is answered with 413, 414 or 431, 0 disables it
HTTP_CERVER_DEFAULT_MAX_BODY_SIZE = 1 << 29
HTTP_CERVER_DEFAULT_MAX_URL_SIZE = 1 << 13
HTTP_CERVER_DEFAULT_MAX_HEADER_SIZE = 1 << 16
HTTP_CERVER_DEFAULT_MAX_HEADERS = 1 << 7
HTTP_CERVER_DEFAULT_MAX_MULTIPART_PARTS = 1 << 10
HTTP_CERVER_DEFAULT_MAX_FILE_SIZE = 1 << 29

# in secs, a slower request is answered with 408, 0 disables it
HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT = 1 << 4
HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT = 0

http_cerver_set_max_body_size = lib_function (
	"http_cerver_set_max_body_size", [c_void_p, c_size_t], None,
	"""Sets the biggest body of a request (413 after it).

	Args:
		http_cerver: The HttpCerver.
		max_body_size: The size in bytes, 0 disables the limit.
	"""
)

http_cerver_set_max_url_size = lib_function (
	"http_cerver_set_max_url_size", [c_void_p, c_size_t], None,
	"""Sets the longest url of a request (414 after it).

	Args:
		http_cerver: The HttpCerver.
		max_url_size: The size in bytes, 0 disables the limit.
	"""
)

http_cerver_set_max_header_size = lib_function (
	"http_cerver_set_max_header_size", [c_void_p, c_size_t], None,
	"""Sets the biggest headers of a request (431 after it).

	Args:
		http_cerver: The HttpCerver.
		max_header_size: The size in bytes, 0 disables the limit.
	"""
)

http_cerver_set_max_headers = lib_function (
	"http_cerver_set_max_headers", [c_void_p, c_uint], None,
	"""Sets the most headers of a request (431 after them).

	Args:
		http_cerver: The HttpCerver.
		max_headers: The number of headers, 0 disables the limit.
	"""
)

http_cerver_set_max_multipart_parts = lib_function (
	"http_cerver_set_max_multipart_parts", [c_void_p, c_uint], None,
	"""Sets the most parts of a multipart request (413 after them).

	Args:
		http_cerver: The HttpCerver.
		max_multipart_parts: The number of parts, 0 disables the limit.
	"""
)

http_cerver_set_max_file_size = lib_function (
	"http_cerver_set_max_file_size", [c_void_p, c_size_t], None,
	"""Sets the biggest uploaded file (413 after it).

	Args:
		http_cerver: The HttpCerver.
		max_file_size: The size in bytes, 0 disables the limit.
	"""
)

http_cerver_set_headers_timeout = lib_function (
	"http_cerver_set_headers_timeout", [c_void_p, c_uint], None,
	"""Sets the seconds to receive the headers of a request (408 after them).

	Args:
		http_cerver: The HttpCerver.
		headers_timeout: The seconds, 0 disables it.
	"""
)

http_cerver_set_request_timeout = lib_function (
	"http_cerver_set_request_timeout", [c_void_p, c_uint], None,
	"""Sets the seconds to receive a complete request (408 after them).

	Args:
		http_cerver: The HttpCerver.
		request_timeout: The seconds, 0 disables it.
	"""
)
