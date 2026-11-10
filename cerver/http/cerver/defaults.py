"""The headers that an HTTP cerver adds to every response: Date and X-Request-Id."""

from ctypes import c_void_p, c_bool

from ...lib import lib_function

__all__ = [
	"HTTP_CERVER_DEFAULT_DATE_HEADER", "HTTP_CERVER_DEFAULT_REQUEST_ID",
	"http_cerver_set_date_header", "http_cerver_set_request_id"
]

HTTP_CERVER_DEFAULT_DATE_HEADER = True
HTTP_CERVER_DEFAULT_REQUEST_ID = False

http_cerver_set_date_header = lib_function (
	"http_cerver_set_date_header", [c_void_p, c_bool], None,
	"""Sets if every response has a Date header.

	Args:
		http_cerver: The HttpCerver.
		date_header: True (the default) to add it.
	"""
)

http_cerver_set_request_id = lib_function (
	"http_cerver_set_request_id", [c_void_p, c_bool], None,
	"""Identifies every request with its valid X-Request-Id or a new UUID v4, echoed in the response.

	Args:
		http_cerver: The HttpCerver.
		request_id: True to identify them, False by default.
	"""
)
