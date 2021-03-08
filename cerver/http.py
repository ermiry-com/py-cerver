from ctypes import c_void_p, c_char_p

from .lib import lib

# main
http_cerver_get = lib.http_cerver_get
http_cerver_get.argtypes = [c_void_p]
http_cerver_get.restype = c_void_p

# stats
http_cerver_all_stats_print = lib.http_cerver_all_stats_print
http_cerver_all_stats_print.argtypes = [c_void_p]

# public
http_cerver_static_path_add = lib.http_cerver_static_path_add
http_cerver_static_path_add.argtypes = [c_void_p, c_char_p]
http_cerver_static_path_add.restype = c_void_p

# routes
http_cerver_route_register = lib.http_cerver_route_register
http_cerver_route_register.argtypes = [c_void_p, c_void_p]
