from ctypes import c_int, c_uint8, c_uint16, c_char_p, c_size_t, c_void_p, c_bool

from .lib import lib

CerverType = c_int

CERVER_TYPE_NONE = 0
CERVER_TYPE_CUSTOM = 1 
CERVER_TYPE_GAME = 2
CERVER_TYPE_WEB = 3
CERVER_TYPE_FILES = 4

CerverHandlerType = c_int

CERVER_HANDLER_TYPE_NONE = 0
CERVER_HANDLER_TYPE_POLL = 1
CERVER_HANDLER_TYPE_THREADS = 2

# main
cerver_create_web = lib.cerver_create_web
cerver_create_web.argtypes = [c_char_p, c_uint16, c_uint16]
cerver_create_web.restype = c_void_p

# configuration
cerver_set_receive_buffer_size = lib.cerver_set_receive_buffer_size
cerver_set_receive_buffer_size.argtypes = [c_void_p, c_size_t]

cerver_set_thpool_n_threads = lib.cerver_set_thpool_n_threads
cerver_set_thpool_n_threads.argtypes = [c_void_p, c_uint16]

cerver_set_handler_type = lib.cerver_set_handler_type
cerver_set_handler_type.argtypes = [c_void_p, c_int]

cerver_set_reusable_address_flags = lib.cerver_set_reusable_address_flags
cerver_set_reusable_address_flags.argtypes = [c_void_p, c_bool]

# start
cerver_start = lib.cerver_start
cerver_start.argtypes = [c_void_p]
cerver_start.restype = c_uint8
