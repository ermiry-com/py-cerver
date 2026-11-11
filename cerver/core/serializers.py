"""The serializer of cerver: objects encoded by their schema, compatible with CBOR.

The schemas are C structs of libcerver (like ``cerver_summary_schema``), serializer_schema ()
returns the address of one by its name, to pass it to the functions that take a schema.
"""

import ctypes
from ctypes import POINTER
from ctypes import c_char_p, c_int, c_size_t, c_void_p, byref, create_string_buffer
from typing import TypeAlias

from ..lib import lib, lib_function

__all__ = [
	"SerializerType",
	"SERIALIZER_TYPE_NONE", "SERIALIZER_TYPE_BOOL", "SERIALIZER_TYPE_U8", "SERIALIZER_TYPE_U16",
	"SERIALIZER_TYPE_U32", "SERIALIZER_TYPE_U64", "SERIALIZER_TYPE_I8", "SERIALIZER_TYPE_I16",
	"SERIALIZER_TYPE_I32", "SERIALIZER_TYPE_I64", "SERIALIZER_TYPE_F32", "SERIALIZER_TYPE_F64",
	"SERIALIZER_TYPE_ENUM", "SERIALIZER_TYPE_TEXT", "SERIALIZER_TYPE_BYTES",
	"SERIALIZER_TYPE_TEXT_ARENA", "SERIALIZER_TYPE_BYTES_ARENA", "SERIALIZER_TYPE_ARRAY",
	"SERIALIZER_TYPE_OBJECT",
	"SerializerResult",
	"SERIALIZER_RESULT_NONE", "SERIALIZER_RESULT_ARGUMENTS", "SERIALIZER_RESULT_TRUNCATED",
	"SERIALIZER_RESULT_SIZE", "SERIALIZER_RESULT_DEPTH", "SERIALIZER_RESULT_ELEMENTS",
	"SERIALIZER_RESULT_TYPE", "SERIALIZER_RESULT_RANGE", "SERIALIZER_RESULT_LENGTH",
	"SERIALIZER_RESULT_UTF8", "SERIALIZER_RESULT_NUL", "SERIALIZER_RESULT_DUPLICATE",
	"SERIALIZER_RESULT_MISSING", "SERIALIZER_RESULT_VERSION", "SERIALIZER_RESULT_KEY",
	"SERIALIZER_RESULT_UNSUPPORTED", "SERIALIZER_RESULT_ARENA", "SERIALIZER_RESULT_TRAILING",
	"SERIALIZER_RESULT_BUFFER",
	"SERIALIZER_DEFAULT_MAX_SIZE", "SERIALIZER_DEFAULT_MAX_DEPTH", "SERIALIZER_DEFAULT_MAX_ELEMENTS",
	"SERIALIZER_FIELDS_MAX", "SERIALIZER_VERSION_KEY",
	"serializer_type_string", "serializer_result_string",
	"serializer_object_init", "serializer_encoded_size", "serializer_encode", "serializer_decode",
	"serializer_schemas",
	"serializer_schema", "serializer_encode_bytes", "serializer_decode_bytes"
]

SerializerType: TypeAlias = c_int # type: ignore

SERIALIZER_TYPE_NONE = 0
SERIALIZER_TYPE_BOOL = 1
SERIALIZER_TYPE_U8 = 2
SERIALIZER_TYPE_U16 = 3
SERIALIZER_TYPE_U32 = 4
SERIALIZER_TYPE_U64 = 5
SERIALIZER_TYPE_I8 = 6
SERIALIZER_TYPE_I16 = 7
SERIALIZER_TYPE_I32 = 8
SERIALIZER_TYPE_I64 = 9
SERIALIZER_TYPE_F32 = 10
SERIALIZER_TYPE_F64 = 11
SERIALIZER_TYPE_ENUM = 12
SERIALIZER_TYPE_TEXT = 13
SERIALIZER_TYPE_BYTES = 14
SERIALIZER_TYPE_TEXT_ARENA = 15
SERIALIZER_TYPE_BYTES_ARENA = 16
SERIALIZER_TYPE_ARRAY = 17
SERIALIZER_TYPE_OBJECT = 18

SerializerResult: TypeAlias = c_int # type: ignore

SERIALIZER_RESULT_NONE = 0
SERIALIZER_RESULT_ARGUMENTS = 1
SERIALIZER_RESULT_TRUNCATED = 2
SERIALIZER_RESULT_SIZE = 3
SERIALIZER_RESULT_DEPTH = 4
SERIALIZER_RESULT_ELEMENTS = 5
SERIALIZER_RESULT_TYPE = 6
SERIALIZER_RESULT_RANGE = 7
SERIALIZER_RESULT_LENGTH = 8
SERIALIZER_RESULT_UTF8 = 9
SERIALIZER_RESULT_NUL = 10
SERIALIZER_RESULT_DUPLICATE = 11
SERIALIZER_RESULT_MISSING = 12
SERIALIZER_RESULT_VERSION = 13
SERIALIZER_RESULT_KEY = 14
SERIALIZER_RESULT_UNSUPPORTED = 15
SERIALIZER_RESULT_ARENA = 16
SERIALIZER_RESULT_TRAILING = 17
SERIALIZER_RESULT_BUFFER = 18

