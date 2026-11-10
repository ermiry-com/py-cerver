"""The validators of the parts of a multipart/form-data request."""

from typing import Any, Callable

from ...core.files import file_exists
from ...lib import lib_c_string

from ...utils.utils import strtobool

from ..multipart import http_multi_part_is_file, http_multi_part_get_saved_filename
from ..multipart import http_multi_part_get_file
from ..requests.multipart import http_request_multi_parts_get, http_request_multi_parts_get_value
from ..requests.multipart import http_request_multi_parts_get_filename
from ..requests.multipart import http_request_multi_parts_get_saved_filename

from .common import VALIDATION_REQUIRED, VALIDATION_INVALID, VALIDATION_LENGTH, VALIDATION_FAILED
from .common import VALIDATION_FILE_MISSING, VALIDATION_NOT_FILE
from .common import validation_decode, validation_error

__all__ = [
	"validate_mparts_exists", "validate_mparts_value", "validate_mparts_value_with_default",
	"validate_mparts_int", "validate_mparts_int_value", "validate_mparts_int_with_default",
	"validate_mparts_float", "validate_mparts_float_value", "validate_mparts_float_with_default",
	"validate_mparts_bool", "validate_mparts_bool_with_default",
	"validate_mparts_file", "validate_mparts_optional_file", "validate_mparts_file_exists",
	"validate_mparts_filename_exists", "validate_mparts_saved_filename_exists",
	"validate_mparts_saved_file_exists"
]

def mparts_value (request: int, value: str) -> bytes | None:
	"""Returns the raw value of the part with a name."""
	return http_request_multi_parts_get_value (request, lib_c_string (value))

def validate_mparts_exists (request: int, value: str, errors: dict) -> str | None:
	"""Returns a required value part that is not empty.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The value, None on error.
	"""
	result = validation_decode (mparts_value (request, value)) or None

	if (result is None):
		validation_error (errors, value, VALIDATION_REQUIRED)

	return result

def validate_mparts_value (request: int, value: str, min_len: int, max_len: int, errors: dict) -> str | None:
	"""Returns a required value part with a length between two values.

	Args:
		request: The request.
		value: The name of the part.
		min_len: The shortest length.
		max_len: The longest length.
		errors: The errors of the request.

	Returns:
		The value, None on error.
	"""
	result = None

	found = validate_mparts_exists (request, value, errors)
	if (found is not None):
		if (min_len <= len (found) <= max_len):
			result = found

		else:
			validation_error (errors, value, VALIDATION_LENGTH, minimum=min_len, maximum=max_len)

	return result

def validate_mparts_value_with_default (request: int, value: str, default: Any) -> Any:
	"""Returns a value part, or a default when it is missing or not utf-8.

	Args:
		request: The request.
		value: The name of the part.
		default: The value of a missing part.

	Returns:
		The value or the default.
	"""
	decoded = validation_decode (mparts_value (request, value))
	return default if (decoded is None) else decoded

def mparts_cast (request: int, value: str, cast: Callable [[str], Any], errors: dict | None, default: Any) -> Any:
	"""Converts a value part, setting its errors when errors is a dict."""
	result = default

	found = mparts_value (request, value)
	if (found is None):
		if (errors is not None):
			validation_error (errors, value, VALIDATION_REQUIRED)

	else:
		# a value that is not utf-8 is invalid like a value that is not a number
		try:
			result = cast (found.decode ("utf-8"))

		except (ValueError, TypeError):
			if (errors is not None):
				validation_error (errors, value, VALIDATION_INVALID)

	return result

def mparts_bool (text: str) -> bool:
	"""Returns the bool of a truth value."""
	return bool (strtobool (text))

def mparts_checked (request: int, value: str, cast, validation: Callable, errors: dict) -> Any:
	"""Converts a required value part and checks it."""
	result = None

	actual_value = mparts_cast (request, value, cast, errors, None)
	if (actual_value is not None):
		if (validation (actual_value)):
			result = actual_value

		else:
			validation_error (errors, value, VALIDATION_FAILED)

	return result

def validate_mparts_int (request: int, value: str, errors: dict) -> int | None:
	"""Returns a required integer value part.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The integer, None on error.
	"""
	return mparts_cast (request, value, int, errors, None)

def validate_mparts_int_value (
	request: int, value: str, validation: Callable [[int], bool], errors: dict
) -> int | None:
	"""Returns a required integer value part that passes a check.

	Args:
		request: The request.
		value: The name of the part.
		validation: Returns True for a valid integer.
		errors: The errors of the request.

	Returns:
		The integer, None on error.
	"""
	return mparts_checked (request, value, int, validation, errors)

