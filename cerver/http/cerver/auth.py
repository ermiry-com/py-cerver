"""The JWTs of an HTTP cerver: its keys, the creation of tokens and their validation."""

import json

from ctypes import POINTER, byref, cast, string_at
from ctypes import c_void_p, c_char_p, c_bool, c_int, c_size_t, c_uint8

from ...lib import lib_function, lib_take_c_string, lib_c_string, lib_text, libc_free

from ..algorithms import JwtAlgorithm, JWT_ALG_NONE
from ..requests.getters import http_request_get_decoded_data
from ..responses.json import http_response_json_custom_reference_send
from ..status import HTTP_STATUS_OK

from .receive import http_receive_get_cerver

__all__ = [
	"HTTP_JWT_TOKEN_SIZE",
	"http_jwt_get_bearer", "http_jwt_get_bearer_len", "http_jwt_get_json", "http_jwt_get_json_len",
	"http_cerver_auth_load_key_c_string", "http_cerver_auth_load_key",
	"http_cerver_auth_set_jwt_algorithm",
	"http_cerver_auth_set_jwt_priv_key_filename", "http_cerver_auth_set_jwt_pub_key_filename",
	"http_cerver_auth_jwt_new", "http_cerver_auth_jwt_delete",
	"http_cerver_auth_jwt_add_value", "http_cerver_auth_jwt_add_value_bool",
	"http_cerver_auth_jwt_add_value_int",
	"http_cerver_auth_generate_jwt_c_string", "http_cerver_auth_generate_jwt",
	"http_cerver_auth_generate_bearer_jwt", "http_cerver_auth_generate_bearer_jwt_json",
	"http_cerver_auth_generate_bearer_jwt_json_with_value",
	"http_cerver_auth_validate_jwt",
	"http_cerver_auth_configuration", "http_jwt_create", "http_jwt_create_and_send",
	"http_jwt_get_bearer_string", "http_jwt_token_decode"
]

# the size of the bearer and of the json of an HttpJwt
HTTP_JWT_TOKEN_SIZE = 4096

TEXT_ENCODING = "utf-8"

http_jwt_get_bearer = lib_function (
	"http_jwt_get_bearer", [c_void_p], c_char_p,
	"""Returns the bearer token ("Bearer <jwt>") of a generated JWT.

	Args:
		http_jwt: The HttpJwt.

	Returns:
		The bearer, as bytes.
	"""
)

http_jwt_get_bearer_len = lib_function (
	"http_jwt_get_bearer_len", [c_void_p], c_size_t,
	"""Returns the length of the bearer token of a generated JWT.

	Args:
		http_jwt: The HttpJwt.

	Returns:
		The length.
	"""
)

http_jwt_get_json = lib_function (
	"http_jwt_get_json", [c_void_p], c_char_p,
	"""Returns the JSON {"token": "Bearer <jwt>"} of a generated JWT.

	Args:
		http_jwt: The HttpJwt.

	Returns:
		The JSON, as bytes.
	"""
)

http_jwt_get_json_len = lib_function (
	"http_jwt_get_json_len", [c_void_p], c_size_t,
	"""Returns the length of the JSON of a generated JWT.

	Args:
		http_jwt: The HttpJwt.

	Returns:
		The length.
	"""
)

http_cerver_auth_load_key_c_string = lib_function (
	"http_cerver_auth_load_key", [c_char_p, POINTER (c_size_t)], c_void_p,
	"""Loads the contents of a key file into a new buffer, use http_cerver_auth_load_key ().

	Args:
		filename: The path, as bytes.
		keylen: A pointer to a c_size_t that gets the length.

	Returns:
		The address of the buffer that the caller frees, None on error.
	"""
)

def http_cerver_auth_load_key (filename: str | bytes) -> bytes | None:
	"""Loads the contents of a key file.

	Args:
		filename: The path.

	Returns:
		The key, None on error.
	"""
	result = None

	length = c_size_t (0)
	pointer = http_cerver_auth_load_key_c_string (lib_c_string (filename), byref (length))
	if (pointer):
		result = string_at (pointer, length.value)
		libc_free (pointer)

	return result

http_cerver_auth_set_jwt_algorithm = lib_function (
	"http_cerver_auth_set_jwt_algorithm", [c_void_p, JwtAlgorithm], None,
	"""Sets the algorithm that signs and validates the JWTs.

	Args:
		http_cerver: The HttpCerver.
		jwt_alg: A JWT_ALG_* value, JWT_ALG_HS256 by default.
	"""
)

