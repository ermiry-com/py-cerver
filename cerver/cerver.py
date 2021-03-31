import signal

from ctypes import c_int, c_uint8, c_uint16, c_char_p, c_size_t, c_void_p, c_bool

from .lib import lib

from .version import cerver_version_print_full

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

# global
cerver_init = lib.cerver_init
cerver_end = lib.cerver_end

# stats
cerver_stats_print = lib.cerver_stats_print
cerver_stats_print.argtypes = [c_void_p, c_bool, c_bool]

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

def cerver_initialize (end, print_version = True):
    """
    Function to correctly initialize cerver
    # Parameters
    ------------
    ### end: func ()
        Function to kill cerver process
    ### print_version: bool, optional.
        Flag to choose printing version of cerver.
        Defaults to True.
    """
    signal.signal (signal.SIGINT, end)
    signal.signal (signal.SIGTERM, end)

    cerver_init()
    
    if(print_version):
        cerver_version_print_full ()

# end
cerver_shutdown = lib.cerver_shutdown
cerver_shutdown.argtypes = [c_void_p]
cerver_shutdown.restype = c_uint8

cerver_teardown = lib.cerver_teardown
cerver_teardown.argtypes = [c_void_p]
cerver_teardown.restype = c_uint8
