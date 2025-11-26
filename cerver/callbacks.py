"""The references to the Python functions that cerver calls from C.

A function given to cerver as a callback must live as long as cerver may call it:
ctypes releases the C thunk of a callback when its Python object is collected, and
cerver would then jump to freed memory. Every high level function of the package
keeps the callbacks that it creates here; the raw bindings expect a callback that
the caller already keeps.
"""

from typing import Any, Callable

__all__ = [
	"callbacks", "callback_keep", "callback_wrap", "callback_release"
]

# the kept callbacks by their id, so a callback registered twice is kept once
callbacks: dict = {}

def callback_keep (callback: Any) -> Any:
	"""Keeps a callback for as long as the process lives.

	Args:
		callback: A ctypes function (an instance of a CFUNCTYPE type).

	Returns:
		The same callback.
	"""
	callbacks[id (callback)] = callback
	return callback

def callback_wrap (function: Callable, callback_type: Any) -> Any:
	"""Returns a function as a callback of a ctypes type and keeps it.

	A function that already is a callback of the type is kept as it is.

	Args:
		function: A Python function, or a callback of the type.
		callback_type: The CFUNCTYPE type that cerver expects.

	Returns:
		The kept callback of the type.
	"""
	callback = function
	if (not isinstance (function, callback_type)):
		callback = callback_type (function)

	return callback_keep (callback)

def callback_release (callback: Any) -> None:
	"""Stops keeping a callback, only when cerver will never call it again.

	Args:
		callback: A callback kept with callback_keep () or callback_wrap ().
	"""
	callbacks.pop (id (callback), None)
