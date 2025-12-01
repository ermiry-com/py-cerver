from ctypes import Structure, POINTER
from ctypes import c_int, c_char, c_char_p, c_void_p

from ..lib import lib

HTTP_ORIGINS_SIZE = 16
HTTP_ORIGIN_VALUE_SIZE = 256

class HttpOrigin (Structure):
	_fields_ = [
		("len", c_int),
		("value", c_char * HTTP_ORIGIN_VALUE_SIZE)
	]

http_origin_new = lib.http_origin_new
http_origin_new.restype = POINTER (HttpOrigin)

http_origin_delete = lib.http_origin_delete
http_origin_delete.argtypes = [c_void_p]

http_origin_get_len = lib.http_origin_get_len
http_origin_get_len.argtypes = [c_void_p]
http_origin_get_len.restype = c_int

http_origin_get_value = lib.http_origin_get_value
http_origin_get_value.argtypes = [c_void_p]
http_origin_get_value.restype = c_char_p

http_origin_print = lib.http_origin_print
http_origin_print.argtypes = [c_void_p]
