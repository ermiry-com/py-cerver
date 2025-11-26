"""Loading of libcerver and the declaration of its functions.

The library is loaded from the path in the ``CERVER_LIBRARY`` environment variable,
then from ``/usr/local/lib/libcerver.so`` (where ``make install`` of cerver puts it),
and at last from the paths of the system linker.
"""

import ctypes
import ctypes.util
import os

__all__ = [
	"CERVER_LIBRARY_VARIABLE", "CERVER_LIBRARY_DEFAULT_PATH", "CERVER_LIBRARY_NAME",
	"CerverLibraryError",
	"lib"
]

CERVER_LIBRARY_VARIABLE = "CERVER_LIBRARY"
CERVER_LIBRARY_DEFAULT_PATH = "/usr/local/lib/libcerver.so"
CERVER_LIBRARY_NAME = "cerver"

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