http_cerver_auth_set_jwt_priv_key_filename = lib_function (
	"http_cerver_auth_set_jwt_priv_key_filename", [c_void_p, c_char_p], None,
	"""Sets the file of the private key that signs the JWTs, loaded when the cerver starts.

	Args:
		http_cerver: The HttpCerver.
		filename: The path, as bytes.
	"""
)

http_cerver_auth_set_jwt_pub_key_filename = lib_function (
	"http_cerver_auth_set_jwt_pub_key_filename", [c_void_p, c_char_p], None,
	"""Sets the file of the public key that validates the JWTs, loaded when the cerver starts.

	Args:
		http_cerver: The HttpCerver.
		filename: The path, as bytes.
	"""
)

http_cerver_auth_jwt_new = lib_function (
	"http_cerver_auth_jwt_new", [], c_void_p,
	"""Creates an empty JWT.

	Returns:
		The HttpJwt, released with http_cerver_auth_jwt_delete ().
	"""
)

http_cerver_auth_jwt_delete = lib_function (
	"http_cerver_auth_jwt_delete", [c_void_p], None,
	"""Releases a JWT.

	Args:
		http_jwt: The HttpJwt.
	"""
)

http_cerver_auth_jwt_add_value = lib_function (
	"http_cerver_auth_jwt_add_value", [c_void_p, c_char_p, c_char_p], None,
	"""Adds a text value to a JWT.

	Args:
		http_jwt: The HttpJwt.
		key: The key, as bytes.
		value: The value, as bytes.
	"""
)

http_cerver_auth_jwt_add_value_bool = lib_function (
	"http_cerver_auth_jwt_add_value_bool", [c_void_p, c_char_p, c_bool], None,
	"""Adds a bool value to a JWT.

	Args:
		http_jwt: The HttpJwt.
		key: The key, as bytes.
		value: The bool.
	"""
)

http_cerver_auth_jwt_add_value_int = lib_function (
	"http_cerver_auth_jwt_add_value_int", [c_void_p, c_char_p, c_int], None,
	"""Adds an integer value to a JWT.

	Args:
		http_jwt: The HttpJwt.
		key: The key, as bytes.
		value: The integer, of 32 bits.
	"""
)

http_cerver_auth_generate_jwt_c_string = lib_function (
	"http_cerver_auth_generate_jwt", [c_void_p, c_void_p], c_void_p,
	"""Generates a signed token with the values of a JWT in a new C string, use http_cerver_auth_generate_jwt ().

	Args:
		http_cerver: The HttpCerver.
		http_jwt: The HttpJwt.

	Returns:
		The address of the token that the caller frees, None on error.
	"""
)

def http_cerver_auth_generate_jwt (http_cerver: int, http_jwt: int) -> bytes | None:
	"""Generates a signed token with the values of a JWT.

	Args:
		http_cerver: The HttpCerver.
		http_jwt: The HttpJwt.

	Returns:
		The token, None on error.
	"""
	return lib_take_c_string (http_cerver_auth_generate_jwt_c_string (http_cerver, http_jwt))

