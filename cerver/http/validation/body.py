"""The validators of the values of a JSON body."""

from typing import Any

from .common import VALIDATION_REQUIRED, VALIDATION_INVALID, VALIDATION_LENGTH
from .common import validation_error

__all__ = [
	"validate_body_value_exists", "validate_body_string_value_exists_ignore_size",
	"validate_body_value", "validate_body_value_optional", "validate_body_value_with_default",
	"validate_body_int_value_exists", "validate_body_float_value_exists"
]

def body_value_present (value: Any) -> bool:
	"""Returns if a value of a body counts as given: an empty text does not."""
	return (value is not None) and (not (isinstance (value, str) and (not value)))

def validate_body_value_exists (body: dict, value: str, errors: dict) -> Any:
	"""Returns a required value of a body, an empty text is missing.

	Args:
		body: The JSON body.
		value: The key.
		errors: The errors of the request.

	Returns:
		The value, None on error.
	"""
	result = body.get (value)

	if (not body_value_present (result)):
		result = None
		validation_error (errors, value, VALIDATION_REQUIRED)

	return result

def validate_body_string_value_exists_ignore_size (body: dict, value: str, errors: dict) -> str | None:
	"""Returns a required text value of a body, an empty one too.

	Args:
		body: The JSON body.
		value: The key.
		errors: The errors of the request.

	Returns:
		The text, None on error.
	"""
	result = None

	if (value not in body):
		validation_error (errors, value, VALIDATION_REQUIRED)

	elif (isinstance (body[value], str)):
		result = body[value]

	else:
		validation_error (errors, value, VALIDATION_INVALID)

	return result

def validate_body_value (body: dict, value: str, min_len: int, max_len: int, errors: dict) -> Any:
	"""Returns a required text, list or object value of a body with a length between two values.

	Args:
		body: The JSON body.
		value: The key.
		min_len: The shortest length.
		max_len: The longest length.
		errors: The errors of the request.

	Returns:
		The value, None on error.
	"""
	result = None

	# a value without a length, like a number, is invalid instead of raising TypeError
	found = validate_body_value_exists (body, value, errors)
	if (found is not None):
		if (not isinstance (found, (str, list, dict))):
			validation_error (errors, value, VALIDATION_INVALID)

		elif (min_len <= len (found) <= max_len):
			result = found

		else:
			validation_error (errors, value, VALIDATION_LENGTH, minimum=min_len, maximum=max_len)

	return result

def validate_body_value_optional (body: dict, value: str) -> Any:
	"""Returns a value of a body, None when it is missing.

	Args:
		body: The JSON body.
		value: The key.

	Returns:
		The value or None.
	"""
	return body.get (value)

def validate_body_value_with_default (body: dict, value: str, default: Any) -> Any:
	"""Returns a value of a body, or a default when it is missing, null or an empty text.

	Args:
		body: The JSON body.
		value: The key.
		default: The value of a missing key.

	Returns:
		The value or the default.
	"""
	found = body.get (value)
	return found if (body_value_present (found)) else default

def validate_body_int_value_exists (body: dict, value: str, errors: dict) -> int | None:
	"""Returns a required integer value of a body.

	JSON has a single number type: 5.0 is the integer 5, and a bool is never a number.

	Args:
		body: The JSON body.
		value: The key.
		errors: The errors of the request, "required" when it is missing, "invalid" when it
			is not an integer.

	Returns:
		The integer, None on error.
	"""
	result = None

	if (value not in body):
		validation_error (errors, value, VALIDATION_REQUIRED)

	else:
		found = body[value]
		if (type (found) is int):
			result = found

		elif ((type (found) is float) and found.is_integer ()):
			result = int (found)

		else:
			validation_error (errors, value, VALIDATION_INVALID)

	return result

def validate_body_float_value_exists (body: dict, value: str, errors: dict) -> float | None:
	"""Returns a required number value of a body.

	JSON has a single number type: the integer 5 is 5.0, and a bool is never a number.

	Args:
		body: The JSON body.
		value: The key.
		errors: The errors of the request, "required" when it is missing, "invalid" when it
			is not a number.

	Returns:
		The number, None on error.
	"""
	result = None

	if (value not in body):
		validation_error (errors, value, VALIDATION_REQUIRED)

	else:
		found = body[value]
		if (type (found) in (int, float)):
			result = float (found)

		else:
			validation_error (errors, value, VALIDATION_INVALID)

	return result
