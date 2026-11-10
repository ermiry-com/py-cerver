"""Loading of libcerver and the declaration of its functions.

The library is loaded from the path in the ``CERVER_LIBRARY`` environment variable,
then from ``/usr/local/lib/libcerver.so`` (where ``make install`` of cerver puts it),
and at last from the paths of the system linker.
"""

import ctypes
import ctypes.util
import os
from typing import Any

__all__ = [
	"CERVER_LIBRARY_VARIABLE", "CERVER_LIBRARY_DEFAULT_PATH", "CERVER_LIBRARY_NAME",
	"CerverLibraryError",
	"lib", "libc", "libc_free",
	"lib_functions", "lib_function",
	"lib_take_c_string", "lib_c_string", "lib_text"
]

CERVER_LIBRARY_VARIABLE = "CERVER_LIBRARY"
CERVER_LIBRARY_DEFAULT_PATH = "/usr/local/lib/libcerver.so"
CERVER_LIBRARY_NAME = "cerver"

TEXT_ENCODING = "utf-8"

class CerverLibraryError (ImportError):
	"""Raised when libcerver can not be found or loaded."""

def lib_candidates () -> list:
	"""Returns the paths where libcerver is looked for, in order."""
	candidates = []

	configured = os.environ.get (CERVER_LIBRARY_VARIABLE)
	if (configured):
		candidates.append (configured)

	candidates.append (CERVER_LIBRARY_DEFAULT_PATH)

	found = ctypes.util.find_library (CERVER_LIBRARY_NAME)
	if (found):
		candidates.append (found)

	return candidates

def lib_load () -> ctypes.CDLL:
	"""Loads libcerver from the first path that works.

	Returns:
		The loaded library.

	Raises:
		CerverLibraryError: If no path has a library that can be loaded.
	"""
	errors = []

	library = None
	for candidate in lib_candidates ():
		try:
			library = ctypes.CDLL (candidate)
			break

		except OSError as error:
			errors.append (f"{candidate}: {error}")

	if (library is None):
		raise CerverLibraryError (
			"Failed to load libcerver, install cerver or set "
			f"{CERVER_LIBRARY_VARIABLE} to its path ({'; '.join (errors)})"
		)

	return library

lib = lib_load ()

# the C library of the process, used to free the memory that cerver allocates for the caller
libc = ctypes.CDLL (None)

libc_free = libc.free
libc_free.argtypes = [ctypes.c_void_p]
libc_free.restype = None

# every function that the package declares, by its name in libcerver
lib_functions: dict = {}

def lib_function (name: str, argtypes: list | None, restype: Any, doc: str) -> Any:
	"""Declares a function of libcerver with its types and its documentation.

	Args:
		name: The name of the function in libcerver.
		argtypes: The ctypes of its arguments, None for a variadic function,
			whose arguments must be given already converted to ctypes values.
		restype: The ctypes of its result, None when it returns nothing.
		doc: Its docstring.

	Returns:
		The function of the library, ready to be called.
	"""
	function = getattr (lib, name)

	if (argtypes is not None):
		function.argtypes = argtypes

	function.restype = restype
	function.__doc__ = doc

	lib_functions[name] = function

	return function

def lib_take_c_string (pointer: int | None) -> bytes | None:
	"""Copies a C string that cerver allocated for the caller and frees it.

	Args:
		pointer: The address of the string, None or 0 for a NULL one.

	Returns:
		The bytes of the string, None for a NULL one.
	"""
	result = None
	if (pointer):
		result = ctypes.string_at (pointer)
		libc_free (pointer)

	return result

def lib_c_string (value: str | bytes | None) -> bytes | None:
	"""Converts a value given by the caller into the bytes that a C string argument expects.

	Args:
		value: A str (encoded as utf-8), bytes or None (NULL).

	Returns:
		The bytes, or None.
	"""
	result = value
	if (isinstance (value, str)):
		result = value.encode (TEXT_ENCODING)

	return result

def lib_text (value: bytes | None) -> str | None:
	"""Converts the bytes of a C string into text.

	Args:
		value: The bytes, None for a NULL string.

	Returns:
		The text, None when it is NULL or it is not valid utf-8.
	"""
	result = None
	if (value is not None):
		try:
			result = value.decode (TEXT_ENCODING)

		except UnicodeDecodeError:
			pass

	return result
