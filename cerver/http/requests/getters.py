"""The values of a request: its id, its client, its url, its headers and its data."""

from ctypes import CFUNCTYPE, c_void_p, c_char_p, c_size_t, c_bool, c_uint8
from typing import TypeAlias

from ...lib import lib_function

from ...types.string import StringPointer

from ..content import ContentType
from ..headers import HttpHeaderType
from ..utils import BytesRangePointer

from .methods import RequestMethod

__all__ = [
	"HTTP_REQUEST_ID_LENGTH", "HTTP_REQUEST_ID_SIZE", "HTTP_REQUEST_CLIENT_IP_SIZE",
	"RequestDeleteDecoded", "RequestDeleteCustom",
	"http_request_new", "http_request_delete", "http_request_create",
	"http_request_get_method", "http_request_get_id", "http_request_get_client_ip",
	"http_request_id_is_valid", "http_request_id_generate",
	"http_request_get_url", "http_request_get_header",
	"http_request_get_custom_headers_count", "http_request_get_custom_header",
	"http_request_get_content_type", "http_request_get_content_type_string",
	"http_request_content_type_is_json", "http_request_get_bytes_range",
	"http_request_get_decoded_data", "http_request_set_decoded_data",
	"http_request_set_delete_decoded_data", "http_request_set_default_delete_decoded_data",
	"http_request_get_custom_data", "http_request_set_custom_data",
	"http_request_set_delete_custom_data", "http_request_set_default_delete_custom_data",
	"http_request_headers_print", "http_request_headers_print_full"
]

HTTP_REQUEST_ID_LENGTH = 64
HTTP_REQUEST_ID_SIZE = HTTP_REQUEST_ID_LENGTH + 1

# NETWORK_ADDRESS_STRING_SIZE, an ip with its zone
HTTP_REQUEST_CLIENT_IP_SIZE = 62

# void (*) (void *), the delete of the decoded data and of the custom data of a request
RequestDeleteDecoded: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore
RequestDeleteCustom: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

http_request_new = lib_function (
	"http_request_new", [], c_void_p,
	"""Allocates an empty request.

	Returns:
		The HttpRequest, released with http_request_delete ().
	"""
)

http_request_delete = lib_function (
	"http_request_delete", [c_void_p], None,
	"""Releases a request.

	Args:
		http_request: The HttpRequest.
	"""
)

http_request_create = lib_function (
	"http_request_create", [], c_void_p,
	"""Creates a request with its values ready to be parsed.

	Returns:
		The HttpRequest, released with http_request_delete ().
	"""
)

http_request_get_method = lib_function (
	"http_request_get_method", [c_void_p], RequestMethod,
	"""Returns the method of the request.

	Args:
		http_request: The request.

	Returns:
		A REQUEST_METHOD_* value.
	"""
)

http_request_get_id = lib_function (
	"http_request_get_id", [c_void_p], c_char_p,
	"""Returns the id of the request, when the cerver identifies its requests.

	Args:
		http_request: The request.

	Returns:
		The id, as bytes, b"" when the requests are not identified.
	"""
)

http_request_get_client_ip = lib_function (
	"http_request_get_client_ip", [c_void_p], c_char_p,
	"""Returns the address of the client: the peer, or the one forwarded by a trusted proxy.

	Args:
		http_request: The request.

	Returns:
		The address, as bytes, with its zone when it is link local.
	"""
)

http_request_id_is_valid = lib_function (
	"http_request_id_is_valid", [c_char_p, c_size_t], c_bool,
	"""Returns if an X-Request-Id can be used: up to 64 characters of [A-Za-z0-9._-].

	Args:
		value: The id, as bytes.
		length: Its length.

	Returns:
		True if it is valid.
	"""
)

