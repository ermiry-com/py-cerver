from ctypes import c_int, c_uint8, c_ulong, c_char_p, c_void_p, CFUNCTYPE

from ..lib import lib

ThreadWork = CFUNCTYPE (c_void_p, c_void_p)

thread_create_detachable = lib.thread_create_detachable
thread_create_detachable.argtypes = [c_ulong, ThreadWork, c_void_p]
thread_create_detachable.restype = c_uint8

thread_set_name = lib.thread_set_name
thread_set_name.argtypes = [c_char_p]
thread_set_name.restype = c_int
