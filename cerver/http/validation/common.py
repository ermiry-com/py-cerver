"""What the validators share: the messages of their errors and the decoding of the values."""

__all__ = [
	"VALIDATION_REQUIRED", "VALIDATION_INVALID", "VALIDATION_LENGTH", "VALIDATION_FAILED",
	"VALIDATION_RANGE", "VALIDATION_CHOICES", "VALIDATION_ITEMS",
	"VALIDATION_FILE_MISSING", "VALIDATION_NOT_FILE", "VALIDATION_NOT_IMAGE",
	"validation_decode", "validation_error"
]

TEXT_ENCODING = "utf-8"

# the messages of the errors, by the name of the field
VALIDATION_REQUIRED = "Field {field} is required."
VALIDATION_INVALID = "Field {field} is invalid."
VALIDATION_LENGTH = "Field {field} must be between {minimum} and {maximum} characters long."
VALIDATION_FAILED = "Failed to validate field {field}."
VALIDATION_RANGE = "Field {field} must be between {minimum} and {maximum}."
VALIDATION_CHOICES = "Field {field} must be one of {choices}."
VALIDATION_ITEMS = "Field {field} must have between {minimum} and {maximum} items."
VALIDATION_FILE_MISSING = "File {field} is missing."
VALIDATION_NOT_FILE = "Field {field} is not a file."
VALIDATION_NOT_IMAGE = "File {field} is not png or jpeg."

def validation_decode (value: bytes | None) -> str | None:
	"""Returns a value of the client as text.

	Args:
		value: The bytes of the value.

	Returns:
		The text, None when it is missing or it is not utf-8.
	"""
	result = None

	if (value is not None):
		try:
			result = value.decode (TEXT_ENCODING)

		except UnicodeDecodeError:
			pass

	return result

def validation_error (errors: dict, field: str, message: str, **values) -> None:
	"""Sets the error of a field.

	Args:
		errors: The errors of the request, by field.
		field: The name of the field.
		message: A VALIDATION_* message.
		**values: The other values of the message.
	"""
	errors[field] = message.format (field=field, **values)
