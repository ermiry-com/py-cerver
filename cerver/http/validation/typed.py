"""Typed validators of the values of a query or of a JSON body: texts, numbers in a range,
bools, choices, lists and dates.

Each validator takes the errors of the request and the name of the field: a missing
required value sets its "required" error, and a value of another type or outside its
limits sets its "invalid" error (or the message of its limits). An optional value that is
missing returns its default without an error.
"""

from datetime import datetime
from typing import Any, Callable, Iterable

from ...utils.utils import strtobool

from .common import VALIDATION_REQUIRED, VALIDATION_INVALID, VALIDATION_LENGTH
from .common import VALIDATION_RANGE, VALIDATION_CHOICES, VALIDATION_ITEMS
from .common import validation_error
from .query import QUERY_MISSING, validate_query_found

__all__ = [
	"VALIDATION_LIST_SEPARATOR",
	"validate_string", "validate_int", "validate_float", "validate_bool",
	"validate_choice", "validate_list", "validate_date",
	"validate_query_string", "validate_query_int", "validate_query_float", "validate_query_bool",
	"validate_query_choice", "validate_query_list", "validate_query_date",
	"validate_body_string", "validate_body_int", "validate_body_float", "validate_body_bool",
	"validate_body_choice", "validate_body_list", "validate_body_date"
]

# the separator of the items of a list in a query, like ?ids=a,b,c
VALIDATION_LIST_SEPARATOR = ","

# a value that the caller did not give
MISSING = QUERY_MISSING

def validate_missing (field: str, errors: dict, required: bool, default: Any) -> Any:
	"""Returns the default of a missing value, setting the required error when it is required."""
	if (required):
		validation_error (errors, field, VALIDATION_REQUIRED)

	return None if (required) else default

def validate_limits (value, field: str, errors: dict, minimum, maximum, message: str, measure) -> bool:
	"""Returns if a measure of a value is between its limits, setting the error when it is not."""
	result = True

	measured = measure (value)
	if (((minimum is not None) and (measured < minimum)) or ((maximum is not None) and (measured > maximum))):
		result = False
		validation_error (errors, field, message, minimum=minimum, maximum=maximum)

	return result

def validate_string (
	value: Any, field: str, errors: dict, required: bool = True, default: Any = None,
	min_len: int | None = None, max_len: int | None = None
) -> str | None:
	"""Validates a text, an empty one is missing.

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.
		min_len: The shortest length.
		max_len: The longest length.

	Returns:
		The text, the default, or None on error.
	"""
	result = None

	if ((value is MISSING) or (value is None) or (value == "")):
		result = validate_missing (field, errors, required, default)

	elif (not isinstance (value, str)):
		validation_error (errors, field, VALIDATION_INVALID)

	elif (validate_limits (value, field, errors, min_len, max_len, VALIDATION_LENGTH, len)):
		result = value

	return result

def number_value (value: Any, cast: Callable) -> Any:
	"""Converts a text or a JSON number, a bool is never a number."""
	result = None

	if (isinstance (value, str)):
		result = cast (value)

	elif ((not isinstance (value, bool)) and isinstance (value, (int, float))):
		result = cast (value)

	else:
		raise ValueError ("not a number")

	return result

def json_int (value: Any) -> int:
	"""Converts a value into an integer, 5.0 is 5 but 5.5 is not an integer."""
	result = None

	if (isinstance (value, float)):
		if (not value.is_integer ()):
			raise ValueError ("not an integer")

		result = int (value)

	else:
		result = int (value)

	return result

def validate_number (
	value: Any, field: str, errors: dict, required: bool, default: Any,
	minimum, maximum, cast: Callable
) -> Any:
	"""Validates a number with a conversion and its limits."""
	result = None

	if ((value is MISSING) or (value is None) or (value == "")):
		result = validate_missing (field, errors, required, default)

	else:
		try:
			converted = number_value (value, cast)
			if (validate_limits (converted, field, errors, minimum, maximum, VALIDATION_RANGE, lambda number: number)):
				result = converted

		except (ValueError, TypeError, OverflowError):
			validation_error (errors, field, VALIDATION_INVALID)

	return result

