import signal

from ctypes import CFUNCTYPE, Structure, c_void_p, c_char_p
from ctypes import c_int, c_uint, c_uint8, c_uint16, c_size_t, c_bool

from .lib import lib

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
cerver_set_alias = lib.cerver_set_alias
cerver_set_alias.argtypes = [c_void_p, c_char_p]

cerver_set_welcome_msg = lib.cerver_set_welcome_msg
cerver_set_welcome_msg.argtypes = [c_void_p, c_char_p]
cerver_set_welcome_msg.restype = c_uint8

cerver_create = lib.cerver_create
cerver_create.argtypes = [CerverType, c_char_p, c_uint16, c_int, c_bool, c_uint16]
cerver_create.restype = c_void_p

cerver_create_web = lib.cerver_create_web
cerver_create_web.argtypes = [c_char_p, c_uint16, c_uint16]
cerver_create_web.restype = c_void_p

# configuration
cerver_set_receive_buffer_size = lib.cerver_set_receive_buffer_size
cerver_set_receive_buffer_size.argtypes = [c_void_p, c_size_t]

cerver_set_thpool_n_threads = lib.cerver_set_thpool_n_threads
cerver_set_thpool_n_threads.argtypes = [c_void_p, c_uint16]

cerver_set_handler_type = lib.cerver_set_handler_type
cerver_set_handler_type.argtypes = [c_void_p, CerverHandlerType]

cerver_set_reusable_address_flags = lib.cerver_set_reusable_address_flags
cerver_set_reusable_address_flags.argtypes = [c_void_p, c_bool]

cerver_set_app_handlers = lib.cerver_set_app_handlers
cerver_set_app_handlers.argtypes = [c_void_p, c_void_p, c_void_p]

# update
class CerverUpdate (Structure):
	_fields_ = [
		("cerver", c_void_p),
		("args", c_void_p)
	]

CerverUpdateCb = CFUNCTYPE (None, c_void_p)
CerverUpdateDelete = CFUNCTYPE (c_void_p, c_void_p)

cerver_set_update = lib.cerver_set_update
cerver_set_update.argtypes = [
	c_void_p, CerverUpdateCb, c_void_p, CerverUpdateDelete, c_uint
]

cerver_set_update_interval = lib.cerver_set_update_interval
cerver_set_update_interval.argtypes = [
	c_void_p, CerverUpdateCb, c_void_p, CerverUpdateDelete, c_uint
]

# start
cerver_start = lib.cerver_start
cerver_start.argtypes = [c_void_p]
cerver_start.restype = c_uint8

# end
cerver_shutdown = lib.cerver_shutdown
cerver_shutdown.argtypes = [c_void_p]
cerver_shutdown.restype = c_uint8

cerver_teardown = lib.cerver_teardown
cerver_teardown.argtypes = [c_void_p]
cerver_teardown.restype = c_uint8
