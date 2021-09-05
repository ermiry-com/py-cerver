from ctypes import POINTER, c_void_p, c_char_p

from ..lib import lib

from ..types.string import String

http_query_pairs_get_value = lib.http_query_pairs_get_value
http_query_pairs_get_value.argtypes = [c_void_p, c_char_p]
http_query_pairs_get_value.restype = POINTER (String)

http_query_pairs_print = lib.http_query_pairs_print
http_query_pairs_print.argtypes = [c_void_p]