def validate_int (
	value: Any, field: str, errors: dict, required: bool = True, default: Any = None,
	minimum: int | None = None, maximum: int | None = None
) -> int | None:
	"""Validates an integer, from a text or a JSON number.

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.
		minimum: The smallest value.
		maximum: The biggest value.

	Returns:
		The integer, the default, or None on error.
	"""
	return validate_number (value, field, errors, required, default, minimum, maximum, json_int)

def validate_float (
	value: Any, field: str, errors: dict, required: bool = True, default: Any = None,
	minimum: float | None = None, maximum: float | None = None
) -> float | None:
	"""Validates a number, from a text or a JSON number.

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.
		minimum: The smallest value.
		maximum: The biggest value.

	Returns:
		The number, the default, or None on error.
	"""
	return validate_number (value, field, errors, required, default, minimum, maximum, float)

def validate_bool (
	value: Any, field: str, errors: dict, required: bool = True, default: Any = None
) -> bool | None:
	"""Validates a bool, a JSON bool or a truth value text (see strtobool ()).

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.

	Returns:
		The bool, the default, or None on error.
	"""
	result = None

	if ((value is MISSING) or (value is None) or (value == "")):
		result = validate_missing (field, errors, required, default)

	elif (isinstance (value, bool)):
		result = value

	else:
		try:
			result = bool (strtobool (value))

		except (ValueError, AttributeError):
			validation_error (errors, field, VALIDATION_INVALID)

	return result

def validate_choice (
	value: Any, field: str, errors: dict, choices: Iterable,
	required: bool = True, default: Any = None
) -> Any:
	"""Validates that a value is one of some choices, like the values of an enum.

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		choices: The valid values.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.

	Returns:
		The value, the default, or None on error.
	"""
	result = None

	valid = list (choices)
	if ((value is MISSING) or (value is None) or (value == "")):
		result = validate_missing (field, errors, required, default)

	elif (value in valid):
		result = value

	else:
		validation_error (errors, field, VALIDATION_CHOICES, choices=", ".join (str (choice) for choice in valid))

	return result

def validate_list (
	value: Any, field: str, errors: dict, item: Callable [[Any], Any] | None = None,
	required: bool = True, default: Any = None,
	min_items: int | None = None, max_items: int | None = None
) -> list | None:
	"""Validates a list, a JSON array or a text with items separated by commas.

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		item: Converts each item, it raises ValueError or TypeError for an invalid one.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.
		min_items: The fewest items.
		max_items: The most items.

	Returns:
		The list, the default, or None on error.
	"""
	result = None

	if ((value is MISSING) or (value is None) or (value == "")):
		result = validate_missing (field, errors, required, default)

	elif (not isinstance (value, (list, str))):
		validation_error (errors, field, VALIDATION_INVALID)

	else:
		items = value.split (VALIDATION_LIST_SEPARATOR) if (isinstance (value, str)) else value

		try:
			converted = [item (element) for element in items] if (item) else list (items)
			if (validate_limits (converted, field, errors, min_items, max_items, VALIDATION_ITEMS, len)):
				result = converted

		except (ValueError, TypeError):
			validation_error (errors, field, VALIDATION_INVALID)

	return result

def validate_date (
	value: Any, field: str, errors: dict, required: bool = True, default: Any = None,
	minimum: datetime | None = None, maximum: datetime | None = None
) -> datetime | None:
	"""Validates an ISO 8601 date, like "2026-11-09" or "2026-11-09T17:00:00+00:00".

	Args:
		value: The value, MISSING when it was not given.
		field: The name of the field.
		errors: The errors of the request.
		required: False to return the default of a missing value.
		default: The value of a missing optional value.
		minimum: The earliest date.
		maximum: The latest date.

	Returns:
		The datetime, the default, or None on error.
	"""
	result = None

	if ((value is MISSING) or (value is None) or (value == "")):
		result = validate_missing (field, errors, required, default)

	else:
		try:
			parsed = datetime.fromisoformat (value)
			if (validate_limits (parsed, field, errors, minimum, maximum, VALIDATION_RANGE, lambda date: date)):
				result = parsed

		except (ValueError, TypeError):
			validation_error (errors, field, VALIDATION_INVALID)

	return result

