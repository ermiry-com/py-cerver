from ctypes import CFUNCTYPE, c_void_p, c_int, c_char_p
from typing import TypeAlias

from ..lib import lib

from .request import RequestMethod

HttpRouteModifier: TypeAlias = c_int # type: ignore

HTTP_ROUTE_MODIFIER_NONE = 0
HTTP_ROUTE_MODIFIER_MULTI_PART = 1
HTTP_ROUTE_MODIFIER_WEB_SOCKET = 2

HttpRouteAuthType: TypeAlias = c_int # type: ignore

HTTP_ROUTE_AUTH_TYPE_NONE = 0
HTTP_ROUTE_AUTH_TYPE_BEARER = 1
HTTP_ROUTE_AUTH_TYPE_CUSTOM = 2

HttpHandler: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p) # type: ignore

HttpDecodeData: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore
HttpDeleteDecoded: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

RouteDeleteCustom: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

http_route_create = lib.http_route_create
http_route_create.argtypes = [RequestMethod, c_char_p, HttpHandler]
http_route_create.restype = c_void_p

http_route_set_handler = lib.http_route_set_handler
http_route_set_handler.argtypes = [c_void_p, RequestMethod, HttpHandler]

http_route_child_add = lib.http_route_child_add
http_route_child_add.argtypes = [c_void_p, c_void_p]

http_route_set_modifier = lib.http_route_set_modifier
http_route_set_modifier.argtypes = [c_void_p, HttpRouteModifier]

http_route_set_auth = lib.http_route_set_auth
http_route_set_auth.argtypes = [c_void_p, HttpRouteModifier]

http_route_set_decode_data = lib.http_route_set_decode_data
http_route_set_decode_data.argtypes = [c_void_p, HttpDecodeData, HttpDeleteDecoded]

http_route_set_decode_data_into_json = lib.http_route_set_decode_data_into_json
http_route_set_decode_data_into_json.argtypes = [c_void_p]

http_route_set_authentication_handler = lib.http_route_set_authentication_handler
http_route_set_authentication_handler.argtypes = [c_void_p, c_void_p]

http_route_get_custom_data = lib.http_route_get_custom_data
http_route_get_custom_data.argtypes = [c_void_p]
http_route_get_custom_data.restype = c_void_p

http_route_set_custom_data = lib.http_route_set_custom_data
http_route_set_custom_data.argtypes = [c_void_p, c_void_p]

http_route_set_delete_custom_data = lib.http_route_set_delete_custom_data
http_route_set_delete_custom_data.argtypes = [c_void_p, RouteDeleteCustom]
