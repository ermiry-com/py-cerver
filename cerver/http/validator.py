"""The validators of the params of a route, like ":id<objectid>"."""

from ctypes import CFUNCTYPE, c_bool, c_char_p, c_size_t, c_void_p, string_at
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"HttpParamValidate",
	"HTTP_PARAM_VALIDATOR_OBJECTID", "HTTP_PARAM_VALIDATOR_INT", "HTTP_PARAM_VALIDATOR_UUID",
	"http_param_value",
	"http_param_validator_builtin",
	"http_param_validate_objectid", "http_param_validate_int", "http_param_validate_uuid"
]

# returns true if the raw value of a route param is valid,
# the value is a slice of the url: it is not percent-decoded nor terminated with '\0',
# so it is read with http_param_value (value, length)
HttpParamValidate: TypeAlias = CFUNCTYPE (c_bool, c_void_p, c_size_t) # type: ignore

HTTP_PARAM_VALIDATOR_OBJECTID = "objectid"
HTTP_PARAM_VALIDATOR_INT = "int"
HTTP_PARAM_VALIDATOR_UUID = "uuid"

def http_param_value (value: int, length: int) -> bytes:
	"""Returns the bytes of the raw value that a HttpParamValidate gets.

	Args:
		value: The address of the value.
		length: Its length.

	Returns:
		The bytes of the value.
	"""
	return string_at (value, length)

http_param_validator_builtin = lib_function (
	"http_param_validator_builtin", [c_char_p, c_size_t], c_void_p,
	"""Returns a built-in validator by its name.

	Args:
		name: The name, as bytes, like b"objectid".
		length: The length of the name.

	Returns:
		The HttpParamValidator, None if there is none with that name.
	"""
)

http_param_validate_objectid = lib_function (
	"http_param_validate_objectid", [c_char_p, c_size_t], c_bool,
	"""Returns if a value is a Mongo ObjectId (24 hexadecimal characters).

	Args:
		value: The value, as bytes.
		length: Its length.

	Returns:
		True if it is valid.
	"""
)

http_param_validate_int = lib_function (
	"http_param_validate_int", [c_char_p, c_size_t], c_bool,
	"""Returns if a value is an integer (an optional '-' and digits).

	Args:
		value: The value, as bytes.
		length: Its length.

	Returns:
		True if it is valid.
	"""
)

http_param_validate_uuid = lib_function (
	"http_param_validate_uuid", [c_char_p, c_size_t], c_bool,
	"""Returns if a value is a UUID (8-4-4-4-12 hexadecimal characters).

	Args:
		value: The value, as bytes.
		length: Its length.

	Returns:
		True if it is valid.
	"""
)
