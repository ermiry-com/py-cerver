"""The validators of the uploaded images."""

from typing import Any

from ...core.files import IMAGE_TYPE_NONE, IMAGE_TYPE_PNG, IMAGE_TYPE_JPEG
from ...core.files import files_image_get_type
from ...lib import lib_c_string

from ..multipart import http_multi_part_is_file, http_multi_part_get_saved_filename
from ..multipart import http_multi_part_get_file
from ..requests.multipart import http_request_multi_parts_get

from .common import VALIDATION_FILE_MISSING, VALIDATION_NOT_FILE, VALIDATION_NOT_IMAGE
from .common import validation_error

__all__ = [
	"VALIDATION_IMAGE_TYPES",
	"validate_file_is_image", "validate_mparts_file_is_image", "validate_mparts_optional_file_is_image"
]

# the types of the images that the validators accept
VALIDATION_IMAGE_TYPES = (IMAGE_TYPE_PNG, IMAGE_TYPE_JPEG)

def validate_file_is_image (filename: Any, field: str, errors: dict) -> int:
	"""Returns the type of a png or jpeg file, by its magic bytes.

	Args:
		filename: The path, as str or bytes.
		field: The name of the field of the error.
		errors: The errors of the request.

	Returns:
		IMAGE_TYPE_PNG or IMAGE_TYPE_JPEG, IMAGE_TYPE_NONE on error.
	"""
	result = IMAGE_TYPE_NONE

	# a missing filename is not an image, and NULL never reaches fopen ()
	actual_filename = lib_c_string (filename)
	image_type = files_image_get_type (actual_filename) if (actual_filename) else IMAGE_TYPE_NONE
	if (image_type in VALIDATION_IMAGE_TYPES):
		result = image_type

	else:
		validation_error (errors, field, VALIDATION_NOT_IMAGE)

	return result

def mparts_image (mpart: int, image: str, errors: dict) -> dict | None:
	"""Returns the filenames and the type of a file part that is an image."""
	values = None

	image_type = validate_file_is_image (http_multi_part_get_saved_filename (mpart), image, errors)
	if (image_type):
		values = http_multi_part_get_file (mpart)
		values["type"] = image_type

	return values

def validate_mparts_file_is_image (request: int, image: str, errors: dict) -> dict | None:
	"""Returns the filenames and the type of a required file part that is a png or a jpeg.

	Args:
		request: The request.
		image: The name of the part.
		errors: The errors of the request.

	Returns:
		The filenames with "type", None on error.
	"""
	values = None

	mpart = http_request_multi_parts_get (request, lib_c_string (image))
	if (not mpart):
		validation_error (errors, image, VALIDATION_FILE_MISSING)

	elif (not http_multi_part_is_file (mpart)):
		validation_error (errors, image, VALIDATION_NOT_FILE)

	else:
		values = mparts_image (mpart, image, errors)

	return values

def validate_mparts_optional_file_is_image (request: int, image: str, errors: dict | None = None) -> dict | None:
	"""Returns the filenames and the type of a file part when it is a png or a jpeg.

	An optional image never sets an error.

	Args:
		request: The request.
		image: The name of the part.
		errors: Not used, kept for the callers of the previous versions.

	Returns:
		The filenames with "type", None when it is missing or it is not an image.
	"""
	values = None

	mpart = http_request_multi_parts_get (request, lib_c_string (image))
	if (mpart and http_multi_part_is_file (mpart)):
		values = mparts_image (mpart, image, {})

	return values
