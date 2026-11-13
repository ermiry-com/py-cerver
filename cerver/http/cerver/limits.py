"""The limits and the timeouts of the requests of an HTTP cerver."""

from ctypes import c_void_p, c_size_t, c_uint, c_bool

from ...lib import lib_function

__all__ = [
	"HTTP_CERVER_DEFAULT_MAX_BODY_SIZE", "HTTP_CERVER_DEFAULT_MAX_URL_SIZE",
	"HTTP_CERVER_DEFAULT_MAX_HEADER_SIZE", "HTTP_CERVER_DEFAULT_MAX_HEADERS",
	"HTTP_CERVER_DEFAULT_MAX_CUSTOM_HEADER_SIZE",
	"HTTP_CERVER_DEFAULT_MAX_MULTIPART_PARTS", "HTTP_CERVER_DEFAULT_MAX_FILE_SIZE",
	"HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT", "HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT",
	"HTTP_MILLISECONDS_PER_SECOND",
	"HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT_MILLISECONDS", "HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT_MILLISECONDS",
	"HTTP_CERVER_DEFAULT_IDLE_TIMEOUT", "HTTP_CERVER_DEFAULT_IDLE_TIMEOUT_MILLISECONDS",
	"HTTP_CERVER_DEFAULT_HALF_CLOSE_IS_GONE",
	"http_cerver_set_max_body_size", "http_cerver_set_max_url_size",
	"http_cerver_set_max_header_size", "http_cerver_set_max_headers",
	"http_cerver_set_max_custom_header_size",
	"http_cerver_set_max_multipart_parts", "http_cerver_set_max_file_size",
	"http_cerver_set_headers_timeout", "http_cerver_set_request_timeout",
	"http_cerver_set_headers_timeout_milliseconds", "http_cerver_set_request_timeout_milliseconds",
	"http_cerver_set_idle_timeout_milliseconds", "http_cerver_set_send_timeout_milliseconds",
	"http_cerver_set_half_close_is_gone"
]

# a request that exceeds a limit is answered with 413, 414 or 431, 0 disables it
HTTP_CERVER_DEFAULT_MAX_BODY_SIZE = 1 << 29
HTTP_CERVER_DEFAULT_MAX_URL_SIZE = 1 << 13
HTTP_CERVER_DEFAULT_MAX_HEADER_SIZE = 1 << 16
HTTP_CERVER_DEFAULT_MAX_HEADERS = 1 << 7
HTTP_CERVER_DEFAULT_MAX_CUSTOM_HEADER_SIZE = 1 << 13
HTTP_CERVER_DEFAULT_MAX_MULTIPART_PARTS = 1 << 10
HTTP_CERVER_DEFAULT_MAX_FILE_SIZE = 1 << 29

# in secs, a slower request is answered with 408, 0 disables it
HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT = 1 << 4
HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT = 300

HTTP_MILLISECONDS_PER_SECOND = 1000

HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT_MILLISECONDS = HTTP_CERVER_DEFAULT_HEADERS_TIMEOUT * HTTP_MILLISECONDS_PER_SECOND
HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT_MILLISECONDS = HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT * HTTP_MILLISECONDS_PER_SECOND

# in secs, a connection that receives nothing for longer ends (with 408 if its request had started)
HTTP_CERVER_DEFAULT_IDLE_TIMEOUT = 5
HTTP_CERVER_DEFAULT_IDLE_TIMEOUT_MILLISECONDS = HTTP_CERVER_DEFAULT_IDLE_TIMEOUT * HTTP_MILLISECONDS_PER_SECOND

# http_receive_is_client_gone () takes a client that closed its side as gone
HTTP_CERVER_DEFAULT_HALF_CLOSE_IS_GONE = True

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

http_cerver_set_max_custom_header_size = lib_function (
	"http_cerver_set_max_custom_header_size", [c_void_p, c_size_t], None,
	"""Sets the biggest value of a header that is not one of the known ones (431 after it).

	The values of a header that is repeated are joined, and the size of all the headers
	is still limited by ``http_cerver_set_max_header_size``.

	Args:
		http_cerver: The HttpCerver.
		max_custom_header_size: The size in bytes, 0 disables the limit.
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

http_cerver_set_headers_timeout_milliseconds = lib_function (
	"http_cerver_set_headers_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the milliseconds to receive the headers of a request (408 after them).

	Args:
		http_cerver: The HttpCerver.
		headers_timeout: The milliseconds, 0 disables it.
	"""
)

http_cerver_set_request_timeout_milliseconds = lib_function (
	"http_cerver_set_request_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the milliseconds to receive a complete request (408 after them).

	Args:
		http_cerver: The HttpCerver.
		request_timeout: The milliseconds, 0 disables it.
	"""
)

http_cerver_set_idle_timeout_milliseconds = lib_function (
	"http_cerver_set_idle_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the most milliseconds that a connection waits without receiving anything.

	A request that had started is answered with 408, an empty connection is only closed.

	Args:
		http_cerver: The HttpCerver.
		idle_timeout: The milliseconds, 0 keeps the default.
	"""
)

http_cerver_set_send_timeout_milliseconds = lib_function (
	"http_cerver_set_send_timeout_milliseconds", [c_void_p, c_uint], None,
	"""Sets the most milliseconds that all the sends of a response take together.

	The headers, the body and the files share the deadline, also in a blocking socket with a
	longer SO_SNDTIMEO, so a client that stops reading costs that time in total and not in
	each send; each piece of a stream has its own deadline.

	Args:
		http_cerver: The HttpCerver.
		send_timeout: The milliseconds, 0 (the default) uses the send timeout of the cerver.
	"""
)

http_cerver_set_half_close_is_gone = lib_function (
	"http_cerver_set_half_close_is_gone", [c_void_p, c_bool], None,
	"""Sets if http_receive_is_client_gone () takes a client that closed its side as gone.

	A client that uses a half-close to end its request still waits for the response.

	Args:
		http_cerver: The HttpCerver.
		half_close_is_gone: True by default.
	"""
)
