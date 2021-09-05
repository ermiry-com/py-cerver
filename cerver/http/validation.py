import distutils.util

from ..files import IMAGE_TYPE_PNG, IMAGE_TYPE_JPEG, files_image_get_type

from .request import http_request_multi_parts_get_value
from .request import http_request_multi_parts_get_saved_filename

def validate_body_value_exists (body, value, errors):
	result = None

	if (value in body):
		if (len (body[value]) > 0):
			result = body[value]

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_body_value (body, value, min_len, max_len, errors):
	result = None

	found = validate_body_value_exists (body, value, errors)
	if (found):
		value_len = len (found)
		if (value_len >= min_len and value_len <= max_len):
			result = found

		else:
			errors[value] = (
				"Field {0} must be between {1} and {2} characters long."
				.format	(value, min_len, max_len)
			)

	return result

def validate_mparts_exists (request, value, errors):
	result = None

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		if (len (found) > 0):
			result = found

	if (result is None):
		errors[value] = f"Field {value} is required."

	return result

def validate_mparts_value (request, value, min_len, max_len, errors):
	result = None

	found = validate_mparts_exists (request, value, errors)
	if (found):
		value_len = len (found)
		if (value_len >= min_len and value_len <= max_len):
			result = found

		else:
			errors[value] = (
				"Field {0} must be between {1} and {2} characters long."
				.format	(value, min_len, max_len)
			)

	return result

def validate_mparts_int (request, value, errors):
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

def validate_mparts_int_with_default (
	request, value, default, errors
):
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = int (found)
		except ValueError:
			pass

	return result

def validate_mparts_float (request, value, errors):
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

def validate_mparts_float_with_default (
	request, value, default, errors
):
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = float (found)
		except ValueError:
			pass

	return result

def validate_mparts_bool (request, value, errors):
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
	request, value, default, errors
):
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		found = found.decode ("utf-8")
		try:
			result = bool (distutils.util.strtobool (found))
		except ValueError:
			pass

	return result

def validate_mparts_file_is_image (request, image, errors):
	result = False
	img_type = None

	# get the image filename
	filename = http_request_multi_parts_get_saved_filename (
		request, image.encode ("utf-8")
	)

	if (filename):
		# validate file and get extension
		img_type = files_image_get_type (filename)
		if (img_type == IMAGE_TYPE_PNG or img_type == IMAGE_TYPE_JPEG):
			result = True

		else:
			errors[image] = f"File {image} is not png or jpeg."

	else:
		errors[image] = f"File {image} is missing."

	return result, img_type, filename
