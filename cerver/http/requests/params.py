"""The params of the route that matched a request, like ":id"."""

from ctypes import c_void_p, c_char_p, c_uint

from ...lib import lib_function, lib_c_string, lib_text

from ...types.string import StringPointer, string_text

__all__ = [
	"http_request_get_n_params", "http_request_get_param_at_idx",
	"http_request_get_param", "http_request_get_param_name_at_idx",
	"http_request_get_param_value", "http_get_params_dict", "http_get_params_list"
]

http_request_get_n_params = lib_function (
	"http_request_get_n_params", [c_void_p], c_uint,
	"""Returns how many params the route of the request has.

	Args:
		http_request: The request.

	Returns:
		The number of params.
	"""
)

http_request_get_param_at_idx = lib_function (
	"http_request_get_param_at_idx", [c_void_p, c_uint], StringPointer,
	"""Returns a param of the request by its position in the route, percent-decoded.

	Args:
		http_request: The request.
		idx: The position, from 0.

	Returns:
		A StringPointer, NULL if there is no param in that position.
	"""
)

http_request_get_param = lib_function (
	"http_request_get_param", [c_void_p, c_char_p], StringPointer,
	"""Returns a param of the request by its name in the route (":id" is b"id"), percent-decoded.

	Args:
		http_request: The request.
		name: The name, as bytes.

	Returns:
		A StringPointer, NULL if the route has no param with that name.
	"""
)

http_request_get_param_name_at_idx = lib_function (
	"http_request_get_param_name_at_idx", [c_void_p, c_uint], c_char_p,
	"""Returns the name of a param by its position in the route.

	Args:
		http_request: The request.
		idx: The position, from 0.

	Returns:
		The name, as bytes, None for a param of the first routes API.
	"""
)

def http_request_get_param_value (request: int, name: str) -> str | None:
	"""Returns a param of the request by its name in the route.

	Args:
		request: The request.
		name: The name of the param in the route (":id" is "id").

	Returns:
		The percent-decoded value, None if the route has no param with that name.
	"""
	return string_text (http_request_get_param (request, lib_c_string (name)))

def http_get_params_dict (request: int) -> dict:
	"""Returns the params of the request by their names.

	Args:
		request: The request.

	Returns:
		The values by name, a param without a name is not included.
	"""
	params = {}

	for idx in range (http_request_get_n_params (request)):
		name = lib_text (http_request_get_param_name_at_idx (request, idx))
		value = string_text (http_request_get_param_at_idx (request, idx))
		if ((name is not None) and (value is not None)):
			params[name] = value

	return params

def http_get_params_list (request: int) -> list:
	"""Returns the params of the request in the order of the route.

	Args:
		request: The request.

	Returns:
		The values, a value that is not valid utf-8 is None.
	"""
	return [
		string_text (http_request_get_param_at_idx (request, idx))
		for idx in range (http_request_get_n_params (request))
	]
