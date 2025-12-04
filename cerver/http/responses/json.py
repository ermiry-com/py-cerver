"""The JSON responses: the builders of cerver and the ones of Python values."""

import json

from ctypes import c_void_p, c_char_p, c_size_t, c_uint8, c_int, c_long, c_double, c_bool

from ...lib import lib_function

from ..status import HttpStatus

from .core import http_response_send, http_response_delete

__all__ = [
	"http_response_render_json", "http_response_create_json", "http_response_create_json_key_value",
	"http_response_json_int_value", "http_response_json_int_value_send",
	"http_response_json_large_int_value", "http_response_json_large_int_value_send",
	"http_response_json_real_value", "http_response_json_real_value_send",
	"http_response_json_bool_value", "http_response_json_bool_value_send",
	"http_response_json_msg", "http_response_json_msg_send",
	"http_response_json_error", "http_response_json_error_send",
	"http_response_json_key_value", "http_response_json_key_value_send",
	"http_response_json_custom", "http_response_json_custom_send",
	"http_response_json_custom_reference", "http_response_json_custom_reference_send",
	"http_response_json_send", "http_response_json_create", "http_response_prebuilt_send",
	"HttpPrebuiltResponses"
]

TEXT_ENCODING = "utf-8"

http_response_render_json = lib_function (
	"http_response_render_json", [c_void_p, HttpStatus, c_char_p, c_size_t], c_uint8,
	"""Sends a JSON body with the application/json content type.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		json: The JSON, as bytes.
		json_len: Its length in bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_create_json = lib_function (
	"http_response_create_json", [HttpStatus, c_char_p, c_size_t], c_void_p,
	"""Creates a response with a reference to a JSON body, it is not copied.

	Args:
		status: An HTTP_STATUS_* value.
		json: The JSON, as bytes kept alive by the caller while the response is used.
		json_len: Its length in bytes.

	Returns:
		The HttpResponse, released with http_response_delete ().
	"""
)

http_response_create_json_key_value = lib_function (
	"http_response_create_json_key_value", [HttpStatus, c_char_p, c_char_p], c_void_p,
	"""Creates a response with a body {"key": "value"}.

	Args:
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The value, as bytes.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_int_value = lib_function (
	"http_response_json_int_value", [HttpStatus, c_char_p, c_int], c_void_p,
	"""Creates a response with a body {"key": int}.

	Args:
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The integer.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_int_value_send = lib_function (
	"http_response_json_int_value_send", [c_void_p, HttpStatus, c_char_p, c_int], c_uint8,
	"""Sends a response with a body {"key": int}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The integer.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_large_int_value = lib_function (
	"http_response_json_large_int_value", [HttpStatus, c_char_p, c_long], c_void_p,
	"""Creates a response with a body {"key": long}.

	Args:
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The integer.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_large_int_value_send = lib_function (
	"http_response_json_large_int_value_send", [c_void_p, HttpStatus, c_char_p, c_long], c_uint8,
	"""Sends a response with a body {"key": long}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The integer.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_real_value = lib_function (
	"http_response_json_real_value", [HttpStatus, c_char_p, c_double], c_void_p,
	"""Creates a response with a body {"key": double}.

	Args:
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The number.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_real_value_send = lib_function (
	"http_response_json_real_value_send", [c_void_p, HttpStatus, c_char_p, c_double], c_uint8,
	"""Sends a response with a body {"key": double}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The number.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_bool_value = lib_function (
	"http_response_json_bool_value", [HttpStatus, c_char_p, c_bool], c_void_p,
	"""Creates a response with a body {"key": bool}.

	Args:
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The bool.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_bool_value_send = lib_function (
	"http_response_json_bool_value_send", [c_void_p, HttpStatus, c_char_p, c_bool], c_uint8,
	"""Sends a response with a body {"key": bool}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The bool.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_msg = lib_function (
	"http_response_json_msg", [HttpStatus, c_char_p], c_void_p,
	"""Creates a response with a body {"msg": "message"}.

	Args:
		status: An HTTP_STATUS_* value.
		msg: The message, as bytes.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_msg_send = lib_function (
	"http_response_json_msg_send", [c_void_p, HttpStatus, c_char_p], c_uint8,
	"""Sends a response with a body {"msg": "message"}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		msg: The message, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_error = lib_function (
	"http_response_json_error", [HttpStatus, c_char_p], c_void_p,
	"""Creates a response with a body {"error": "message"}.

	Args:
		status: An HTTP_STATUS_* value.
		error_msg: The message, as bytes.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_error_send = lib_function (
	"http_response_json_error_send", [c_void_p, HttpStatus, c_char_p], c_uint8,
	"""Sends a response with a body {"error": "message"}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		error_msg: The message, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_key_value = lib_function (
	"http_response_json_key_value", [HttpStatus, c_char_p, c_char_p], c_void_p,
	"""Creates a response with a body {"key": "value"}.

	Args:
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The value, as bytes.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_key_value_send = lib_function (
	"http_response_json_key_value_send", [c_void_p, HttpStatus, c_char_p, c_char_p], c_uint8,
	"""Sends a response with a body {"key": "value"}.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		key: The key, as bytes.
		value: The value, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_custom = lib_function (
	"http_response_json_custom", [HttpStatus, c_char_p], c_void_p,
	"""Creates a response with a copy of a JSON body.

	Args:
		status: An HTTP_STATUS_* value.
		json: The JSON, as NUL terminated bytes.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_custom_send = lib_function (
	"http_response_json_custom_send", [c_void_p, HttpStatus, c_char_p], c_uint8,
	"""Sends a response with a JSON body.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		json: The JSON, as NUL terminated bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_json_custom_reference = lib_function (
	"http_response_json_custom_reference", [HttpStatus, c_char_p, c_size_t], c_void_p,
	"""Creates a response with a reference to a JSON body, it is not copied.

	Args:
		status: An HTTP_STATUS_* value.
		json: The JSON, as bytes kept alive by the caller.
		json_len: Its length in bytes.

	Returns:
		The HttpResponse ready to be sent, released with http_response_delete ().
	"""
)

http_response_json_custom_reference_send = lib_function (
	"http_response_json_custom_reference_send", [c_void_p, HttpStatus, c_char_p, c_size_t], c_uint8,
	"""Sends a response with a JSON body without copying it.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		json: The JSON, as bytes.
		json_len: Its length in bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

def http_response_json_bytes (value) -> bytes:
	"""Returns a Python value as the bytes of its JSON."""
	return json.dumps (value).encode (TEXT_ENCODING)

def http_response_json_send (http_receive: int, status: int, value) -> int:
	"""Sends a Python value (a dict, a list, a str, a number, a bool or None) as JSON.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		value: The value, serialized with json.dumps ().

	Returns:
		0 on success, 1 on error.
	"""
	body = http_response_json_bytes (value)
	return http_response_json_custom_reference_send (http_receive, status, body, len (body))

def http_response_json_create (status: int, value) -> int | None:
	"""Creates a compiled response with a copy of a Python value as its JSON body.

	It can be created once and sent many times with http_response_prebuilt_send (), like the
	errors that every handler of a service answers.

	Args:
		status: An HTTP_STATUS_* value.
		value: The value, serialized with json.dumps ().

	Returns:
		The HttpResponse, released with http_response_delete (), None on error.
	"""
	return http_response_json_custom (status, http_response_json_bytes (value))

def http_response_prebuilt_send (response: int, http_receive: int) -> int:
	"""Sends a response that was created and compiled before, it is not released.

	Args:
		response: The HttpResponse, like one of http_response_json_create ().
		http_receive: The HttpReceive of the request.

	Returns:
		0 on success, 1 on error.
	"""
	return http_response_send (response, http_receive)

class HttpPrebuiltResponses:
	"""Responses that are created once and sent by many handlers, like the errors of a service.

	Example:
		errors = HttpPrebuiltResponses ()
		errors.add ("not_found", HTTP_STATUS_NOT_FOUND, {"error": "Not found!"})
		...
		errors.send ("not_found", http_receive)
		...
		errors.delete ()
	"""

	def __init__ (self):
		"""Creates an empty table of responses."""
		self.responses = {}

	def add (self, name: str, status: int, value) -> None:
		"""Creates a response with a JSON body and keeps it by its name.

		Args:
			name: The name of the response.
			status: An HTTP_STATUS_* value.
			value: The JSON body.

		Raises:
			RuntimeError: If cerver could not create the response.
		"""
		response = http_response_json_create (status, value)
		if (not response):
			raise RuntimeError (f"Failed to create the response {name}")

		previous = self.responses.pop (name, None)
		if (previous):
			http_response_delete (previous)

		self.responses[name] = response

	def send (self, name: str, http_receive: int) -> int:
		"""Sends a response by its name.

		Args:
			name: The name of the response.
			http_receive: The HttpReceive of the request.

		Returns:
			0 on success, 1 on error.

		Raises:
			KeyError: If there is no response with that name.
		"""
		return http_response_prebuilt_send (self.responses[name], http_receive)

	def delete (self) -> None:
		"""Releases every response, after the cerver stopped."""
		for response in self.responses.values ():
			http_response_delete (response)

		self.responses.clear ()