http_request_id_generate = lib_function (
	"http_request_id_generate", [c_void_p], c_uint8,
	"""Writes a new UUID v4 in a buffer.

	Args:
		id: A writable buffer of at least HTTP_REQUEST_ID_SIZE bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_request_get_url = lib_function (
	"http_request_get_url", [c_void_p], StringPointer,
	"""Returns the path of the request, without the query.

	Args:
		http_request: The request.

	Returns:
		A StringPointer.
	"""
)

http_request_get_header = lib_function (
	"http_request_get_header", [c_void_p, HttpHeaderType], StringPointer,
	"""Returns the value of a header of the request by its type.

	Args:
		http_request: The request.
		header: An HTTP_HEADER_* value.

	Returns:
		A StringPointer, NULL if the request does not have it.
	"""
)

http_request_get_custom_headers_count = lib_function (
	"http_request_get_custom_headers_count", [c_void_p], c_size_t,
	"""Returns how many headers that cerver does not know the request has.

	Args:
		http_request: The request.

	Returns:
		The number of custom headers.
	"""
)

http_request_get_custom_header = lib_function (
	"http_request_get_custom_header", [c_void_p, c_char_p], c_char_p,
	"""Returns the value of a header that cerver does not know, by its name.

	Args:
		http_request: The request.
		header: The name, as bytes, in any case.

	Returns:
		The value, as bytes, None if the request does not have it.
	"""
)

http_request_get_content_type = lib_function (
	"http_request_get_content_type", [c_void_p], ContentType,
	"""Returns the content type of the body of the request.

	Args:
		http_request: The request.

	Returns:
		An HTTP_CONTENT_TYPE_* value.
	"""
)

http_request_get_content_type_string = lib_function (
	"http_request_get_content_type_string", [c_void_p], StringPointer,
	"""Returns the value of the Content-Type of the request.

	Args:
		http_request: The request.

	Returns:
		A StringPointer, NULL if the request does not have it.
	"""
)

http_request_content_type_is_json = lib_function (
	"http_request_content_type_is_json", [c_void_p], c_bool,
	"""Returns if the Content-Type of the request is application/json.

	Args:
		http_request: The request.

	Returns:
		True for a JSON body.
	"""
)

http_request_get_bytes_range = lib_function (
	"http_request_get_bytes_range", [c_void_p, BytesRangePointer], c_bool,
	"""Reads the Range header of the request.

	Args:
		http_request: The request.
		bytes_range: The BytesRange that gets it.

	Returns:
		True on success.
	"""
)

http_request_get_decoded_data = lib_function (
	"http_request_get_decoded_data", [c_void_p], c_void_p,
	"""Returns the data that the authentication decoded from the JWT of the request.

	With decode data into JSON it is a C string, use http_request_get_decoded_json ().

	Args:
		http_request: The request.

	Returns:
		The address of the data, None if it has none.
	"""
)

http_request_set_decoded_data = lib_function (
	"http_request_set_decoded_data", [c_void_p, c_void_p], None,
	"""Sets the decoded data of the request.

	Args:
		http_request: The request.
		decoded_data: The data.
	"""
)

http_request_set_delete_decoded_data = lib_function (
	"http_request_set_delete_decoded_data", [c_void_p, c_void_p], None,
	"""Sets how the decoded data of the request is released.

	Args:
		http_request: The request.
		delete_decoded_data: An Action kept by the caller, or None.
	"""
)

http_request_set_default_delete_decoded_data = lib_function (
	"http_request_set_default_delete_decoded_data", [c_void_p], None,
	"""Releases the decoded data of the request with free ().

	Args:
		http_request: The request.
	"""
)

http_request_get_custom_data = lib_function (
	"http_request_get_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data that an authentication handler set in the request.

	Args:
		http_request: The request.

	Returns:
		The address of the data, None if it has none.
	"""
)

http_request_set_custom_data = lib_function (
	"http_request_set_custom_data", [c_void_p, c_void_p], None,
	"""Sets the custom data of the request.

	Args:
		http_request: The request.
		custom_data: The data.
	"""
)

http_request_set_delete_custom_data = lib_function (
	"http_request_set_delete_custom_data", [c_void_p, c_void_p], None,
	"""Sets how the custom data of the request is released.

	Args:
		http_request: The request.
		delete_custom_data: An Action kept by the caller, or None.
	"""
)

http_request_set_default_delete_custom_data = lib_function (
	"http_request_set_default_delete_custom_data", [c_void_p], None,
	"""Releases the custom data of the request with free ().

	Args:
		http_request: The request.
	"""
)

http_request_headers_print = lib_function (
	"http_request_headers_print", [c_void_p], None,
	"""Prints the headers of the request that cerver knows.

	Args:
		http_request: The request.
	"""
)

http_request_headers_print_full = lib_function (
	"http_request_headers_print_full", [c_void_p], None,
	"""Prints every header of the request.

	Args:
		http_request: The request.
	"""
)
