from ctypes import c_int, c_char_p, c_void_p, CFUNCTYPE

from .lib import lib

HttpRouteModifier = c_int

HTTP_ROUTE_MODIFIER_NONE = 0
HTTP_ROUTE_MODIFIER_MULTI_PART = 1
HTTP_ROUTE_MODIFIER_WEB_SOCKET = 2

HttpHandler = CFUNCTYPE (None, c_void_p, c_void_p)

http_route_create = lib.http_route_create
http_route_create.argtypes = [c_int, c_char_p, HttpHandler]
http_route_create.restype = c_void_p

http_route_set_modifier = lib.http_route_set_modifier
http_route_set_modifier.argtypes = [c_void_p, HttpRouteModifier]
