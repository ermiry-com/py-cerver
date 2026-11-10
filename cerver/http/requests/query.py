"""The query of a request and the key-value pairs of a query or a form."""

from ctypes import c_void_p, c_char_p

from ...lib import lib_function, lib_c_string

from ...types.string import StringPointer, string_text

from ...utils.utils import strtobool

__all__ = [
	"key_value_pair_new", "key_value_pair_delete", "key_value_pair_create",
	"key_value_pairs_get_value", "key_value_pairs_print",
	"http_query_pairs_get_value", "http_query_pairs_print",
	"http_request_get_query", "http_request_get_query_params",
	"http_request_query_params_print", "http_request_query_params_get_value",
	"http_request_get_query_value", "http_request_get_int_query_value",
	"http_request_get_float_query_value", "http_request_get_bool_query_value"
]

key_value_pair_new = lib_function (
	"key_value_pair_new", [], c_void_p,
	"""Allocates an empty key-value pair.

	Returns:
		The KeyValuePair, released with key_value_pair_delete ().
	"""
)

key_value_pair_delete = lib_function (
	"key_value_pair_delete", [c_void_p], None,
	"""Releases a key-value pair.

	Args:
		kvp_ptr: The KeyValuePair.
	"""
)

key_value_pair_create = lib_function (
	"key_value_pair_create", [c_char_p, c_char_p], c_void_p,
	"""Creates a key-value pair with copies of its values.

	Args:
		key: The key, as bytes.
		value: The value, as bytes.

	Returns:
		The KeyValuePair, released with key_value_pair_delete ().
	"""
)

key_value_pairs_get_value = lib_function (
	"key_value_pairs_get_value", [c_void_p, c_char_p], StringPointer,
	"""Returns the value of a key in a list of key-value pairs.

	Args:
		pairs: The list of pairs.
		key: The key, as bytes.

	Returns:
		A StringPointer, NULL if there is no pair with that key.
	"""
)

key_value_pairs_print = lib_function (
	"key_value_pairs_print", [c_void_p], None,
	"""Prints a list of key-value pairs.

	Args:
		pairs: The list of pairs.
	"""
)

http_query_pairs_get_value = lib_function (
	"http_query_pairs_get_value", [c_void_p, c_char_p], StringPointer,
	"""Returns the value of a key in the pairs of a query or of an x-www-form-urlencoded body.

	Args:
		pairs: The pairs, like the ones of http_request_get_query_params ().
		key: The key, as bytes.

	Returns:
		A StringPointer, NULL if there is no pair with that key.
	"""
)

http_query_pairs_print = lib_function (
	"http_query_pairs_print", [c_void_p], None,
	"""Prints the pairs of a query.

	Args:
		pairs: The pairs.
	"""
)

http_request_get_query = lib_function (
	"http_request_get_query", [c_void_p], StringPointer,
	"""Returns the raw query of the request, without the '?'.

	Args:
		http_request: The request.

	Returns:
		A StringPointer, NULL if the request has no query.
	"""
)

http_request_get_query_params = lib_function (
	"http_request_get_query_params", [c_void_p], c_void_p,
	"""Returns the pairs of the query of the request.

	Args:
		http_request: The request.

	Returns:
		The pairs, None if the request has no query.
	"""
)

http_request_query_params_print = lib_function (
	"http_request_query_params_print", [c_void_p], None,
	"""Prints the pairs of the query of the request.

	Args:
		http_request: The request.
	"""
)

http_request_query_params_get_value = lib_function (
	"http_request_query_params_get_value", [c_void_p, c_char_p], StringPointer,
	"""Returns the value of a key of the query of the request.

	Args:
		http_request: The request.
		key: The key, as bytes.

	Returns:
		A StringPointer, NULL if the query does not have the key.
	"""
)

def http_request_get_query_value (values: int, query_name: str) -> str | None:
	"""Returns the value of a key of a query.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.

	Returns:
		The value, None if it is missing or it is not valid utf-8.
	"""
	return string_text (http_query_pairs_get_value (values, lib_c_string (query_name)))

def http_request_get_int_query_value (values: int, query_name: str) -> int | None:
	"""Returns the value of a key of a query as an integer.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.

	Returns:
		The integer, None if it is missing or it is not an integer.
	"""
	result = None

	value = http_request_get_query_value (values, query_name)
	if (value is not None):
		try:
			result = int (value)

		except ValueError:
			pass

	return result

def http_request_get_float_query_value (values: int, query_name: str) -> float | None:
	"""Returns the value of a key of a query as a float.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.

	Returns:
		The float, None if it is missing or it is not a number.
	"""
	result = None

	value = http_request_get_query_value (values, query_name)
	if (value is not None):
		try:
			result = float (value)

		except ValueError:
			pass

	return result

def http_request_get_bool_query_value (values: int, query_name: str) -> bool | None:
	"""Returns the value of a key of a query as a bool.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.

	Returns:
		The bool of a truth value (see strtobool ()), None if it is missing or it is not one.
	"""
	result = None

	value = http_request_get_query_value (values, query_name)
	if (value is not None):
		try:
			result = bool (strtobool (value))

		except ValueError:
			pass

	return result
