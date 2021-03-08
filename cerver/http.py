from ctypes import c_void_p

from .lib import lib

http_cerver_get = lib.http_cerver_get
http_cerver_get.argtypes = [c_void_p]
http_cerver_get.restype = c_void_p

http_cerver_route_register = lib.http_cerver_route_register
http_cerver_route_register.argtypes = [c_void_p, c_void_p]
