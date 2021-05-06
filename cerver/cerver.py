import signal

from ctypes import c_int, c_uint8, c_uint16, c_char_p, c_size_t, c_void_p, c_bool

from .lib import lib

from .version import cerver_version_print_full, pycerver_version_print_full

CERVER_DEFAULT_PORT							= 7000
# CERVER_DEFAULT_PROTOCOL						= PROTOCOL_TCP
CERVER_DEFAULT_USE_IPV6						= False
CERVER_DEFAULT_CONNECTION_QUEUE				= 10

CERVER_DEFAULT_RECEIVE_BUFFER_SIZE			= 4096
# CERVER_DEFAULT_MAX_RECEIVED_PACKET_SIZE		= MAX_UDP_PACKET_SIZE

CERVER_DEFAULT_REUSABLE_FLAGS				= False

CERVER_DEFAULT_POOL_THREADS					= 4

CERVER_DEFAULT_SOCKETS_INIT					= 10

CERVER_DEFAULT_POLL_FDS						= 128
CERVER_DEFAULT_POLL_TIMEOUT					= 2000

CERVER_DEFAULT_MAX_INACTIVE_TIME			= 60
CERVER_DEFAULT_CHECK_INACTIVE_INTERVAL		= 30

CERVER_DEFAULT_AUTH_REQUIRED				= False
CERVER_DEFAULT_MAX_AUTH_TRIES				= 2

CERVER_DEFAULT_ON_HOLD_POLL_FDS				= 64
CERVER_DEFAULT_ON_HOLD_TIMEOUT				= 2000
CERVER_DEFAULT_ON_HOLD_MAX_BAD_PACKETS		= 4
CERVER_DEFAULT_ON_HOLD_CHECK_PACKETS		= False
CERVER_DEFAULT_ON_HOLD_RECEIVE_BUFFER_SIZE	= 4096

CERVER_DEFAULT_USE_SESSIONS					= False

CERVER_DEFAULT_MULTIPLE_HANDLERS			= False

CERVER_DEFAULT_CHECK_PACKETS				= False

CERVER_DEFAULT_UPDATE_TICKS					= 30
CERVER_DEFAULT_UPDATE_INTERVAL_SECS			= 1

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

	cerver_init ()

	if (print_version):
		cerver_version_print_full ()
		pycerver_version_print_full ()

# end
cerver_shutdown = lib.cerver_shutdown
cerver_shutdown.argtypes = [c_void_p]
cerver_shutdown.restype = c_uint8

cerver_teardown = lib.cerver_teardown
cerver_teardown.argtypes = [c_void_p]
cerver_teardown.restype = c_uint8
