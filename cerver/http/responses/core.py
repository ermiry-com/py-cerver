"""An HTTP response: its status, its headers, its body, and how it is compiled and sent."""

import json

from ctypes import POINTER, byref, c_void_p, c_char_p, c_size_t, c_uint, c_uint8, string_at

from ...lib import lib_function, lib_c_string

from ..content import ContentType, HTTP_CONTENT_TYPE_HTML, HTTP_CONTENT_TYPE_JSON
from ..headers import HttpHeaderType
from ..status import HttpStatus
from ..utils import BytesRangePointer

__all__ = [
	"http_response_delete", "http_response_get", "http_response_return",
	"http_response_set_status", "http_response_set_header",
	"http_response_header_set", "http_response_header_add", "http_response_header_remove",
	"http_response_header_count", "http_response_header_get", "http_response_header_value",
	"http_response_header_set_by_name", "http_response_header_add_by_name",
	"http_response_header_remove_by_name", "http_response_header_count_by_name",
	"http_response_header_get_by_name", "http_response_header_value_by_name",
	"http_response_add_header",
	"http_response_add_custom_header_variadic", "http_response_add_custom_header_value",
	"http_response_add_content_type_header", "http_response_add_content_length_header",
	"http_response_add_json_headers", "http_response_add_content_range_header",
	"http_response_add_video_headers",
	"http_response_add_cors_header", "http_response_add_cors_header_from_origin",
	"http_response_add_whitelist_cors_header", "http_response_add_whitelist_cors_header_from_origin",
	"http_response_add_whitelist_cors_header_from_request",
	"http_response_add_cors_allow_credentials_header", "http_response_add_cors_allow_methods_header",
	"http_response_set_data", "http_response_set_data_ref", "http_response_create",
	"http_response_compile_header", "http_response_compile", "http_response_print",
	"http_response_send", "http_response_send_split", "http_response_create_and_send",
	"http_send_response"
]

# the format that adds a header value as it is
HEADER_VALUE_FORMAT = b"%s"

TEXT_ENCODING = "utf-8"

http_response_delete = lib_function (
	"http_response_delete", [c_void_p], None,
	"""Releases a response with all of its data.

	Args:
		response: The HttpResponse, it must not be used after this call.
	"""
)

http_response_get = lib_function (
	"http_response_get", [], c_void_p,
	"""Takes an empty response from the pool of responses.

	Returns:
		The HttpResponse, given back with http_response_return ().
	"""
)

http_response_return = lib_function (
	"http_response_return", [c_void_p], None,
	"""Gives a response back to the pool of responses.

	Args:
		response: The HttpResponse of http_response_get ().
	"""
)

http_response_set_status = lib_function (
	"http_response_set_status", [c_void_p, HttpStatus], None,
	"""Sets the status of a response.

	Args:
		response: The HttpResponse.
		status: An HTTP_STATUS_* value.
	"""
)

http_response_set_header = lib_function (
	"http_response_set_header", [c_void_p, c_void_p, c_size_t], None,
	"""Sets the header of a response as the bytes that are sent, replacing the previous one.

	The headers that were added to the response are not sent; it is released with the response.

	Args:
		response: The HttpResponse.
		header: The bytes of the header.
		header_len: Their length.
	"""
)

