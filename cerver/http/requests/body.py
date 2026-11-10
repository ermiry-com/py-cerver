"""The body of a request."""

import json

from ctypes import c_void_p, c_char_p

from ...lib import lib_function

from ...types.string import StringPointer, string_bytes

__all__ = [
	"http_request_get_body", "http_request_get_body_values", "http_request_body_get_value",
	"http_request_get_body_json"
]

http_request_get_body = lib_function (
	"http_request_get_body", [c_void_p], StringPointer,
	"""Returns the body of the request.

	Args:
		http_request: The request.

	Returns:
		A StringPointer, NULL when the request has no body.
	"""
)

http_request_get_body_values = lib_function (
	"http_request_get_body_values", [c_void_p], c_void_p,
	"""Returns the pairs of an x-www-form-urlencoded body.

	Args:
		http_request: The request.

	Returns:
		The pairs, None if the body is not a form.
	"""
)

http_request_body_get_value = lib_function (
	"http_request_body_get_value", [c_void_p, c_char_p], StringPointer,
	"""Returns the value of a key of an x-www-form-urlencoded body.

	Args:
		http_request: The request.
		key: The key, as bytes.

	Returns:
		A StringPointer, NULL if the body does not have the key.
	"""
)

def http_request_get_body_json (request: int) -> dict | None:
	"""Returns the JSON body of the request as a dict.

	Args:
		request: The request.

	Returns:
		The body, None when the request has no body, it is not JSON or it is not an object.
	"""
	result = None

	# a NULL pointer of ctypes is falsy, never None
	body = string_bytes (http_request_get_body (request))
	if (body):
		try:
			loaded = json.loads (body)
			if (isinstance (loaded, dict)):
				result = loaded

		except ValueError:
			pass

	return result