# the default limits of an object, a schema can lower them
SERIALIZER_DEFAULT_MAX_SIZE = 65536
SERIALIZER_DEFAULT_MAX_DEPTH = 8
SERIALIZER_DEFAULT_MAX_ELEMENTS = 1024

# the fields of a schema, ids go from 1 to this value
SERIALIZER_FIELDS_MAX = 64

# the key of the version of the schema in every object
SERIALIZER_VERSION_KEY = 0

serializer_type_string = lib_function (
	"serializer_type_string", [SerializerType], c_char_p,
	"""Returns the name of a type of the serializer.

	Args:
		type: A SERIALIZER_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

serializer_result_string = lib_function (
	"serializer_result_string", [SerializerResult], c_char_p,
	"""Returns the description of a result of the serializer.

	Args:
		result: A SERIALIZER_RESULT_* value.

	Returns:
		The description, as bytes.
	"""
)

serializer_object_init = lib_function (
	"serializer_object_init", [c_void_p, c_void_p], None,
	"""Sets every field of the object to its default.

	Args:
		schema: The address of the SerializerSchema.
		object: The address of the object.
	"""
)

serializer_encoded_size = lib_function (
	"serializer_encoded_size", [c_void_p, c_void_p], c_size_t,
	"""Returns the number of bytes of the encoded object.

	Args:
		schema: The address of the SerializerSchema.
		object: The address of the object.

	Returns:
		The bytes, 0 if it can not be encoded.
	"""
)

serializer_encode = lib_function (
	"serializer_encode", [c_void_p, c_void_p, c_void_p, c_size_t, POINTER (c_size_t)], SerializerResult,
	"""Encodes the object in the buffer without allocating memory.

	Args:
		schema: The address of the SerializerSchema.
		object: The address of the object.
		buffer: The buffer.
		size: Its size.
		written: A pointer to a c_size_t that gets the bytes of the encoded object, or None.

	Returns:
		A SERIALIZER_RESULT_* value, SERIALIZER_RESULT_NONE on success.
	"""
)

serializer_decode = lib_function (
	"serializer_decode", [c_void_p, c_void_p, c_size_t, c_void_p, c_void_p], SerializerResult,
	"""Decodes and validates the object in the buffer, the object is only written when it is valid.

	Args:
		schema: The address of the SerializerSchema.
		buffer: The bytes of the object, with nothing after it.
		size: Their size.
		arena: The Arena of the arena fields, or None for a schema without them.
		object: The address of the object that gets the values.

	Returns:
		A SERIALIZER_RESULT_* value, SERIALIZER_RESULT_NONE on success.
	"""
)

serializer_schemas = lib_function (
	"serializer_schemas", [POINTER (c_size_t)], c_void_p,
	"""Returns the schemas of the objects that cerver sends.

	Args:
		count: A pointer to a c_size_t that gets their number.

	Returns:
		The address of an array of addresses of SerializerSchema.
	"""
)

def serializer_schema (name: str) -> int:
	"""Returns the address of a schema of libcerver by its name.

	Args:
		name: The name of the schema, like "cerver_summary_schema" or "lobby_summary_schema".

	Returns:
		The address of the SerializerSchema.

	Raises:
		ValueError: libcerver does not have that schema.
	"""
	try:
		schema = ctypes.c_byte.in_dll (lib, name)

	except ValueError as error:
		raise ValueError (f"libcerver has no schema named {name}") from error

	return ctypes.addressof (schema)

def serializer_encode_bytes (schema: int, object) -> bytes | None:
	"""Encodes an object with its schema.

	Args:
		schema: The address of the SerializerSchema (serializer_schema ()).
		object: The ctypes Structure of the object.

	Returns:
		The bytes of the encoded object, None if it can not be encoded.
	"""
	result = None

	size = serializer_encoded_size (schema, byref (object))
	if (size):
		buffer = create_string_buffer (size)
		written = c_size_t (0)
		if (serializer_encode (schema, byref (object), buffer, size, byref (written)) == SERIALIZER_RESULT_NONE):
			result = buffer.raw[:written.value]

	return result

def serializer_decode_bytes (schema: int, data: bytes, object) -> int:
	"""Decodes the bytes of an object with its schema, its schema can not have arena fields.

	Args:
		schema: The address of the SerializerSchema (serializer_schema ()).
		data: The bytes of the encoded object.
		object: The ctypes Structure that gets the values.

	Returns:
		A SERIALIZER_RESULT_* value, SERIALIZER_RESULT_NONE when the object was decoded.
	"""
	return serializer_decode (schema, data, len (data), None, byref (object))
