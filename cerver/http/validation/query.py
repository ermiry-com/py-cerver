"""The validators of the values of a query (or of an x-www-form-urlencoded body)."""

from typing import Any, Callable

from ...lib import lib_c_string

from ...types.string import string_bytes
from ...utils.utils import strtobool

from ..requests.query import http_query_pairs_get_value

from .common import VALIDATION_REQUIRED, VALIDATION_INVALID, VALIDATION_LENGTH, VALIDATION_FAILED
from .common import validation_decode, validation_error

__all__ = [
	"validate_query_found", "validate_query_exists_internal",
	"validate_query_exists", "validate_query_value", "validate_query_value_with_cast",
	"validate_query_value_with_default",
	"validate_query_int_value", "validate_query_int_limit_value", "validate_query_int_actual_value",
	"validate_query_int_value_with_default",
	"validate_query_float_value", "validate_query_float_value_with_default",
	"validate_query_bool_value", "validate_query_bool_value_with_default"
]

# a value that is missing from the query
QUERY_MISSING = object ()

def validate_query_found (values: int, query_name: str) -> Any:
	"""Returns the text of a key of a query.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.

	Returns:
		The text, None if it is not utf-8, QUERY_MISSING if the query does not have the key.
	"""
	result = QUERY_MISSING

	found = http_query_pairs_get_value (values, lib_c_string (query_name))
	if (found):
		result = validation_decode (string_bytes (found))

	return result

def validate_query_exists_internal (values: int, query_name: str) -> str | None:
	"""Returns a key of a query that is not empty.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.

	Returns:
		The value, None if it is missing, empty or not utf-8.
	"""
	found = validate_query_found (values, query_name)
	return found if (isinstance (found, str) and found) else None

def validate_query_exists (values: int, query_name: str, errors: dict) -> str | None:
	"""Returns a required key of a query.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		errors: The errors of the request, a missing value sets its "required" error.

	Returns:
		The value, None on error.
	"""
	result = validate_query_exists_internal (values, query_name)

	if (result is None):
		validation_error (errors, query_name, VALIDATION_REQUIRED)

	return result

def validate_query_value (
	values: int, query_name: str, min_len: int, max_len: int, errors: dict
) -> str | None:
	"""Returns a required key of a query with a length between two values.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		min_len: The shortest length.
		max_len: The longest length.
		errors: The errors of the request.

	Returns:
		The value, None on error.
	"""
	result = None

	found = validate_query_exists (values, query_name, errors)
	if (found is not None):
		if (min_len <= len (found) <= max_len):
			result = found

		else:
			validation_error (errors, query_name, VALIDATION_LENGTH, minimum=min_len, maximum=max_len)

	return result

def validate_query_value_with_cast (
	values: int, query_name: str, cast: Callable [[str], Any], errors: dict
) -> Any:
	"""Returns a required key of a query converted by a function.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		cast: Converts the text, it raises ValueError or TypeError for an invalid one.
		errors: The errors of the request.

	Returns:
		The converted value, None on error.
	"""
	result = None

	found = validate_query_found (values, query_name)
	if (found is QUERY_MISSING):
		validation_error (errors, query_name, VALIDATION_REQUIRED)

	elif (found is None):
		validation_error (errors, query_name, VALIDATION_INVALID)

	else:
		try:
			result = cast (found)

		except (ValueError, TypeError):
			validation_error (errors, query_name, VALIDATION_INVALID)

	return result

def validate_query_value_with_default (values: int, query_name: str, default: Any) -> Any:
	"""Returns a key of a query, or a default when it is missing or empty.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		default: The value of a missing key.

	Returns:
		The value or the default.
	"""
	result = validate_query_exists_internal (values, query_name)
	return default if (result is None) else result

def validate_query_cast (
	values: int, query_name: str, cast: Callable [[str], Any], errors: dict | None, default: Any
) -> Any:
	"""Converts a key of a query, setting its errors when errors is a dict."""
	result = default

	found = validate_query_found (values, query_name)
	if (found is QUERY_MISSING):
		if (errors is not None):
			validation_error (errors, query_name, VALIDATION_REQUIRED)

	else:
		try:
			# a value that is not utf-8 is invalid like a value that is not a number
			if (found is None):
				raise ValueError ("not utf-8")

			result = cast (found)

		except (ValueError, TypeError):
			if (errors is not None):
				validation_error (errors, query_name, VALIDATION_INVALID)

	return result

def query_bool (value: str) -> bool:
	"""Returns the bool of a truth value."""
	return bool (strtobool (value))

def validate_query_int_value (values: int, query_name: str, errors: dict) -> int | None:
	"""Returns a required integer key of a query.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		errors: The errors of the request.

	Returns:
		The integer, None on error.
	"""
	return validate_query_cast (values, query_name, int, errors, None)

def validate_query_int_limit_value (
	values: int, query_name: str, min_value: int, max_value: int, errors: dict
) -> int | None:
	"""Returns a required integer key of a query, clamped between two values.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		min_value: The value of a smaller integer.
		max_value: The value of a bigger integer.
		errors: The errors of the request.

	Returns:
		The clamped integer, None on error.
	"""
	result = validate_query_int_value (values, query_name, errors)
	if (result is not None):
		result = min (max (result, min_value), max_value)

	return result

def validate_query_int_actual_value (
	values: int, query_name: str, validation: Callable [[int], bool], errors: dict
) -> int | None:
	"""Returns a required integer key of a query that passes a check.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		validation: Returns True for a valid integer.
		errors: The errors of the request.

	Returns:
		The integer, None on error.
	"""
	result = None

	actual_value = validate_query_int_value (values, query_name, errors)
	if (actual_value is not None):
		if (validation (actual_value)):
			result = actual_value

		else:
			validation_error (errors, query_name, VALIDATION_FAILED)

	return result

def validate_query_int_value_with_default (values: int, query_name: str, default: int) -> int:
	"""Returns an integer key of a query, or a default when it is missing or invalid.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		default: The value of a missing or invalid key.

	Returns:
		The integer or the default.
	"""
	return validate_query_cast (values, query_name, int, None, default)

def validate_query_float_value (values: int, query_name: str, errors: dict) -> float | None:
	"""Returns a required number key of a query.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		errors: The errors of the request.

	Returns:
		The number, None on error.
	"""
	return validate_query_cast (values, query_name, float, errors, None)

def validate_query_float_value_with_default (values: int, query_name: str, default: float) -> float:
	"""Returns a number key of a query, or a default when it is missing or invalid.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		default: The value of a missing or invalid key.

	Returns:
		The number or the default.
	"""
	return validate_query_cast (values, query_name, float, None, default)

def validate_query_bool_value (values: int, query_name: str, errors: dict) -> bool | None:
	"""Returns a required truth value key of a query (see strtobool ()).

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		errors: The errors of the request.

	Returns:
		The bool, None on error.
	"""
	return validate_query_cast (values, query_name, query_bool, errors, None)

def validate_query_bool_value_with_default (values: int, query_name: str, default: bool) -> bool:
	"""Returns a truth value key of a query, or a default when it is missing or invalid.

	Args:
		values: The pairs of http_request_get_query_params ().
		query_name: The key.
		default: The value of a missing or invalid key.

	Returns:
		The bool or the default.
	"""
	return validate_query_cast (values, query_name, query_bool, None, default)
