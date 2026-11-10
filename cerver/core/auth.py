"""The authentication of the connections of a cerver."""

from ctypes import POINTER, Structure
from ctypes import c_int, c_char_p, c_void_p, c_size_t
from typing import TypeAlias

from ..lib import lib_function

from ..types.string import StringPointer

__all__ = [
	"CerverAuthError",
	"CERVER_AUTH_ERROR_NONE", "CERVER_AUTH_ERROR_SUCCESS", "CERVER_AUTH_ERROR_NO_HANDLER",
	"CERVER_AUTH_ERROR_MISSING_VALUES", "CERVER_AUTH_ERROR_FAILED",
	"CERVER_AUTH_ERROR_INVALID_SESSION", "CERVER_AUTH_ERROR_DROPPED",
	"AuthData", "AuthDataPointer", "AuthMethod", "AuthMethodPointer",
	"cerver_auth_error_to_string", "cerver_auth_error_description"
]

CerverAuthError: TypeAlias = c_int # type: ignore

CERVER_AUTH_ERROR_NONE = 0
CERVER_AUTH_ERROR_SUCCESS = 1
CERVER_AUTH_ERROR_NO_HANDLER = 2
CERVER_AUTH_ERROR_MISSING_VALUES = 3
CERVER_AUTH_ERROR_FAILED = 4
CERVER_AUTH_ERROR_INVALID_SESSION = 5
CERVER_AUTH_ERROR_DROPPED = 6

class AuthData (Structure):
	"""The auth data of an auth packet, ``AuthData``.

	Attributes:
		token: The session token, a StringPointer.
		auth_data: The credentials.
		auth_data_size: The size of the credentials.
		data: The data that the authenticate method keeps for the client.
		delete_data: How the data is released.
	"""

	_fields_ = [
		("token", StringPointer),

		("auth_data", c_void_p),
		("auth_data_size", c_size_t),

		("data", c_void_p),
		("delete_data", c_void_p)
	]

AuthDataPointer: TypeAlias = POINTER (AuthData) # type: ignore

class AuthMethod (Structure):
	"""What the authenticate method of a cerver gets, ``AuthMethod``.

	Attributes:
		packet: The auth packet.
		auth_data: The auth data of the packet.
		error_message: A StringPointer that the method can set to send it with the failed auth.
	"""

	_fields_ = [
		("packet", c_void_p),
		("auth_data", AuthDataPointer),
		("error_message", StringPointer)
	]

AuthMethodPointer: TypeAlias = POINTER (AuthMethod) # type: ignore

cerver_auth_error_to_string = lib_function (
	"cerver_auth_error_to_string", [CerverAuthError], c_char_p,
	"""Returns the name of an authentication error.

	Args:
		error: A CERVER_AUTH_ERROR_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_auth_error_description = lib_function (
	"cerver_auth_error_description", [CerverAuthError], c_char_p,
	"""Returns the description of an authentication error.

	Args:
		error: A CERVER_AUTH_ERROR_* value.

	Returns:
		The description, as bytes.
	"""
)
