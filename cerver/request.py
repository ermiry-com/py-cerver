from ctypes import c_int, c_void_p, c_char_p, POINTER

from .lib import lib

from .types.string import String

RequestMethod = c_int

REQUEST_METHOD_DELETE = 0
REQUEST_METHOD_GET = 1 
REQUEST_METHOD_HEAD = 2
REQUEST_METHOD_POST = 3
REQUEST_METHOD_PUT = 4

# headers
http_request_headers_print = lib.http_request_headers_print
http_request_headers_print.argtypes = [c_void_p]

# query
http_request_query_params_print = lib.http_request_query_params_print
http_request_query_params_print.argtypes = [c_void_p]

http_request_query_params_get_value = lib.http_request_query_params_get_value
http_request_query_params_get_value.argtypes = [c_void_p, c_char_p]
http_request_query_params_get_value.restype = POINTER (String)

# multi-parts
http_request_multi_parts_get_value = lib.http_request_multi_parts_get_value
http_request_multi_parts_get_value.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_value.restype = POINTER (String)

http_request_multi_parts_get_filename = lib.http_request_multi_parts_get_filename
http_request_multi_parts_get_filename.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_filename.restype = c_char_p

http_request_multi_parts_get_saved_filename = lib.http_request_multi_parts_get_saved_filename
http_request_multi_parts_get_saved_filename.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_saved_filename.restype = c_char_p

http_request_multi_part_keep_files = lib.http_request_multi_part_keep_files
http_request_multi_part_keep_files.argtypes = [c_void_p]

http_request_multi_part_discard_files = lib.http_request_multi_part_discard_files
http_request_multi_part_discard_files.argtypes = [c_void_p]

http_request_multi_parts_print = lib.http_request_multi_parts_print
http_request_multi_parts_print.argtypes = [c_void_p]

# body
http_request_body_get_value = lib.http_request_body_get_value
http_request_body_get_value.argtypes = [c_void_p, c_char_p]
http_request_body_get_value.restype = POINTER (String)
