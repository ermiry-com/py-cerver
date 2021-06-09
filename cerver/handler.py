from ctypes import c_int, c_void_p, py_object, c_bool, CFUNCTYPE, Structure, POINTER

from .lib import lib

from .packets import Packet

class HandlerData (Structure):
	_fields_ = [
		("handler_id", c_int),

		("data", py_object),
		("packet", POINTER (Packet))
	]

HandlerMethod = CFUNCTYPE (None, c_void_p)

HandlerDataCreate = CFUNCTYPE (py_object, c_void_p)
HandlerDataDelete = CFUNCTYPE (None, c_void_p)

handler_delete = lib.handler_delete
handler_delete.argtypes = [c_void_p]

handler_create = lib.handler_create
handler_create.argtypes = [HandlerMethod]
handler_create.restype = c_void_p

handler_create_with_id = lib.handler_create_with_id
handler_create_with_id.argtypes = [c_int, HandlerMethod]
handler_create_with_id.restype = c_void_p

handler_set_data = lib.handler_set_data
handler_set_data.argtypes = [c_void_p, c_void_p]
handler_set_data.restype = c_void_p

handler_set_data_create = lib.handler_set_data_create
handler_set_data_create.argtypes = [c_void_p, HandlerDataCreate, c_void_p]

handler_set_data_delete = lib.handler_set_data_delete
handler_set_data_delete.argtypes = [c_void_p, HandlerDataDelete]

handler_set_direct_handle = lib.handler_set_direct_handle
handler_set_direct_handle.argtypes = [c_void_p, c_bool]