http_cerver_auth_generate_bearer_jwt = lib_function (
	"http_cerver_auth_generate_bearer_jwt", [c_void_p, c_void_p], c_uint8,
	"""Generates the bearer token of a JWT, read it with http_jwt_get_bearer ().

	Args:
		http_cerver: The HttpCerver.
		http_jwt: The HttpJwt.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_auth_generate_bearer_jwt_json = lib_function (
	"http_cerver_auth_generate_bearer_jwt_json", [c_void_p, c_void_p], c_uint8,
	"""Generates the bearer token of a JWT and its JSON {"token": ...}, read it with http_jwt_get_json ().

	Args:
		http_cerver: The HttpCerver.
		http_jwt: The HttpJwt.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_auth_generate_bearer_jwt_json_with_value = lib_function (
	"http_cerver_auth_generate_bearer_jwt_json_with_value", [c_void_p, c_void_p, c_char_p, c_char_p], c_uint8,
	"""Works like http_cerver_auth_generate_bearer_jwt_json () with another key-value in the JSON.

	Args:
		http_cerver: The HttpCerver.
		http_jwt: The HttpJwt.
		key: The key, as bytes.
		value: The value, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_cerver_auth_validate_jwt = lib_function (
	"http_cerver_auth_validate_jwt", [c_void_p, c_char_p, c_void_p, POINTER (c_void_p)], c_bool,
	"""Validates a bearer token with the public key of the cerver.

	Args:
		http_cerver: The HttpCerver.
		bearer_token: The token, as bytes.
		decode_data: An HttpDecodeData kept by the caller that creates the decoded data, or None.
		decoded_data: A pointer to a c_void_p that gets the decoded data.

	Returns:
		True if the token is valid.
	"""
)

def http_cerver_auth_configuration (
	http_cerver: int, jwt_algorithm: int = JWT_ALG_NONE,
	priv_key_filename: str | None = None, pub_key_filename: str | None = None
) -> None:
	"""Sets the algorithm and the keys of the JWTs of an HTTP cerver.

	Args:
		http_cerver: The HttpCerver.
		jwt_algorithm: A JWT_ALG_* value, the one of the keys.
		priv_key_filename: The file of the private key, to sign tokens.
		pub_key_filename: The file of the public key, to validate tokens.
	"""
	http_cerver_auth_set_jwt_algorithm (http_cerver, jwt_algorithm)
	if (jwt_algorithm != JWT_ALG_NONE):
		if (priv_key_filename):
			http_cerver_auth_set_jwt_priv_key_filename (http_cerver, lib_c_string (priv_key_filename))

		if (pub_key_filename):
			http_cerver_auth_set_jwt_pub_key_filename (http_cerver, lib_c_string (pub_key_filename))

def http_jwt_add (http_jwt: int, key: str, value) -> None:
	"""Adds a Python value to a JWT by its type."""
	actual_key = lib_c_string (key)

	if (isinstance (value, bool)):
		http_cerver_auth_jwt_add_value_bool (http_jwt, actual_key, value)

	elif (isinstance (value, int)):
		http_cerver_auth_jwt_add_value_int (http_jwt, actual_key, value)

	elif (isinstance (value, str)):
		http_cerver_auth_jwt_add_value (http_jwt, actual_key, lib_c_string (value))

	else:
		raise TypeError (f"The value of {key} must be a str, an int or a bool, not {type (value).__name__}")

def http_jwt_create (values: dict | None = None) -> int:
	"""Creates a JWT with values.

	Args:
		values: The values of the token: str, int (32 bits) or bool.

	Returns:
		The HttpJwt, released with http_cerver_auth_jwt_delete ().

	Raises:
		TypeError: If a value has another type, before the JWT is created.
	"""
	actual_values = values or {}

	for key, value in actual_values.items ():
		if (not isinstance (value, (bool, int, str))):
			raise TypeError (f"The value of {key} must be a str, an int or a bool, not {type (value).__name__}")

	http_jwt = http_cerver_auth_jwt_new ()
	for key, value in actual_values.items ():
		http_jwt_add (http_jwt, key, value)

	return http_jwt

def http_jwt_create_and_send (
	http_receive: int, status_code: int = HTTP_STATUS_OK, values: dict | None = None
) -> int:
	"""Creates a bearer JWT and sends its JSON {"token": "Bearer <jwt>"}.

	Args:
		http_receive: The HttpReceive of the request.
		status_code: An HTTP_STATUS_* value.
		values: The values of the token: str, int (32 bits) or bool.

	Returns:
		0 on success, 1 if the token could not be generated or sent.
	"""
	result = 1

	http_jwt = http_jwt_create (values)
	if (not http_cerver_auth_generate_bearer_jwt_json (http_receive_get_cerver (http_receive), http_jwt)):
		result = http_response_json_custom_reference_send (
			http_receive, status_code,
			http_jwt_get_json (http_jwt), http_jwt_get_json_len (http_jwt)
		)

	http_cerver_auth_jwt_delete (http_jwt)

	return result

def http_jwt_get_bearer_string (http_jwt: int) -> str | None:
	"""Returns the bearer token of a generated JWT.

	Args:
		http_jwt: The HttpJwt, after http_cerver_auth_generate_bearer_jwt ().

	Returns:
		The bearer ("Bearer <jwt>"), a copy that outlives the HttpJwt.
	"""
	return lib_text (http_jwt_get_bearer (http_jwt))

def http_jwt_token_decode (request: int) -> dict | None:
	"""Returns the decoded data of a route that decodes its JWT into JSON.

	Args:
		request: The request.

	Returns:
		The values of the token, None when the request has no decoded data or it is not an object.
	"""
	result = None

	decoded = http_request_get_decoded_data (request)
	if (decoded):
		json_string = cast (decoded, c_char_p).value
		if (json_string):
			try:
				loaded = json.loads (json_string)
				if (isinstance (loaded, dict)):
					result = loaded

			except ValueError:
				pass

	return result
