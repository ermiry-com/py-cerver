"""The methods that a cerver runs in its own threads, every tick or every interval."""

from ctypes import CFUNCTYPE, POINTER, Structure, cast
from ctypes import c_void_p, c_uint, c_uint8
from typing import Any, Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function

__all__ = [
	"CerverUpdate", "CerverUpdatePointer", "CerverUpdateCb", "CerverUpdateDelete",
	"cerver_set_update", "cerver_set_update_interval",
	"cerver_update_delete",
	"cerver_update_configure", "cerver_update_interval_configure"
]

class CerverUpdate (Structure):
	"""The argument of an update method, ``CerverUpdate``.

	Attributes:
		cerver: The cerver.
		args: The update args that were given with the method.
	"""

	_fields_ = [
		("cerver", c_void_p),
		("args", c_void_p)
	]

CerverUpdatePointer: TypeAlias = POINTER (CerverUpdate) # type: ignore

# the method gets a CerverUpdate *
CerverUpdateCb: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore
CerverUpdateDelete: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

cerver_set_update = lib_function (
	"cerver_set_update", [c_void_p, c_void_p, c_void_p, c_void_p, c_uint8], None,
	"""Runs a method in a new thread every tick, like the frames of a game.

	Args:
		cerver: The cerver.
		update: A CerverUpdateCb kept by the caller, it gets a CerverUpdate.
		update_args: The args of the CerverUpdate.
		delete_update_args: A CerverUpdateDelete kept by the caller that releases the args
			at the teardown, or None.
		fps: The ticks per second.
	"""
)

cerver_set_update_interval = lib_function (
	"cerver_set_update_interval", [c_void_p, c_void_p, c_void_p, c_void_p, c_uint], None,
	"""Runs a method in a new thread every interval of seconds.

	Args:
		cerver: The cerver.
		update: A CerverUpdateCb kept by the caller, it gets a CerverUpdate.
		update_args: The args of the CerverUpdate.
		delete_update_args: A CerverUpdateDelete kept by the caller that releases the args
			at the teardown, or None.
		interval: The interval in seconds.
	"""
)

cerver_update_delete = lib_function (
	"cerver_update_delete", [c_void_p], None,
	"""Releases a CerverUpdate.

	Args:
		cerver_update_ptr: The CerverUpdate.
	"""
)

def cerver_update_callback (method: Callable [[int, Any], None]) -> Any:
	"""Returns a kept CerverUpdateCb that calls the method with the cerver and the args."""
	def update (cerver_update_ptr: int) -> None:
		update_values = cast (cerver_update_ptr, CerverUpdatePointer).contents
		method (update_values.cerver, update_values.args)

	return callback_wrap (update, CerverUpdateCb)

def cerver_update_configure (
	cerver: int, method: Callable [[int, Any], None], fps: int, args: Any = None
) -> None:
	"""Runs a Python method in a new thread every tick.

	Args:
		cerver: The cerver.
		method: Called with (cerver, args) every tick.
		fps: The ticks per second.
		args: A c_void_p value given to the method, None by default.
	"""
	cerver_set_update (cerver, cerver_update_callback (method), args, None, fps)

def cerver_update_interval_configure (
	cerver: int, method: Callable [[int, Any], None], interval: int, args: Any = None
) -> None:
	"""Runs a Python method in a new thread every interval of seconds.

	Args:
		cerver: The cerver.
		method: Called with (cerver, args) every interval.
		interval: The interval in seconds.
		args: A c_void_p value given to the method, None by default.
	"""
	cerver_set_update_interval (cerver, cerver_update_callback (method), args, None, interval)
