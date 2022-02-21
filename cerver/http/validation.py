from ctypes import c_void_p
from typing import Any, Callable

import distutils.util

from ..files import file_exists
from ..files import IMAGE_TYPE_NONE, IMAGE_TYPE_PNG, IMAGE_TYPE_JPEG
from ..files import files_image_get_type

from .multipart import http_multi_part_is_file
from .multipart import http_multi_part_get_filename
from .multipart import http_multi_part_get_generated_filename
from .multipart import http_multi_part_get_saved_filename
from .multipart import http_multi_part_get_file
from .request import http_query_pairs_get_value
from .request import http_request_multi_parts_get
from .request import http_request_multi_parts_get_value
from .request import http_request_multi_parts_get_filename
from .request import http_request_multi_parts_get_saved_filename

def validate_query_exists_internal (
	values: c_void_p, query_name: str
) -> str:
	result = None

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		query_value = found.contents.str.decode ("utf-8")
		if (len (query_value) > 0):
			result = query_value

	return result

def validate_query_exists (
	values: c_void_p, query_name: str, errors: dict
) -> str:
	result = validate_query_exists_internal (values, query_name)

	if (result is None):
		errors[query_name] = f"Field {query_name} is required."

	return result

def validate_query_value (
	values: c_void_p, query_name: str, min_len: int, max_len: int, errors: dict
) -> str:
	result = None

	found = validate_query_exists (values, query_name, errors)
	if (found):
		value_len = len (found)
		if ((value_len >= min_len) and (value_len <= max_len)):
			result = found

		else:
			errors[query_name] = (
				"Field {0} must be between {1} and {2} characters long."
				.format	(query_name, min_len, max_len)
			)

	return result

def validate_query_value_with_default (
	values: c_void_p, query_name: str, default: str
):
	result = validate_query_exists_internal (values, query_name)

	if (result is None):
		result = default

	return result

def validate_query_int_value (
	values: c_void_p, query_name: str, errors: dict
) -> int:
	result = None

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		try:
			result = int (found.contents.str.decode ("utf-8"))
		except ValueError:
			errors[query_name] = f"Field {query_name} is invalid."

	else:
		errors[query_name] = f"Field {query_name} is required."

	return result

def validate_query_int_value_with_default (
	values: c_void_p, query_name: str, default: int
) -> int:
	result = default

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		try:
			result = int (found.contents.str.decode ("utf-8"))
		except ValueError:
			pass

	return result

def validate_query_float_value (
	values: c_void_p, query_name: str, errors: dict
) -> float:
	result = None

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		try:
			result = float (found.contents.str.decode ("utf-8"))
		except ValueError:
			errors[query_name] = f"Field {query_name} is invalid."

	else:
		errors[query_name] = f"Field {query_name} is required."

	return result

def validate_query_float_value_with_default (
	values: c_void_p, query_name: str, default: float
) -> float:
	result = default

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		try:
			result = float (found.contents.str.decode ("utf-8"))
		except ValueError:
			pass

	return result

def validate_query_bool_value (
	values: c_void_p, query_name: str, errors: dict
) -> bool:
	result = None

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		try:
			result = bool (
				distutils.util.strtobool (found.contents.str.decode ("utf-8"))
			)
		except ValueError:
			errors[query_name] = f"Field {query_name} is invalid."

	else:
		errors[query_name] = f"Field {query_name} is required."

	return result

def validate_query_bool_value_with_default (
	values: c_void_p, query_name: str, default: bool
) -> bool:
	result = default

	found = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	if (found):
		try:
			result = bool (
				distutils.util.strtobool (found.contents.str.decode ("utf-8"))
			)
		except ValueError:
			pass

	return result

def validate_body_required_keys (values, body):
	if not all (k in body for k in values):
		raise Exception ("Missing key(s) in body")

def validate_body_value_exists (body: dict, value: str, errors: dict):
	result = None

	if (value in body):
		if (type (body[value]) is str):
			if (len (body[value]) > 0):
				result = body[value]

		else:
			result = body[value]

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_body_string_value_exists_ignore_size (
	body: dict, value: str, errors: dict
):
	result = None

	if (value in body):
		if (type (body[value]) is str):
			result = body[value]

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_body_value (
	body: dict, value: str, min_len: int, max_len: int, errors: dict
):
	result = None

	found = validate_body_value_exists (body, value, errors)
	if (found):
		value_len = len (found)
		if ((value_len >= min_len) and (value_len <= max_len)):
			result = found

		else:
			errors[value] = (
				"Field {0} must be between {1} and {2} characters long."
				.format	(value, min_len, max_len)
			)

	return result

def validate_body_int_value_exists (
	body: dict, value: str, errors: dict
) -> int:
	result = None

	if (value in body):
		if (type (body[value]) == int):
			result = body[value]

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_body_float_value_exists (
	body: dict, value: str, errors: dict
) -> float:
	result = None

	if (value in body):
		if (type (body[value]) == float):
			result = body[value]

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_body_value_with_default (body: dict, value: str, default: dict):
	result = default

	if (value in body):
		result = body[value]

	return result

def validate_mparts_exists (request: c_void_p, value: str, errors: dict):
	result = None

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		if (len (found) > 0):
			result = found

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_mparts_value (
	request: c_void_p, value: str, min_len: int, max_len: int, errors: dict
):
	result = None

	found = validate_mparts_exists (request, value, errors)
	if (found):
		value_len = len (found)
		if ((value_len >= min_len) and (value_len <= max_len)):
			result = found

		else:
			errors[value] = (
				"Field {0} must be between {1} and {2} characters long."
				.format	(value, min_len, max_len)
			)

	return result

def validate_mparts_value_with_default (
	request: c_void_p, value: str, default: str
):
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		result = found.decode ("utf-8")

	return result

