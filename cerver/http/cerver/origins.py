"""The whitelist of the origins of the CORS responses of an HTTP cerver."""

from ctypes import c_void_p, c_char_p, c_uint8

from ...lib import lib_function

__all__ = [
	"http_cerver_add_origin_to_whitelist", "http_cerver_print_origins_whitelist"
]

http_cerver_add_origin_to_whitelist = lib_function (
	"http_cerver_add_origin_to_whitelist", [c_void_p, c_char_p], c_uint8,
	"""Adds an origin to the whitelist of the CORS responses, up to HTTP_ORIGINS_SIZE.

	Args:
		http_cerver: The HttpCerver.
		domain: The origin, as bytes, like b"https://app.example.com".

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_print_origins_whitelist = lib_function (
	"http_cerver_print_origins_whitelist", [c_void_p], None,
	"""Prints the whitelist of the origins.

	Args:
		http_cerver: The HttpCerver.
	"""
)