def validate_mparts_int_with_default (request: int, value: str, default: int) -> int:
	"""Returns an integer value part, or a default when it is missing or invalid.

	Args:
		request: The request.
		value: The name of the part.
		default: The value of a missing or invalid part.

	Returns:
		The integer or the default.
	"""
	return mparts_cast (request, value, int, None, default)

def validate_mparts_float (request: int, value: str, errors: dict) -> float | None:
	"""Returns a required number value part.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The number, None on error.
	"""
	return mparts_cast (request, value, float, errors, None)

def validate_mparts_float_value (
	request: int, value: str, validation: Callable [[float], bool], errors: dict
) -> float | None:
	"""Returns a required number value part that passes a check.

	Args:
		request: The request.
		value: The name of the part.
		validation: Returns True for a valid number.
		errors: The errors of the request.

	Returns:
		The number, None on error.
	"""
	return mparts_checked (request, value, float, validation, errors)

def validate_mparts_float_with_default (request: int, value: str, default: float) -> float:
	"""Returns a number value part, or a default when it is missing or invalid.

	Args:
		request: The request.
		value: The name of the part.
		default: The value of a missing or invalid part.

	Returns:
		The number or the default.
	"""
	return mparts_cast (request, value, float, None, default)

def validate_mparts_bool (request: int, value: str, errors: dict) -> bool | None:
	"""Returns a required truth value part (see strtobool ()).

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The bool, None on error.
	"""
	return mparts_cast (request, value, mparts_bool, errors, None)

def validate_mparts_bool_with_default (request: int, value: str, default: bool) -> bool:
	"""Returns a truth value part, or a default when it is missing or invalid.

	Args:
		request: The request.
		value: The name of the part.
		default: The value of a missing or invalid part.

	Returns:
		The bool or the default.
	"""
	return mparts_cast (request, value, mparts_bool, None, default)

def validate_mparts_file (request: int, value: str, errors: dict) -> dict | None:
	"""Returns the filenames of a required file part.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The filenames (see http_multi_part_get_file ()), None on error.
	"""
	values = None

	mpart = http_request_multi_parts_get (request, lib_c_string (value))
	if (mpart):
		values = http_multi_part_get_file (mpart)
		if (not values):
			values = None
			validation_error (errors, value, VALIDATION_NOT_FILE)

	else:
		validation_error (errors, value, VALIDATION_FILE_MISSING)

	return values

def validate_mparts_optional_file (request: int, value: str) -> dict | None:
	"""Returns the filenames of a file part, None when it is missing.

	Args:
		request: The request.
		value: The name of the part.

	Returns:
		The filenames, empty for a part that is not a file, None if it is missing.
	"""
	values = None

	mpart = http_request_multi_parts_get (request, lib_c_string (value))
	if (mpart):
		values = http_multi_part_get_file (mpart)

	return values

def validate_mparts_file_exists (request: int, value: str, errors: dict) -> dict | None:
	"""Returns the filenames of a required file part whose saved file exists.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request, a file that was not saved, or that is gone, is missing.

	Returns:
		The filenames, None on error.
	"""
	values = None

	mpart = http_request_multi_parts_get (request, lib_c_string (value))
	if (not mpart):
		validation_error (errors, value, VALIDATION_FILE_MISSING)

	elif (not http_multi_part_is_file (mpart)):
		validation_error (errors, value, VALIDATION_NOT_FILE)

	else:
		saved = http_multi_part_get_saved_filename (mpart)
		if (saved and file_exists (saved)):
			values = http_multi_part_get_file (mpart)

		else:
			validation_error (errors, value, VALIDATION_FILE_MISSING)

	return values

def mparts_filename (filename: bytes | None, value: str, errors: dict) -> str | None:
	"""Returns a filename as text, setting the missing error when there is none."""
	result = validation_decode (filename) if (filename) else None

	if (result is None):
		validation_error (errors, value, VALIDATION_FILE_MISSING)

	return result

def validate_mparts_filename_exists (request: int, value: str, errors: dict) -> str | None:
	"""Returns the original filename of a required file part.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The filename, None on error.
	"""
	return mparts_filename (
		http_request_multi_parts_get_filename (request, lib_c_string (value)), value, errors
	)

def validate_mparts_saved_filename_exists (request: int, value: str, errors: dict) -> str | None:
	"""Returns the saved filename of a required file part.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The path, None on error.
	"""
	return mparts_filename (
		http_request_multi_parts_get_saved_filename (request, lib_c_string (value)), value, errors
	)

def validate_mparts_saved_file_exists (request: int, value: str, errors: dict) -> str | None:
	"""Returns the saved filename of a required file part whose file exists.

	Args:
		request: The request.
		value: The name of the part.
		errors: The errors of the request.

	Returns:
		The path, None on error.
	"""
	filename = http_request_multi_parts_get_saved_filename (request, lib_c_string (value))
	existing = filename if (filename and file_exists (filename)) else None

	return mparts_filename (existing, value, errors)
