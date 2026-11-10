"""The headers of HTTP that cerver knows by their type."""

from ctypes import POINTER, c_int, c_char_p, c_bool, c_size_t, c_void_p
from typing import TypeAlias

from ..lib import lib_function

HttpHeaderType: TypeAlias = c_int # type: ignore

# Authentication
HTTP_HEADER_AUTHENTICATE = 0
HTTP_HEADER_AUTHORIZATION = 1
HTTP_HEADER_PROXY_AUTHENTICATE = 2
HTTP_HEADER_PROXY_AUTHORIZATION = 3

# Caching
HTTP_HEADER_AGE = 4
HTTP_HEADER_CACHE_CONTROL = 5
HTTP_HEADER_CLEAR_SITE_DATA = 6
HTTP_HEADER_EXPIRES = 7
HTTP_HEADER_WARNING = 8

# Connection management
HTTP_HEADER_CONNECTION = 9
HTTP_HEADER_KEEP_ALIVE = 10

# Content negotiation
HTTP_HEADER_ACCEPT = 11
HTTP_HEADER_ACCEPT_CHARSET = 12
HTTP_HEADER_ACCEPT_ENCODING = 13
HTTP_HEADER_ACCEPT_LANGUAGE = 14

# Controls
HTTP_HEADER_EXPECT = 15

# Cookies
HTTP_HEADER_COOKIE = 16
HTTP_HEADER_SET_COOKIE = 17

# CORS
HTTP_HEADER_ACCESS_CONTROL_ALLOW_ORIGIN = 18
HTTP_HEADER_ACCESS_CONTROL_ALLOW_CREDENTIALS = 19
HTTP_HEADER_ACCESS_CONTROL_ALLOW_HEADERS = 20
HTTP_HEADER_ACCESS_CONTROL_ALLOW_METHODS = 21
HTTP_HEADER_ACCESS_CONTROL_EXPOSE_HEADER = 22
HTTP_HEADER_ACCESS_CONTROL_MAX_AGE = 23
HTTP_HEADER_ACCESS_CONTROL_REQUEST_HEADERS = 24
HTTP_HEADER_ACCESS_CONTROL_REQUEST_METHOD = 25
HTTP_HEADER_ORIGIN = 26
HTTP_HEADER_TIMING_ALLOW_ORIGIN = 27

# Downloads
HTTP_HEADER_CONTENT_DISPOSITION = 28

# Message body information
HTTP_HEADER_CONTENT_LENGTH = 29
HTTP_HEADER_CONTENT_TYPE = 30
HTTP_HEADER_CONTENT_ENCODING = 31
HTTP_HEADER_CONTENT_LANGUAGE = 32
HTTP_HEADER_CONTENT_LOCATION = 33

# Proxies
HTTP_HEADER_FORWARDED = 34
HTTP_HEADER_VIA = 35

# Redirects
HTTP_HEADER_LOCATION = 36

# Request context
HTTP_HEADER_FROM = 37
HTTP_HEADER_HOST = 38
HTTP_HEADER_REFERER = 39
HTTP_HEADER_REFERRER_POLICY = 40
HTTP_HEADER_USER_AGENT = 41

# Response context
HTTP_HEADER_ALLOW = 42
HTTP_HEADER_SERVER = 43

# Range requests
HTTP_HEADER_ACCEPT_RANGES = 44
HTTP_HEADER_RANGE = 45
HTTP_HEADER_IF_RANGE = 46
HTTP_HEADER_CONTENT_RANGE = 47

# WebSockets
HTTP_HEADER_SEC_WEBSOCKET_KEY = 48
HTTP_HEADER_SEC_WEBSOCKET_EXTENSIONS = 49
HTTP_HEADER_SEC_WEBSOCKET_ACCEPT = 50
HTTP_HEADER_SEC_WEBSOCKET_PROTOCOL = 51
HTTP_HEADER_SEC_WEBSOCKET_VERSION = 52

# Other
HTTP_HEADER_DATE = 53
HTTP_HEADER_UPGRADE = 54

# Transfer coding
HTTP_HEADER_TRANSFER_ENCODING = 55

# Conditionals
HTTP_HEADER_IF_NONE_MATCH = 56
HTTP_HEADER_IF_MODIFIED_SINCE = 57
HTTP_HEADER_ETAG = 58
HTTP_HEADER_LAST_MODIFIED = 59

# Tracing
HTTP_HEADER_REQUEST_ID = 60
HTTP_HEADER_FORWARDED_FOR = 61
HTTP_HEADER_REAL_IP = 62

HTTP_HEADER_UNDEFINED = 63

http_header_string = lib_function (
	"http_header_string", [HttpHeaderType], c_char_p,
	"""Returns the name of a header.

	Args:
		header: An HTTP_HEADER_* value.

	Returns:
		The name, as bytes, like b"Content-Type".
	"""
)

http_header_description = lib_function (
	"http_header_description", [HttpHeaderType], c_char_p,
	"""Returns the description of a header.

	Args:
		header: An HTTP_HEADER_* value.

	Returns:
		The description, as bytes.
	"""
)

http_header_type_by_string = lib_function (
	"http_header_type_by_string", [c_char_p], HttpHeaderType,
	"""Returns the type of a header by its name.

	Args:
		header_type_string: The name, as bytes.

	Returns:
		An HTTP_HEADER_* value, HTTP_HEADER_UNDEFINED if it is unknown.
	"""
)

http_header_print = lib_function (
	"http_header_print", [c_void_p], None,
	"""Prints a header of a request.

	Args:
		header: The HttpHeader.
	"""
)

http_headers_buffer_find = lib_function (
	"http_headers_buffer_find",
	[c_char_p, c_size_t, c_char_p, c_size_t, POINTER (c_void_p), POINTER (c_size_t)],
	c_bool,
	"""Finds a header by its name in a buffer of headers, without a copy.

	Args:
		buffer: The headers, as bytes.
		length: Their length.
		name: The name of the header, as bytes.
		name_length: Its length.
		value: A pointer to a c_void_p that gets the address of the value.
		value_length: A pointer to a c_size_t that gets its length.

	Returns:
		True if it was found.
	"""
)

__all__ = ["HttpHeaderType"] + [name for name in dir () if name.startswith (("HTTP_HEADER_", "http_header"))]
