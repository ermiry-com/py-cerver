import distutils.util

from ..files import file_exists
from ..files import IMAGE_TYPE_PNG, IMAGE_TYPE_JPEG
from ..files import files_image_get_type

from .multipart import http_multi_part_is_file
from .multipart import http_multi_part_get_filename
from .multipart import http_multi_part_get_generated_filename
from .multipart import http_multi_part_get_saved_filename
from .request import http_request_multi_parts_get
from .request import http_request_multi_parts_get_value
from .request import http_request_multi_parts_get_filename
from .request import http_request_multi_parts_get_saved_filename

def validate_body_required_keys (values, body):
	if not all (k in body for k in values):
		raise Exception ("Missing key(s) in body")

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

def validate_body_value_with_default (body, value, default, errors):
	result = default

	if (value in body):
		result = body[value]

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

def validate_mparts_value_with_default (request, value, default, errors):
	result = default

	found = http_request_multi_parts_get_value (request, value.encode ("utf-8"))
	if (found):
		result = found.decode ("utf-8")

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

def validate_mparts_file_exists (request, value, errors):
	values = None

	mpart = http_request_multi_parts_get (request, value.encode ("utf-8"))
	if (mpart):
		if (http_multi_part_is_file (mpart)):
			saved = http_multi_part_get_saved_filename (mpart)
			if (file_exists (saved)):
				values = {}
				original = http_multi_part_get_filename (mpart)
				values["original"] = original.decode ("utf-8")
				generated = http_multi_part_get_generated_filename (mpart)
				if (generated):
					values["generated"] = generated.decode ("utf-8")

				values["saved"] = saved.decode ("utf-8")

		else:
			errors[value] = f"Field {value} is not a file."

	else:
		errors[value] = f"File {value} is missing."

	return values

def validate_mparts_filename_exists (request, value, errors):
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

def validate_mparts_saved_filename_exists (request, value, errors):
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

def validate_mparts_saved_file_exists (request, value, errors):
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

def validate_mparts_file_is_image (request, image, errors):
	values = None
	
	mpart = http_request_multi_parts_get (request, image.encode ("utf-8"))
	if (mpart):
		if (http_multi_part_is_file (mpart)):
			saved = http_multi_part_get_saved_filename (mpart)

			# validate file and get extension
			img_type = files_image_get_type (saved)
			if (img_type == IMAGE_TYPE_PNG or img_type == IMAGE_TYPE_JPEG):
				values = {}
				values["type"] = img_type
				original = http_multi_part_get_filename (mpart)
				values["original"] = original.decode ("utf-8")
				generated = http_multi_part_get_generated_filename (mpart)
				if (generated):
					values["generated"] = generated.decode ("utf-8")
				
				values["saved"] = saved.decode ("utf-8")

			else:
				errors[image] = f"File {image} is not png or jpeg."

		else:
			errors[image] = f"Field {image} is not a file."

	else:
		errors[image] = f"File {image} is missing."

	return values