# the query
def query_value (values: int, name: str) -> Any:
	"""Returns the text of a key of a query, MISSING when it does not have it."""
	found = validate_query_found (values, name)
	return found if (found is MISSING) else (found if (found is not None) else b"")

def validate_query_string (values: int, name: str, errors: dict, **limits) -> str | None:
	"""Validates a text of a query, see validate_string () for the limits."""
	return validate_string (query_value (values, name), name, errors, **limits)

def validate_query_int (values: int, name: str, errors: dict, **limits) -> int | None:
	"""Validates an integer of a query, see validate_int () for the limits."""
	return validate_int (query_value (values, name), name, errors, **limits)

def validate_query_float (values: int, name: str, errors: dict, **limits) -> float | None:
	"""Validates a number of a query, see validate_float () for the limits."""
	return validate_float (query_value (values, name), name, errors, **limits)

def validate_query_bool (values: int, name: str, errors: dict, **limits) -> bool | None:
	"""Validates a truth value of a query, see validate_bool ()."""
	return validate_bool (query_value (values, name), name, errors, **limits)

def validate_query_choice (values: int, name: str, errors: dict, choices: Iterable, **limits) -> Any:
	"""Validates a value of a query that is one of some choices, see validate_choice ()."""
	return validate_choice (query_value (values, name), name, errors, choices, **limits)

def validate_query_list (values: int, name: str, errors: dict, **limits) -> list | None:
	"""Validates a list of a query, items separated by commas, see validate_list ()."""
	return validate_list (query_value (values, name), name, errors, **limits)

def validate_query_date (values: int, name: str, errors: dict, **limits) -> datetime | None:
	"""Validates an ISO 8601 date of a query, see validate_date ()."""
	return validate_date (query_value (values, name), name, errors, **limits)

# the body
def body_value (body: dict, name: str) -> Any:
	"""Returns a value of a JSON body, MISSING when it does not have it."""
	return body.get (name, MISSING) if (isinstance (body, dict)) else MISSING

def validate_body_string (body: dict, name: str, errors: dict, **limits) -> str | None:
	"""Validates a text of a JSON body, see validate_string () for the limits."""
	return validate_string (body_value (body, name), name, errors, **limits)

def validate_body_int (body: dict, name: str, errors: dict, **limits) -> int | None:
	"""Validates an integer of a JSON body, see validate_int () for the limits."""
	return validate_int (body_value (body, name), name, errors, **limits)

def validate_body_float (body: dict, name: str, errors: dict, **limits) -> float | None:
	"""Validates a number of a JSON body, see validate_float () for the limits."""
	return validate_float (body_value (body, name), name, errors, **limits)

def validate_body_bool (body: dict, name: str, errors: dict, **limits) -> bool | None:
	"""Validates a bool of a JSON body, see validate_bool ()."""
	return validate_bool (body_value (body, name), name, errors, **limits)

def validate_body_choice (body: dict, name: str, errors: dict, choices: Iterable, **limits) -> Any:
	"""Validates a value of a JSON body that is one of some choices, see validate_choice ()."""
	return validate_choice (body_value (body, name), name, errors, choices, **limits)

def validate_body_list (body: dict, name: str, errors: dict, **limits) -> list | None:
	"""Validates an array of a JSON body, see validate_list ()."""
	return validate_list (body_value (body, name), name, errors, **limits)

def validate_body_date (body: dict, name: str, errors: dict, **limits) -> datetime | None:
	"""Validates an ISO 8601 date of a JSON body, see validate_date ()."""
	return validate_date (body_value (body, name), name, errors, **limits)
