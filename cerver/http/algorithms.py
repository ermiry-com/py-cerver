"""The algorithms of the JWTs of an HTTP cerver."""

from ctypes import c_int, c_char_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"JwtAlgorithm",
	"JWT_ALG_NONE", "JWT_ALG_HS256", "JWT_ALG_HS384", "JWT_ALG_HS512",
	"JWT_ALG_RS256", "JWT_ALG_RS384", "JWT_ALG_RS512",
	"JWT_ALG_ES256", "JWT_ALG_ES384", "JWT_ALG_ES512", "JWT_ALG_TERM",
	"JWT_ALG_INVAL", "JWT_DEFAULT_ALG",
	"jwt_alg_str", "jwt_str_alg"
]

JwtAlgorithm: TypeAlias = c_int # type: ignore

JWT_ALG_NONE = 0
JWT_ALG_HS256 = 1
JWT_ALG_HS384 = 2
JWT_ALG_HS512 = 3
JWT_ALG_RS256 = 4
JWT_ALG_RS384 = 5
JWT_ALG_RS512 = 6
JWT_ALG_ES256 = 7
JWT_ALG_ES384 = 8
JWT_ALG_ES512 = 9
JWT_ALG_TERM = 10

JWT_ALG_INVAL = JWT_ALG_TERM
JWT_DEFAULT_ALG = JWT_ALG_HS256

jwt_alg_str = lib_function (
	"jwt_alg_str", [JwtAlgorithm], c_char_p,
	"""Returns the name of an algorithm.

	Args:
		alg: A JWT_ALG_* value.

	Returns:
		The name, as bytes, like b"RS256", None for an invalid one.
	"""
)

jwt_str_alg = lib_function (
	"jwt_str_alg", [c_char_p], JwtAlgorithm,
	"""Returns the algorithm of a name.

	Args:
		alg: The name, as bytes, like b"RS256".

	Returns:
		A JWT_ALG_* value, JWT_ALG_INVAL if it is unknown.
	"""
)
