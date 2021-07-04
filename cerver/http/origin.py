from ctypes import Structure, POINTER, c_int, c_char_p, c_void_p

class HttpOrigin (Structure):
	_fields_ = [
		("len", c_uint),
		("value", c_char_p),
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
