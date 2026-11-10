"""The handlers of the packets of a cerver or a client."""

from ctypes import CFUNCTYPE, POINTER, Structure
from ctypes import c_int, c_void_p, c_char_p, c_bool, py_object
from typing import TypeAlias

from ..lib import lib_function

from .packets import Packet

__all__ = [
	"HandlerType",
	"HANDLER_TYPE_NONE", "HANDLER_TYPE_CERVER", "HANDLER_TYPE_CLIENT", "HANDLER_TYPE_ADMIN",
	"HandlerData", "HandlerDataPointer",
	"HandlerMethod", "HandlerDataCreate", "HandlerDataDelete",
	"CerverHandlerError",
	"CERVER_HANDLER_ERROR_NONE", "CERVER_HANDLER_ERROR_PACKET", "CERVER_HANDLER_ERROR_DROPPED",
	"handler_create", "handler_create_with_id",
	"handler_set_data", "handler_set_data_create", "handler_set_data_delete",
	"handler_set_direct_handle",
	"cerver_handler_error_to_string", "cerver_handler_error_description"
]

HandlerType: TypeAlias = c_int # type: ignore

HANDLER_TYPE_NONE = 0
HANDLER_TYPE_CERVER = 1
HANDLER_TYPE_CLIENT = 2
HANDLER_TYPE_ADMIN = 3

class HandlerData (Structure):
	"""What a handler method gets for each packet, ``HandlerData``.

	Attributes:
		handler_id: The id of the handler.
		data: The data of the handler, the Python object of handler_set_data_create ().
		packet: The packet to handle.
	"""

	_fields_ = [
		("handler_id", c_int),

		("data", py_object),
		("packet", POINTER (Packet))
	]

HandlerDataPointer: TypeAlias = POINTER (HandlerData) # type: ignore

# the method of a handler, it gets a HandlerData *
HandlerMethod: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

HandlerDataCreate: TypeAlias = CFUNCTYPE (py_object, c_void_p) # type: ignore
HandlerDataDelete: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

CerverHandlerError: TypeAlias = c_int # type: ignore

CERVER_HANDLER_ERROR_NONE = 0
CERVER_HANDLER_ERROR_PACKET = 1
CERVER_HANDLER_ERROR_DROPPED = 2

handler_create = lib_function (
	"handler_create", [c_void_p], c_void_p,
	"""Creates a handler of packets.

	Args:
		handler_method: A HandlerMethod kept by the caller, it gets a HandlerData.

	Returns:
		The handler, None on error.
	"""
)

handler_create_with_id = lib_function (
	"handler_create_with_id", [c_int, c_void_p], c_void_p,
	"""Creates a handler for the multiple app handlers of a cerver.

	The packets are given to the handler whose id matches their handler id.

	Args:
		id: The unique id of the handler, lower than the number of handlers of the cerver.
		handler_method: A HandlerMethod kept by the caller, it gets a HandlerData.

	Returns:
		The handler, None on error.
	"""
)

handler_set_data = lib_function (
	"handler_set_data", [c_void_p, c_void_p], None,
	"""Sets the data of the handler, given to its method in the HandlerData.

	Args:
		handler: The handler.
		data: The data.
	"""
)

handler_set_data_create = lib_function (
	"handler_set_data_create", [c_void_p, c_void_p, c_void_p], None,
	"""Sets a method that creates the data of the handler when it starts.

	Args:
		handler: The handler.
		data_create: A HandlerDataCreate kept by the caller.
		data_create_args: The argument of the method.
	"""
)

handler_set_data_delete = lib_function (
	"handler_set_data_delete", [c_void_p, c_void_p], None,
	"""Sets a method that releases the data of the handler when it ends.

	Args:
		handler: The handler.
		data_delete: A HandlerDataDelete kept by the caller, or None.
	"""
)

handler_set_direct_handle = lib_function (
	"handler_set_direct_handle", [c_void_p, c_bool], None,
	"""Sets if the packets are handled in the thread that receives them instead of the queue of the handler.

	Args:
		handler: The handler.
		direct_handle: True to handle them right away, False by default.
	"""
)

cerver_handler_error_to_string = lib_function (
	"cerver_handler_error_to_string", [CerverHandlerError], c_char_p,
	"""Returns the name of a handler error.

	Args:
		error: A CERVER_HANDLER_ERROR_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_handler_error_description = lib_function (
	"cerver_handler_error_description", [CerverHandlerError], c_char_p,
	"""Returns the description of a handler error.

	Args:
		error: A CERVER_HANDLER_ERROR_* value.

	Returns:
		The description, as bytes.
	"""
)