http_response_header_set = lib_function (
	"http_response_header_set", [c_void_p, HttpHeaderType, c_char_p], c_uint8,
	"""Sets a header of a response, it replaces the ones that it has with the same type.

	Args:
		response: The HttpResponse.
		type: An HTTP_HEADER_* value.
		value: The value, as bytes, without a CR, a LF or a NUL.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_header_add = lib_function (
	"http_response_header_add", [c_void_p, HttpHeaderType, c_char_p], c_uint8,
	"""Adds a header to a response after the ones that it has, so a header can be repeated, like Set-Cookie.

	The headers are sent in the order they were added.

	Args:
		response: The HttpResponse.
		type: An HTTP_HEADER_* value.
		value: The value, as bytes, without a CR, a LF or a NUL.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_header_remove = lib_function (
	"http_response_header_remove", [c_void_p, HttpHeaderType], c_uint,
	"""Removes the headers of a response with the type.

	Args:
		response: The HttpResponse.
		type: An HTTP_HEADER_* value.

	Returns:
		The number of headers that were removed.
	"""
)

http_response_header_count = lib_function (
	"http_response_header_count", [c_void_p, HttpHeaderType], c_uint,
	"""Returns the number of headers of a response with the type.

	Args:
		response: The HttpResponse.
		type: An HTTP_HEADER_* value.
	"""
)

http_response_header_get = lib_function (
	"http_response_header_get", [c_void_p, HttpHeaderType, c_uint, POINTER (c_size_t)], c_void_p,
	"""Gets the value of a header of a response, that does not end with a NUL.

	http_response_header_value () returns it as bytes.

	Args:
		response: The HttpResponse.
		type: An HTTP_HEADER_* value.
		position: The position between the headers with the type, 0 is the first one that was added.
		value_length: Where the length of the value is written.

	Returns:
		The address of the value, None if the response does not have the header.
	"""
)

def http_response_header_value (response: int, header_type: int, position: int = 0) -> bytes | None:
	"""Returns the value of a header of a response.

	Args:
		response: The HttpResponse.
		header_type: An HTTP_HEADER_* value.
		position: The position between the headers with the type, 0 is the first one that was added.

	Returns:
		The value, None if the response does not have the header.
	"""
	length = c_size_t (0)
	value = http_response_header_get (response, header_type, position, byref (length))

	return string_at (value, length.value) if (value) else None

http_response_header_set_by_name = lib_function (
	"http_response_header_set_by_name", [c_void_p, c_char_p, c_char_p], c_uint8,
	"""Sets a header of a response by its name, it replaces the ones that it has with the same name.

	The name can be the one of any header, it is compared without case.

	Args:
		response: The HttpResponse.
		name: The name, as bytes, like b"X-Trace".
		value: The value, as bytes, without a CR, a LF or a NUL.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_header_add_by_name = lib_function (
	"http_response_header_add_by_name", [c_void_p, c_char_p, c_char_p], c_uint8,
	"""Adds a header to a response by its name, after the ones that it has.

	Args:
		response: The HttpResponse.
		name: The name, as bytes.
		value: The value, as bytes, without a CR, a LF or a NUL.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_header_remove_by_name = lib_function (
	"http_response_header_remove_by_name", [c_void_p, c_char_p], c_uint,
	"""Removes the headers of a response with the name.

	Args:
		response: The HttpResponse.
		name: The name, as bytes.

	Returns:
		The number of headers that were removed.
	"""
)

http_response_header_count_by_name = lib_function (
	"http_response_header_count_by_name", [c_void_p, c_char_p], c_uint,
	"""Returns the number of headers of a response with the name.

	Args:
		response: The HttpResponse.
		name: The name, as bytes.
	"""
)

http_response_header_get_by_name = lib_function (
	"http_response_header_get_by_name", [c_void_p, c_char_p, c_uint, POINTER (c_size_t)], c_void_p,
	"""Gets the value of a header of a response by its name, that does not end with a NUL.

	http_response_header_value_by_name () returns it as bytes.

	Args:
		response: The HttpResponse.
		name: The name, as bytes.
		position: The position between the headers with the name, 0 is the first one that was added.
		value_length: Where the length of the value is written.

	Returns:
		The address of the value, None if the response does not have the header.
	"""
)

def http_response_header_value_by_name (response: int, name: str | bytes, position: int = 0) -> bytes | None:
	"""Returns the value of a header of a response by its name.

	Args:
		response: The HttpResponse.
		name: The name of the header.
		position: The position between the headers with the name, 0 is the first one that was added.

	Returns:
		The value, None if the response does not have the header.
	"""
	length = c_size_t (0)
	value = http_response_header_get_by_name (response, lib_c_string (name), position, byref (length))

	return string_at (value, length.value) if (value) else None

http_response_add_header = lib_function (
	"http_response_add_header", [c_void_p, HttpHeaderType, c_char_p], c_uint8,
	"""Sets a header of a response, like http_response_header_set ().

	Args:
		response: The HttpResponse.
		type: An HTTP_HEADER_* value.
		actual_header: The value, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_custom_header_variadic = lib_function (
	"http_response_add_custom_header", None, c_uint8,
	"""Adds a header to a response with a printf format (variadic).

	Args:
		response: The HttpResponse, as c_void_p.
		type: An HTTP_HEADER_* value, as c_int.
		format: The format, as bytes, followed by its arguments.

	Returns:
		0 on success, 1 on error.
	"""
)

def http_response_add_custom_header_value (response: int, header_type: int, value: str | bytes) -> int:
	"""Adds a header to a response with its exact value.

	Args:
		response: The HttpResponse.
		header_type: An HTTP_HEADER_* value.
		value: The value of the header.

	Returns:
		0 on success, 1 on error.
	"""
	return http_response_add_custom_header_variadic (
		c_void_p (response), HttpHeaderType (header_type),
		c_char_p (HEADER_VALUE_FORMAT), c_char_p (lib_c_string (value))
	)

http_response_add_content_type_header = lib_function (
	"http_response_add_content_type_header", [c_void_p, ContentType], c_uint8,
	"""Adds a Content-Type header to a response.

	Args:
		response: The HttpResponse.
		type: An HTTP_CONTENT_TYPE_* value.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_content_length_header = lib_function (
	"http_response_add_content_length_header", [c_void_p, c_size_t], c_uint8,
	"""Adds a Content-Length header to a response.

	Args:
		response: The HttpResponse.
		length: The length of the body in bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_json_headers = lib_function (
	"http_response_add_json_headers", [c_void_p, c_size_t], None,
	"""Adds the Content-Type application/json and the Content-Length headers to a response.

	Args:
		response: The HttpResponse.
		json_len: The length of the body in bytes.
	"""
)

http_response_add_content_range_header = lib_function (
	"http_response_add_content_range_header", [c_void_p, BytesRangePointer], c_uint8,
	"""Adds a Content-Range header to a response from a BytesRange.

	Args:
		response: The HttpResponse.
		bytes_range: The BytesRange.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_video_headers = lib_function (
	"http_response_add_video_headers", [c_void_p, ContentType, BytesRangePointer], None,
	"""Adds the headers of a part of a video to a response.

	Args:
		response: The HttpResponse.
		content_type: The HTTP_CONTENT_TYPE_* of the video.
		bytes_range: The BytesRange of the part.
	"""
)

http_response_add_cors_header = lib_function (
	"http_response_add_cors_header", [c_void_p, c_char_p], c_uint8,
	"""Adds an Access-Control-Allow-Origin header to a response.

	Args:
		response: The HttpResponse.
		origin: The origin, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_cors_header_from_origin = lib_function (
	"http_response_add_cors_header_from_origin", [c_void_p, c_void_p], c_uint8,
	"""Works like http_response_add_cors_header () with an HttpOrigin.

	Args:
		response: The HttpResponse.
		origin: The HttpOrigin.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_whitelist_cors_header = lib_function (
	"http_response_add_whitelist_cors_header", [c_void_p, c_char_p], c_uint8,
	"""Adds an Access-Control-Allow-Origin header only if the domain is in the whitelist.

	Args:
		response: The HttpResponse.
		domain: The domain, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_whitelist_cors_header_from_origin = lib_function (
	"http_response_add_whitelist_cors_header_from_origin", [c_void_p, c_void_p], c_uint8,
	"""Works like http_response_add_whitelist_cors_header () with an HttpOrigin.

	Args:
		response: The HttpResponse.
		origin: The HttpOrigin.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_whitelist_cors_header_from_request = lib_function (
	"http_response_add_whitelist_cors_header_from_request", [c_void_p, c_void_p], c_uint8,
	"""Adds an Access-Control-Allow-Origin header if the Origin of the request is in the whitelist.

	Args:
		http_receive: The HttpReceive of the request.
		response: The HttpResponse.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_cors_allow_credentials_header = lib_function (
	"http_response_add_cors_allow_credentials_header", [c_void_p], c_uint8,
	"""Adds Access-Control-Allow-Credentials, needed when a CORS request has an Authorization.

	Args:
		response: The HttpResponse.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_add_cors_allow_methods_header = lib_function (
	"http_response_add_cors_allow_methods_header", [c_void_p, c_char_p], c_uint8,
	"""Adds Access-Control-Allow-Methods, needed in the responses to a preflight OPTIONS.

	Args:
		response: The HttpResponse.
		methods: The methods, as bytes, like b"GET, HEAD, OPTIONS".

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_set_data = lib_function (
	"http_response_set_data", [c_void_p, c_void_p, c_size_t], None,
	"""Sets a copy of the body of a response, replacing the previous one.

	Args:
		response: The HttpResponse.
		data: The body, as bytes.
		data_len: Its length.
	"""
)

http_response_set_data_ref = lib_function (
	"http_response_set_data_ref", [c_void_p, c_void_p, c_size_t], c_uint8,
	"""Sets a reference to the body of a response, it is not copied nor released.

	Args:
		response: The HttpResponse.
		data: The body, kept alive by the caller until the response was sent.
		data_size: Its length.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_create = lib_function (
	"http_response_create", [HttpStatus, c_void_p, c_size_t], c_void_p,
	"""Creates a response with a status and a copy of its body.

	Args:
		status: An HTTP_STATUS_* value.
		data: The body, as bytes, or None.
		data_len: Its length.

	Returns:
		The HttpResponse, released with http_response_delete ().
	"""
)

http_response_compile_header = lib_function (
	"http_response_compile_header", [c_void_p], None,
	"""Compiles the status and the headers of a response into a single buffer.

	Args:
		response: The HttpResponse.
	"""
)

http_response_compile = lib_function (
	"http_response_compile", [c_void_p], c_uint8,
	"""Compiles the header and the body of a response, ready to be sent.

	Args:
		response: The HttpResponse.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_print = lib_function (
	"http_response_print", [c_void_p], None,
	"""Prints a response.

	Args:
		response: The HttpResponse.
	"""
)

http_response_send = lib_function (
	"http_response_send", [c_void_p, c_void_p], c_uint8,
	"""Sends a compiled response to the connection of a request, the response is not released.

	Args:
		response: The HttpResponse.
		http_receive: The HttpReceive of the request.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_send_split = lib_function (
	"http_response_send_split", [c_void_p, c_void_p], c_uint8,
	"""Sends the compiled header and the body of a response without joining them.

	Args:
		response: The HttpResponse.
		http_receive: The HttpReceive of the request.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_create_and_send = lib_function (
	"http_response_create_and_send", [HttpStatus, c_void_p, c_size_t, c_void_p], c_uint8,
	"""Creates and sends a response with a status and a body.

	Args:
		status: An HTTP_STATUS_* value.
		data: The body, as bytes, or None.
		data_len: Its length.
		http_receive: The HttpReceive of the request.

	Returns:
		0 on success, 1 on error.
	"""
)

def http_send_response_body (body, content_type: int) -> tuple:
	"""Returns the bytes and the content type of a body of http_send_response ()."""
	actual_body = body
	actual_content_type = content_type

	if (isinstance (body, (dict, list))):
		actual_body = json.dumps (body).encode (TEXT_ENCODING)
		actual_content_type = HTTP_CONTENT_TYPE_JSON

	elif (body is None):
		actual_body = b""

	elif (isinstance (body, str)):
		actual_body = body.encode (TEXT_ENCODING)

	return (actual_body, actual_content_type)

def http_send_response (
	http_receive: int, status_code: int,
	body: dict | list | str | bytes | None = None, body_len: int | None = None,
	content_type: int = HTTP_CONTENT_TYPE_HTML
) -> int:
	"""Creates and sends a response with a body.

	A dict or a list is sent as JSON. The length is the one of the encoded bytes, so a
	text with accents is never truncated.

	Args:
		http_receive: The HttpReceive of the request.
		status_code: An HTTP_STATUS_* value.
		body: A dict or a list (JSON), a str (utf-8), bytes, or None for an empty body.
		body_len: The length of the bytes to send, all of them by default.
		content_type: The content type of a str or bytes body, HTML by default.

	Returns:
		0 on success, 1 on error.
	"""
	result = 1

	actual_body, actual_content_type = http_send_response_body (body, content_type)
	length = len (actual_body) if (body_len is None) else body_len

	response = http_response_create (status_code, actual_body, length)
	if (response):
		http_response_add_content_type_header (response, actual_content_type)
		http_response_add_content_length_header (response, length)

		if (not http_response_compile (response)):
			result = http_response_send (response, http_receive)

		http_response_delete (response)

	return result
