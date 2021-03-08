from ctypes import c_int, c_char_p, c_void_p, CFUNCTYPE

from .lib import lib

RequestMethod = c_int

REQUEST_METHOD_DELETE = 0
REQUEST_METHOD_GET = 1 
REQUEST_METHOD_HEAD = 2
REQUEST_METHOD_POST = 3
REQUEST_METHOD_PUT = 4

HttpHandler = CFUNCTYPE (None, c_void_p, c_void_p)

http_route_create = lib.http_route_create
http_route_create.argtypes = [c_int, c_char_p, HttpHandler]
http_route_create.restype = c_void_p
