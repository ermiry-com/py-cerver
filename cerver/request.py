from ctypes import c_int, c_void_p

from .lib import lib

RequestMethod = c_int

REQUEST_METHOD_DELETE = 0
REQUEST_METHOD_GET = 1 
REQUEST_METHOD_HEAD = 2
REQUEST_METHOD_POST = 3
REQUEST_METHOD_PUT = 4

http_request_headers_print = lib.http_request_headers_print
http_request_headers_print.argtypes = [c_void_p]

http_request_query_params_print = lib.http_request_query_params_print
http_request_query_params_print.argtypes = [c_void_p]
