"""The values of a request as Python text, without reading the Strings of cerver by hand."""

import json

from ctypes import cast, c_char_p

from ...lib import lib_c_string, lib_text

from ...types.string import string_text

from ..headers import HTTP_HEADER_CONTENT_TYPE

from .body import http_request_get_body
from .getters import http_request_get_url, http_request_get_header
from .getters import http_request_get_custom_header, http_request_get_id
from .getters import http_request_get_client_ip, http_request_get_decoded_data
from .params import http_request_get_param_at_idx, http_request_get_param
from .query import http_request_get_query, http_request_query_params_get_value

__all__ = [
	"http_request_get_url_string", "http_request_get_query_string",
	"http_request_get_param_string", "http_request_get_named_param_string",
	"http_request_get_header_string", "http_request_get_custom_header_string",
	"http_request_get_query_value_string", "http_request_get_body_string",
	"http_request_get_id_string", "http_request_get_client_ip_string",
	"http_request_get_decoded_string", "http_request_get_decoded_json",
	"http_request_content_type_is_multi_part"
]

HTTP_CONTENT_TYPE_MULTI_PART = "multipart/form-data"

def http_request_get_url_string (request: int) -> str | None:
	"""Returns the path of the request, without its query.

	Args:
		request: The request.

	Returns:
		The path.
	"""
	return string_text (http_request_get_url (request))

def http_request_get_query_string (request: int) -> str | None:
	"""Returns the raw query of the request.

	Args:
		request: The request.

	Returns:
		The query without the '?', None if the request has none.
	"""
	return string_text (http_request_get_query (request))

def http_request_get_param_string (request: int, index: int) -> str | None:
	"""Returns a param of the route of the request by its position.

	Args:
		request: The request.
		index: The position, from 0.

	Returns:
		The percent-decoded value, None if there is no param in that position.
	"""
	return string_text (http_request_get_param_at_idx (request, index))

def http_request_get_named_param_string (request: int, name: str) -> str | None:
	"""Returns a param of the route of the request by its name.

	Args:
		request: The request.
		name: The name in the route (":id" is "id").

	Returns:
		The percent-decoded value, None if the route has no param with that name.
	"""
	return string_text (http_request_get_param (request, lib_c_string (name)))

def http_request_get_header_string (request: int, header: int) -> str | None:
	"""Returns the value of a header of the request by its type.

	Args:
		request: The request.
		header: An HTTP_HEADER_* value.

	Returns:
		The value, None if the request does not have it.
	"""
	return string_text (http_request_get_header (request, header))

def http_request_content_type_is_multi_part (request: int) -> bool:
	"""Checks if the Content-Type of the request is multipart/form-data.

	Args:
		request: The request.

	Returns:
		True if the request declares a multipart/form-data body, in any case.
	"""
	content_type = http_request_get_header_string (request, HTTP_HEADER_CONTENT_TYPE)

	return (content_type is not None) and (HTTP_CONTENT_TYPE_MULTI_PART in content_type.lower ())

def http_request_get_custom_header_string (request: int, name: str) -> str | None:
	"""Returns the value of a header that cerver does not know, by its name.

	Args:
		request: The request.
		name: The name of the header, in any case.

	Returns:
		The value, None if the request does not have it.
	"""
	return lib_text (http_request_get_custom_header (request, lib_c_string (name)))

def http_request_get_query_value_string (request: int, key: str) -> str | None:
	"""Returns the value of a key of the query of the request.

	Args:
		request: The request.
		key: The key.

	Returns:
		The value, None if the query does not have it.
	"""
	return string_text (http_request_query_params_get_value (request, lib_c_string (key)))

def http_request_get_body_string (request: int) -> str | None:
	"""Returns the body of the request as text.

	Args:
		request: The request.

	Returns:
		The body, None if it has none or it is not valid utf-8.
	"""
	return string_text (http_request_get_body (request))

def http_request_get_id_string (request: int) -> str | None:
	"""Returns the id of the request, when the cerver identifies its requests.

	Args:
		request: The request.

	Returns:
		The id, None when the requests are not identified.
	"""
	return lib_text (http_request_get_id (request)) or None

def http_request_get_client_ip_string (request: int) -> str | None:
	"""Returns the address of the client of the request.

	Args:
		request: The request.

	Returns:
		The peer, or the address forwarded by a trusted proxy.
	"""
	return lib_text (http_request_get_client_ip (request))

def http_request_get_decoded_string (request: int) -> str | None:
	"""Returns the decoded data of a route that decodes its JWT into JSON, as text.

	Args:
		request: The request.

	Returns:
		The JSON text, None if the request has no decoded data.
	"""
	result = None

	decoded = http_request_get_decoded_data (request)
	if (decoded):
		result = lib_text (cast (decoded, c_char_p).value)

	return result

def http_request_get_decoded_json (request: int) -> dict | None:
	"""Returns the decoded data of a route that decodes its JWT into JSON.

	Args:
		request: The request.

	Returns:
		The values of the token, None if the request has no decoded data or it is not an object.
	"""
	result = None

	decoded = http_request_get_decoded_string (request)
	if (decoded):
		try:
			loaded = json.loads (decoded)
			if (isinstance (loaded, dict)):
				result = loaded

		except ValueError:
			pass

	return result
