from ctypes import c_int, c_char_p, c_void_p, CFUNCTYPE

from .lib import lib

HttpHandler = CFUNCTYPE (None, c_void_p, c_void_p)

http_route_create = lib.http_route_create
http_route_create.argtypes = [c_int, c_char_p, HttpHandler]
http_route_create.restype = c_void_p