def validate_mparts_int (request: c_void_p, value: str, errors: dict) -> int:
	result = None

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = int (found)
		except ValueError:
			errors[value] = f"Field {value} is invalid."

	else:
		errors[value] = f"Field {value} is required."

	return result

def validate_mparts_int_value (
	request: c_void_p, value: str,
	validation: Callable [[int], bool], errors: dict
) -> int:
	result = None

	actual_value = validate_mparts_int (request, value, errors)
	if (actual_value is not None):
		if (validation (actual_value)):
			result = actual_value

		else:
			errors[value] = f"Failed to validate field {value}."

	return result

def validate_mparts_int_with_default (
	request: c_void_p, value: str, default: int
) -> int:
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = int (found)
		except ValueError:
			pass

	return result

def validate_mparts_float (
	request: c_void_p, value: str, errors: dict
) -> float:
	result = None

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = float (found)
		except ValueError:
			errors[value] = f"Field {value} is invalid."

	else:
		errors[value] = f"Field {value} is required."

	return result

def validate_mparts_float_value (
	request: c_void_p, value: str,
	validation: Callable [[float], bool], errors: dict
):
	result = None

	actual_value = validate_mparts_float (request, value, errors)
	if (actual_value is not None):
		if (validation (actual_value)):
			result = actual_value

		else:
			errors[value] = f"Failed to validate field {value}."

	return result

def validate_mparts_float_with_default (
	request: c_void_p, value: str, default: float
) -> float:
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = float (found)
		except ValueError:
			pass

	return result

def validate_mparts_bool (
	request: c_void_p, value: str, errors: dict
) -> bool:
	result = None

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = bool (distutils.util.strtobool (found))
		except ValueError:
			errors[value] = f"Field {value} is invalid."

	else:
		errors[value] = f"Field {value} is required."

	return result

def validate_mparts_bool_with_default (
	request: c_void_p, value: str, default: bool
) -> bool:
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = bool (distutils.util.strtobool (found))
		except ValueError:
			pass

	return result

def validate_mparts_file_exists (
	request: c_void_p, value: str, errors: dict
) -> dict:
	values = None

	mpart = http_request_multi_parts_get (request, value.encode ("utf-8"))
	if (mpart):
		if (http_multi_part_is_file (mpart)):
			saved = http_multi_part_get_saved_filename (mpart)
			if (file_exists (saved)):
				values = http_multi_part_get_file (mpart)

		else:
			errors[value] = f"Field {value} is not a file."

	else:
		errors[value] = f"File {value} is missing."

	return values

def validate_mparts_filename_exists (
	request: c_void_p, value: str, errors: dict
) -> str:
	result = None

	# get the value filename
	filename = http_request_multi_parts_get_filename (
		request, value.encode ("utf-8")
	)

	if (filename):
		result = filename.decode ("utf-8")

	else:
		errors[value] = f"File {value} is missing."

	return result

def validate_mparts_saved_filename_exists (
	request: c_void_p, value: str, errors: dict
) -> str:
	result = None

	# get the value filename
	filename = http_request_multi_parts_get_saved_filename (
		request, value.encode ("utf-8")
	)

	if (filename):
		result = filename.decode ("utf-8")

	else:
		errors[value] = f"File {value} is missing."

	return result

def validate_mparts_saved_file_exists (
	request: c_void_p, value: str, errors: dict
) -> str:
	result = None

	# get the value filename
	filename = http_request_multi_parts_get_saved_filename (
		request, value.encode ("utf-8")
	)

	if (filename):
		if (file_exists (filename)):
			result = filename.decode ("utf-8")

	if (result is None):
		errors[value] = f"File {value} is missing."

	return result

def validate_mparts_file_complete (
	request: c_void_p, value: str, errors: dict
) -> dict:
	values = None

	mpart = http_request_multi_parts_get (request, value.encode ("utf-8"))
	if (mpart):
		values = http_multi_part_get_file (mpart)
		if (not values):
			errors[value] = f"Field {value} is not a file."

	else:
		errors[value] = f"File {value} is missing."

	return values

def validate_file_is_image (
	filename: Any, field: str, errors: dict
) -> int:
	result = IMAGE_TYPE_NONE

	if (type (filename) == str):
		filename = filename.encode ("utf-8")

	img_type = files_image_get_type (filename)
	if ((img_type == IMAGE_TYPE_PNG) or (img_type == IMAGE_TYPE_JPEG)):
		result = img_type

	else:
		errors[field] = f"File {field} is not png or jpeg."

	return result

def validate_mparts_file_is_image (
	request: c_void_p, image: str, errors: dict
) -> dict:
	values = None

	mpart = http_request_multi_parts_get (request, image.encode ("utf-8"))
	if (mpart):
		if (http_multi_part_is_file (mpart)):
			saved = http_multi_part_get_saved_filename (mpart)

			# validate file and get extension
			img_type = validate_file_is_image (saved, image, errors)
			if (img_type):
				values = http_multi_part_get_file (mpart)
				values["type"] = img_type

			else:
				errors[image] = f"File {image} is not png or jpeg."

		else:
			errors[image] = f"Field {image} is not a file."

	else:
		errors[image] = f"File {image} is missing."

	return values

def validate_mparts_optional_file_is_image (
	request: c_void_p, image: str, errors: dict
) -> dict:
	values = {}

	mpart = http_request_multi_parts_get (request, image.encode ("utf-8"))
	if (mpart):
		if (http_multi_part_is_file (mpart)):
			saved = http_multi_part_get_saved_filename (mpart)

			# validate file and get extension
			img_type = validate_file_is_image (saved, image, errors)
			if (img_type):
				values = http_multi_part_get_file (mpart)
				values["type"] = img_type

	return values
