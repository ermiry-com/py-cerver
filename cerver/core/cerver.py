"""The cerver: its creation, its configuration, its start and its end.

The functions that take a callback expect one that the caller keeps alive (a
CFUNCTYPE object, see cerver.callbacks): a plain Python function is rejected with
TypeError, so a temporary C thunk is never left behind.
"""

from ctypes import CFUNCTYPE, POINTER, Structure
from ctypes import c_void_p, c_char_p, c_bool, c_int, c_long
from ctypes import c_uint, c_uint8, c_uint16, c_uint32, c_size_t
from typing import TypeAlias

from ..lib import lib_function

from ..network.network import Protocol, PROTOCOL_TCP, MAX_UDP_PACKET_SIZE

from ..utils.histograms import Histogram

__all__ = [
	"CERVER_DEFAULT_ALIAS", "CERVER_DEFAULT_PORT", "CERVER_DEFAULT_PROTOCOL",
	"CERVER_DEFAULT_USE_IPV6", "CERVER_DEFAULT_IPV6_ONLY", "CERVER_DEFAULT_CONNECTION_QUEUE",
	"CERVER_BIND_ADDRESS_SIZE",
	"CERVER_DEFAULT_RECEIVE_BUFFER_SIZE", "CERVER_DEFAULT_MAX_RECEIVED_PACKET_SIZE",
	"CERVER_DEFAULT_REUSABLE_FLAGS", "CERVER_DEFAULT_REUSABLE_PORT", "CERVER_DEFAULT_IGNORE_SIGPIPE",
	"CERVER_DEFAULT_POOL_THREADS", "CERVER_DEFAULT_THPOOL_QUEUE_SIZE",
	"CERVER_OVERLOAD_WAIT_TIMEOUT", "CERVER_DEFAULT_DRAIN_TIMEOUT", "CERVER_DRAIN_GRACE_TIMEOUT",
	"CERVER_DEFAULT_SEND_TIMEOUT", "CERVER_DEFAULT_SOCKETS_INIT",
	"CERVER_DEFAULT_POLL_FDS", "CERVER_DEFAULT_POLL_TIMEOUT",
	"CERVER_DEFAULT_MAX_INACTIVE_TIME", "CERVER_DEFAULT_CHECK_INACTIVE_INTERVAL",
	"CERVER_DEFAULT_AUTH_REQUIRED", "CERVER_DEFAULT_MAX_AUTH_TRIES",
	"CERVER_DEFAULT_ON_HOLD_POLL_FDS", "CERVER_DEFAULT_ON_HOLD_TIMEOUT",
	"CERVER_DEFAULT_ON_HOLD_MAX_BAD_PACKETS", "CERVER_DEFAULT_ON_HOLD_CHECK_PACKETS",
	"CERVER_DEFAULT_ON_HOLD_RECEIVE_BUFFER_SIZE", "CERVER_DEFAULT_ON_HOLD_SECONDS",
	"CERVER_DEFAULT_MAX_BAD_PACKETS", "CERVER_DEFAULT_USE_SESSIONS",
	"CERVER_DEFAULT_MULTIPLE_HANDLERS", "CERVER_DEFAULT_CHECK_PACKETS",
	"CERVER_DEFAULT_UPDATE_TICKS", "CERVER_DEFAULT_UPDATE_INTERVAL_SECONDS",
	"CERVER_INFO_NAME_SIZE", "CERVER_INFO_ALIAS_SIZE", "CERVER_INFO_WELCOME_SIZE",
	"CERVER_POLL_MIN_FDS", "CERVER_REQUEST_STATS_SIZE", "CERVER_REQUEST_HANDLERS_MAX",
	"RequestStats", "RequestStatsPointer",
	"cerver_get_request_stats", "cerver_request_stats_print",
	"cerver_set_poll_fds", "cerver_set_on_hold_poll_fds",
	"cerver_set_request_handler", "cerver_set_auth_schema",
	"CerverPointer", "Action", "Delegate", "SessionIdGenerator",
	"CerverType",
	"CERVER_TYPE_NONE", "CERVER_TYPE_CUSTOM", "CERVER_TYPE_GAME",
	"CERVER_TYPE_WEB", "CERVER_TYPE_FILES", "CERVER_TYPE_BALANCER",
	"CerverHandlerType",
	"CERVER_HANDLER_TYPE_NONE", "CERVER_HANDLER_TYPE_POLL", "CERVER_HANDLER_TYPE_THREADS",
	"cerver_init", "cerver_end",
	"cerver_type_to_string", "cerver_handler_type_to_string", "cerver_handler_type_description",
	"cerver_set_alias", "cerver_set_welcome_msg", "cerver_info_send_info_packet",
	"cerver_stats_set_threshold_time", "cerver_stats_print",
	"cerver_set_network_values", "cerver_set_connection_queue",
	"cerver_set_receive_buffer_size", "cerver_set_reusable_address_flags",
	"cerver_set_reusable_port", "cerver_set_bind_address", "cerver_set_ipv6_only",
	"cerver_is_running", "cerver_set_ignore_sigpipe", "cerver_set_cerver_data",
	"cerver_set_thpool_n_threads", "cerver_set_thpool_queue_size",
	"cerver_set_send_timeout", "cerver_set_sockets_pool_init",
	"cerver_set_inactive_clients", "cerver_set_handler_type",
	"cerver_set_handle_detachable_threads", "cerver_set_poll_time_out",
	"cerver_set_auth", "cerver_set_auth_max_tries", "cerver_set_auth_method",
	"cerver_set_on_hold_poll_timeout", "cerver_set_on_hold_timeout",
	"cerver_set_on_hold_max_bad_packets", "cerver_set_on_hold_check_packets",
	"cerver_set_on_hold_receive_buffer_size",
	"cerver_set_sessions", "cerver_set_handle_recieved_buffer",
	"cerver_set_max_received_packet_size",
	"cerver_set_app_handlers", "cerver_set_app_handler_delete",
	"cerver_set_app_error_handler_delete",
	"cerver_set_custom_handler", "cerver_set_custom_handler_delete",
	"cerver_set_multiple_handlers", "cerver_set_check_packets", "cerver_set_max_bad_packets",
	"cerver_set_admin_enable",
	"cerver_handlers_print_info", "cerver_handlers_add",
	"cerver_get_n_handlers", "cerver_get_n_handlers_alive", "cerver_get_n_handlers_working",
	"cerver_create", "cerver_create_web",
	"cerver_start", "cerver_shutdown", "cerver_teardown"
]

CERVER_DEFAULT_ALIAS = "my-cerver"

CERVER_DEFAULT_PORT = 7000
CERVER_DEFAULT_PROTOCOL = PROTOCOL_TCP
CERVER_DEFAULT_USE_IPV6 = False
CERVER_DEFAULT_IPV6_ONLY = False

# SOMAXCONN in linux
CERVER_DEFAULT_CONNECTION_QUEUE = 4096

# INET6_ADDRSTRLEN + IF_NAMESIZE, a literal IPv4 or IPv6 address with its zone
CERVER_BIND_ADDRESS_SIZE = 62

CERVER_DEFAULT_RECEIVE_BUFFER_SIZE = 4096
CERVER_DEFAULT_MAX_RECEIVED_PACKET_SIZE = MAX_UDP_PACKET_SIZE

CERVER_DEFAULT_REUSABLE_FLAGS = False
CERVER_DEFAULT_REUSABLE_PORT = False
CERVER_DEFAULT_IGNORE_SIGPIPE = True

CERVER_DEFAULT_POOL_THREADS = 4

# 0 uses the thpool default (threads * THPOOL_DEFAULT_QUEUE_SIZE_FACTOR)
CERVER_DEFAULT_THPOOL_QUEUE_SIZE = 0

# the ms that the accept loop waits for space in a full thpool before checking the cerver
CERVER_OVERLOAD_WAIT_TIMEOUT = 1024

CERVER_DEFAULT_DRAIN_TIMEOUT = 32

# the extra secs that a drain that timed out waits before reporting what is still alive
CERVER_DRAIN_GRACE_TIMEOUT = 4

CERVER_DEFAULT_SEND_TIMEOUT = 32

CERVER_DEFAULT_SOCKETS_INIT = 10

CERVER_DEFAULT_POLL_FDS = 128
CERVER_DEFAULT_POLL_TIMEOUT = 2000

CERVER_DEFAULT_MAX_INACTIVE_TIME = 60
CERVER_DEFAULT_CHECK_INACTIVE_INTERVAL = 30

CERVER_DEFAULT_AUTH_REQUIRED = False
CERVER_DEFAULT_MAX_AUTH_TRIES = 2

CERVER_DEFAULT_ON_HOLD_POLL_FDS = 64
CERVER_DEFAULT_ON_HOLD_TIMEOUT = 2000
CERVER_DEFAULT_ON_HOLD_MAX_BAD_PACKETS = 4
CERVER_DEFAULT_ON_HOLD_CHECK_PACKETS = False
CERVER_DEFAULT_ON_HOLD_RECEIVE_BUFFER_SIZE = 4096
CERVER_DEFAULT_ON_HOLD_SECONDS = 16

CERVER_DEFAULT_MAX_BAD_PACKETS = 16

CERVER_DEFAULT_USE_SESSIONS = False

CERVER_DEFAULT_MULTIPLE_HANDLERS = False

CERVER_DEFAULT_CHECK_PACKETS = False

CERVER_DEFAULT_UPDATE_TICKS = 30
CERVER_DEFAULT_UPDATE_INTERVAL_SECONDS = 1

# the smallest initial size of the main poll array (cerver_set_poll_fds ())
CERVER_POLL_MIN_FDS = 2

# the request types below it have their own stats in each packet type, the bigger ones share the last entry
CERVER_REQUEST_STATS_SIZE = 32

# the request types below it can have their own handler (cerver_set_request_handler ())
CERVER_REQUEST_HANDLERS_MAX = 1024

class RequestStats (Structure):
	"""The packets of a request type that the handlers of the cerver handled, ``RequestStats``.

	Attributes:
		durations: The microseconds that the handler took with each packet.
		sizes: The bytes of each packet, with its header.
	"""

	_fields_ = [
		("durations", Histogram),
		("sizes", Histogram)
	]

RequestStatsPointer: TypeAlias = POINTER (RequestStats) # type: ignore

CERVER_INFO_NAME_SIZE = 128
CERVER_INFO_ALIAS_SIZE = 32
CERVER_INFO_WELCOME_SIZE = 512

# a pointer to a cerver, as ctypes returns it
CerverPointer: TypeAlias = int | None

# void (*) (void *), the action of cerver that takes its arguments
Action: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

# u8 (*) (void *), returns 0 on success
Delegate: TypeAlias = CFUNCTYPE (c_uint8, c_void_p) # type: ignore

# void *(*) (const void *), returns a session id allocated with malloc ()
SessionIdGenerator: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

# types
CerverType: TypeAlias = c_int # type: ignore

CERVER_TYPE_NONE = 0
CERVER_TYPE_CUSTOM = 1
CERVER_TYPE_GAME = 2
CERVER_TYPE_WEB = 3
CERVER_TYPE_FILES = 4
CERVER_TYPE_BALANCER = 5

CerverHandlerType: TypeAlias = c_int # type: ignore

CERVER_HANDLER_TYPE_NONE = 0
CERVER_HANDLER_TYPE_POLL = 1
CERVER_HANDLER_TYPE_THREADS = 2

# global
cerver_init = lib_function (
	"cerver_init", [], None,
	"""Initializes the global values of cerver.

	It must be called once at the start of the program, before any cerver is created.
	"""
)

cerver_end = lib_function (
	"cerver_end", [], None,
	"""Releases the global values of cerver.

	It must be called once at the very end of the program.
	"""
)

cerver_type_to_string = lib_function (
	"cerver_type_to_string", [CerverType], c_char_p,
	"""Returns the name of a cerver type.

	Args:
		type: A CERVER_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_handler_type_to_string = lib_function (
	"cerver_handler_type_to_string", [CerverHandlerType], c_char_p,
	"""Returns the name of a handler type.

	Args:
		type: A CERVER_HANDLER_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_handler_type_description = lib_function (
	"cerver_handler_type_description", [CerverHandlerType], c_char_p,
	"""Returns the description of a handler type.

	Args:
		type: A CERVER_HANDLER_TYPE_* value.

	Returns:
		The description, as bytes.
	"""
)

# info
cerver_set_alias = lib_function (
	"cerver_set_alias", [c_void_p, c_char_p], None,
	"""Sets the alias of the cerver, used in the names of its threads.

	Args:
		cerver: The cerver.
		alias: The alias, as bytes, up to CERVER_INFO_ALIAS_SIZE bytes.
	"""
)

cerver_set_welcome_msg = lib_function (
	"cerver_set_welcome_msg", [c_void_p, c_char_p], c_uint8,
	"""Sets the message that is sent to a client when it connects.

	Args:
		cerver: The cerver.
		msg: The message, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_info_send_info_packet = lib_function (
	"cerver_info_send_info_packet", [c_void_p, c_void_p, c_void_p], c_uint8,
	"""Sends the info packet of the cerver to a connection.

	Args:
		cerver: The cerver.
		client: The client of the connection.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
)

# stats
cerver_stats_set_threshold_time = lib_function (
	"cerver_stats_set_threshold_time", [c_void_p, c_long], None,
	"""Sets how often the stats of the cerver are reset.

	Args:
		cerver: The cerver.
		threshold_time: The time in seconds, 24 hours by default.
	"""
)

cerver_stats_print = lib_function (
	"cerver_stats_print", [c_void_p, c_bool, c_bool], None,
	"""Prints the stats of the cerver, with those of its thpool.

	Args:
		cerver: The cerver.
		received: True to print the received packets by type.
		sent: True to print the sent packets by type.
	"""
)

cerver_get_request_stats = lib_function (
	"cerver_get_request_stats", [c_void_p, c_int, c_uint32, RequestStatsPointer], c_uint8,
	"""Copies the stats of a request type of PACKET_TYPE_APP, PACKET_TYPE_APP_ERROR or PACKET_TYPE_CUSTOM.

	Args:
		cerver: The cerver.
		packet_type: The PACKET_TYPE_* value.
		request_type: The request type, one of CERVER_REQUEST_STATS_SIZE or bigger gets the shared stats.
		stats: The RequestStats that gets the values.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_request_stats_print = lib_function (
	"cerver_request_stats_print", [c_void_p], None,
	"""Prints the stats of the request types that have packets.

	Args:
		cerver: The cerver.
	"""
)

# main
cerver_set_network_values = lib_function (
	"cerver_set_network_values", [c_void_p, c_uint16, Protocol, c_bool, c_uint16], None,
	"""Sets the main network values of the cerver.

	Args:
		cerver: The cerver.
		port: The port that it listens.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.
		use_ipv6: True to use IPv6.
		connection_queue: The backlog of listen ().
	"""
)

cerver_set_connection_queue = lib_function (
	"cerver_set_connection_queue", [c_void_p, c_uint16], None,
	"""Sets how many connections wait to be accepted (the backlog of listen ()).

	Args:
		cerver: The cerver.
		connection_queue: The number of connections.
	"""
)

cerver_set_receive_buffer_size = lib_function (
	"cerver_set_receive_buffer_size", [c_void_p, c_size_t], None,
	"""Sets the size of the buffer that recv () uses.

	Args:
		cerver: The cerver.
		size: The size in bytes.
	"""
)

cerver_set_reusable_address_flags = lib_function (
	"cerver_set_reusable_address_flags", [c_void_p, c_bool], None,
	"""Sets SO_REUSEADDR in the socket of the cerver, so a restart can bind its address again.

	Args:
		cerver: The cerver.
		value: True to set it, CERVER_DEFAULT_REUSABLE_FLAGS by default.
	"""
)

cerver_set_reusable_port = lib_function (
	"cerver_set_reusable_port", [c_void_p, c_bool], None,
	"""Sets SO_REUSEPORT in the socket of the cerver, so other sockets can bind its port.

	Only enable it when more than one process must listen in the same port, otherwise a
	second cerver can bind the same port without any error.

	Args:
		cerver: The cerver.
		value: True to set it, CERVER_DEFAULT_REUSABLE_PORT by default.
	"""
)

cerver_set_bind_address = lib_function (
	"cerver_set_bind_address", [c_void_p, c_char_p], c_uint,
	"""Sets the literal IPv4 or IPv6 address that the cerver binds, like b"127.0.0.1" or b"::1".

	Its family sets if the cerver uses IPv6, and a link local IPv6 address can have its zone
	(b"fe80::1%eth0"). It must be called before cerver_start ().

	Args:
		cerver: The cerver.
		address: The address, as bytes, None binds every address of its family again.

	Returns:
		0 on success, 1 if it is not a valid ip.
	"""
)

cerver_set_ipv6_only = lib_function (
	"cerver_set_ipv6_only", [c_void_p, c_bool], None,
	"""Sets IPV6_V6ONLY in the socket of an IPv6 cerver.

	Args:
		cerver: The cerver.
		ipv6_only: False (the default) also accepts IPv4 connections, as ::ffff:a.b.c.d.
	"""
)

cerver_is_running = lib_function (
	"cerver_is_running", [c_void_p], c_bool,
	"""Returns if the cerver is accepting connections.

	Args:
		cerver: The cerver.

	Returns:
		True while it is running.
	"""
)

cerver_set_ignore_sigpipe = lib_function (
	"cerver_set_ignore_sigpipe", [c_void_p, c_bool], None,
	"""Sets if cerver_start () ignores SIGPIPE when the process has not set a handler for it.

	Writing to a connection that the client reset raises SIGPIPE, that by default kills the process.

	Args:
		cerver: The cerver.
		value: True (CERVER_DEFAULT_IGNORE_SIGPIPE) to ignore it.
	"""
)

cerver_set_cerver_data = lib_function (
	"cerver_set_cerver_data", [c_void_p, c_void_p, c_void_p], None,
	"""Sets the data of the cerver and how it is released.

	Args:
		cerver: The cerver.
		data: The data.
		delete_data: An Action kept by the caller that releases it, or None.
	"""
)

cerver_set_thpool_n_threads = lib_function (
	"cerver_set_thpool_n_threads", [c_void_p, c_uint16], None,
	"""Sets the threads of the thpool that handles the connections.

	Args:
		cerver: The cerver.
		n_threads: The number of threads.
	"""
)

cerver_set_thpool_queue_size = lib_function (
	"cerver_set_thpool_queue_size", [c_void_p, c_uint], None,
	"""Sets how many accepted connections can wait in the queue of the thpool.

	Args:
		cerver: The cerver.
		queue_size: The size, rounded up to a power of 2, 0 uses the thpool default.
	"""
)

cerver_set_send_timeout = lib_function (
	"cerver_set_send_timeout", [c_void_p, c_uint32], None,
	"""Sets SO_SNDTIMEO for every accepted connection, so a client that never reads can not block a thread.

	Args:
		cerver: The cerver.
		send_timeout: The timeout in seconds, 0 disables it, CERVER_DEFAULT_SEND_TIMEOUT by default.
	"""
)

cerver_set_sockets_pool_init = lib_function (
	"cerver_set_sockets_pool_init", [c_void_p, c_uint], None,
	"""Deprecated: the sockets pool was removed and every connection owns its socket.

	Args:
		cerver: The cerver.
		n_sockets: Ignored.
	"""
)

cerver_set_inactive_clients = lib_function (
	"cerver_set_inactive_clients", [c_void_p, c_uint32, c_uint32], None,
	"""Drops the clients that do not send or receive a packet in a time.

	Args:
		cerver: The cerver.
		max_inactive_time: The seconds that a client can be inactive, 0 for the default.
		check_inactive_interval: How often the clients are checked in seconds, 0 for the default.
	"""
)

cerver_set_handler_type = lib_function (
	"cerver_set_handler_type", [c_void_p, CerverHandlerType], None,
	"""Sets how the connections are handled.

	Args:
		cerver: The cerver.
		handler_type: CERVER_HANDLER_TYPE_POLL (a single thread with poll ()) or
			CERVER_HANDLER_TYPE_THREADS (a thread for each connection).
	"""
)

cerver_set_handle_detachable_threads = lib_function (
	"cerver_set_handle_detachable_threads", [c_void_p, c_bool], None,
	"""Sets if a THREADS cerver handles each connection in a new detached thread instead of its thpool.

	Args:
		cerver: The cerver.
		active: True to create a thread for each connection.
	"""
)

cerver_set_poll_time_out = lib_function (
	"cerver_set_poll_time_out", [c_void_p, c_uint32], None,
	"""Sets the timeout of poll () in a POLL cerver.

	Args:
		cerver: The cerver.
		poll_timeout: The timeout in milliseconds.
	"""
)

cerver_set_auth = lib_function (
	"cerver_set_auth", [c_void_p, c_uint8, c_void_p], c_uint8,
	"""Requires the new connections to authenticate.

	Args:
		cerver: The cerver.
		max_auth_tries: The failed attempts of a connection before it is dropped.
		authenticate: A Delegate kept by the caller, it takes an AuthMethod and returns 0
			on a successful authentication.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_set_auth_max_tries = lib_function (
	"cerver_set_auth_max_tries", [c_void_p, c_uint8], None,
	"""Sets the failed attempts of a connection to authenticate before it is dropped.

	Args:
		cerver: The cerver.
		max_auth_tries: The number of attempts.
	"""
)

cerver_set_auth_method = lib_function (
	"cerver_set_auth_method", [c_void_p, c_void_p], None,
	"""Sets the method that authenticates a connection.

	Args:
		cerver: The cerver.
		authenticate: A Delegate kept by the caller that returns 0 on success.
	"""
)

cerver_set_auth_schema = lib_function (
	"cerver_set_auth_schema", [c_void_p, c_void_p], None,
	"""Sets the schema of the credentials, decoded and validated before the authenticate method gets them.

	Args:
		cerver: The cerver.
		schema: The address of the SerializerSchema (serializer_schema ()), without arena fields.
	"""
)

cerver_set_poll_fds = lib_function (
	"cerver_set_poll_fds", [c_void_p, c_uint32, c_uint32], c_uint8,
	"""Sets, before the cerver starts, the initial size of the main poll array and its max connections.

	Args:
		cerver: The cerver.
		initial: The initial size, at least CERVER_POLL_MIN_FDS.
		max_connections: The max connections, 0 (the default) is no limit; a new one beyond it is closed.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_set_on_hold_poll_fds = lib_function (
	"cerver_set_on_hold_poll_fds", [c_void_p, c_uint32], c_uint8,
	"""Sets, before the cerver starts, the connections that the on hold poll handles at the same time.

	Args:
		cerver: The cerver.
		max_connections: The max connections, CERVER_DEFAULT_ON_HOLD_POLL_FDS by default.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_set_request_handler = lib_function (
	"cerver_set_request_handler", [c_void_p, c_int, c_uint32, c_void_p], c_uint8,
	"""Sets the handler of a request type, that takes its packets before the handler of the packet type.

	Args:
		cerver: The cerver.
		packet_type: PACKET_TYPE_APP, PACKET_TYPE_APP_ERROR or PACKET_TYPE_CUSTOM.
		request_type: The request type, below CERVER_REQUEST_HANDLERS_MAX.
		handler: The Handler (handler_create ()), owned by the cerver after this.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_set_on_hold_poll_timeout = lib_function (
	"cerver_set_on_hold_poll_timeout", [c_void_p, c_uint32], None,
	"""Sets the timeout of the poll () of the connections that did not authenticate.

	Args:
		cerver: The cerver.
		on_hold_poll_timeout: The timeout in milliseconds.
	"""
)

cerver_set_on_hold_timeout = lib_function (
	"cerver_set_on_hold_timeout", [c_void_p, c_uint32], None,
	"""Sets the seconds that a new connection has to authenticate before it is dropped.

	Args:
		cerver: The cerver.
		on_hold_timeout: The seconds, 0 disables it, CERVER_DEFAULT_ON_HOLD_SECONDS by default.
	"""
)

cerver_set_on_hold_max_bad_packets = lib_function (
	"cerver_set_on_hold_max_bad_packets", [c_void_p, c_uint8], None,
	"""Sets the bad packets of a connection that did not authenticate before it is dropped.

	Args:
		cerver: The cerver.
		on_hold_max_bad_packets: The number of bad packets.
	"""
)

cerver_set_on_hold_check_packets = lib_function (
	"cerver_set_on_hold_check_packets", [c_void_p, c_bool], None,
	"""Sets if the packets of the connections that did not authenticate are checked with packet_check ().

	Args:
		cerver: The cerver.
		check: True to check them.
	"""
)

cerver_set_on_hold_receive_buffer_size = lib_function (
	"cerver_set_on_hold_receive_buffer_size", [c_void_p, c_size_t], None,
	"""Sets the size of the buffer that receives the packets of the connections that did not authenticate.

	Args:
		cerver: The cerver.
		on_hold_receive_buffer_size: The size in bytes.
	"""
)

cerver_set_sessions = lib_function (
	"cerver_set_sessions", [c_void_p, c_void_p], c_uint8,
	"""Lets the clients have many connections with a session id (token).

	Args:
		cerver: The cerver.
		session_id_generator: A SessionIdGenerator kept by the caller, or None for the default one.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_set_handle_recieved_buffer = lib_function (
	"cerver_set_handle_recieved_buffer", [c_void_p, c_void_p], None,
	"""Sets a method that handles the raw buffers received from the sockets (a custom protocol).

	Args:
		cerver: The cerver.
		handle_received_buffer: An Action kept by the caller.
	"""
)

cerver_set_max_received_packet_size = lib_function (
	"cerver_set_max_received_packet_size", [c_void_p, c_size_t], None,
	"""Sets the biggest packet that the cerver handles, a bigger one is a bad packet.

	Args:
		cerver: The cerver.
		max_received_packet_size: The size in bytes.
	"""
)

cerver_set_app_handlers = lib_function (
	"cerver_set_app_handlers", [c_void_p, c_void_p, c_void_p], None,
	"""Sets the handlers of the PACKET_TYPE_APP and PACKET_TYPE_APP_ERROR packets.

	Args:
		cerver: The cerver.
		app_handler: A Handler of handler_create (), or None.
		app_error_handler: A Handler of handler_create (), or None.
	"""
)

cerver_set_app_handler_delete = lib_function (
	"cerver_set_app_handler_delete", [c_void_p, c_bool], None,
	"""Sets if cerver deletes the PACKET_TYPE_APP packets after their handler.

	Args:
		cerver: The cerver.
		delete_packet: False when the handler deletes them, True by default.
	"""
)

cerver_set_app_error_handler_delete = lib_function (
	"cerver_set_app_error_handler_delete", [c_void_p, c_bool], None,
	"""Sets if cerver deletes the PACKET_TYPE_APP_ERROR packets after their handler.

	Args:
		cerver: The cerver.
		delete_packet: False when the handler deletes them, True by default.
	"""
)

cerver_set_custom_handler = lib_function (
	"cerver_set_custom_handler", [c_void_p, c_void_p], None,
	"""Sets the handler of the PACKET_TYPE_CUSTOM packets.

	Args:
		cerver: The cerver.
		custom_handler: A Handler of handler_create (), or None.
	"""
)

cerver_set_custom_handler_delete = lib_function (
	"cerver_set_custom_handler_delete", [c_void_p, c_bool], None,
	"""Sets if cerver deletes the PACKET_TYPE_CUSTOM packets after their handler.

	Args:
		cerver: The cerver.
		delete_packet: False when the handler deletes them, True by default.
	"""
)

cerver_set_multiple_handlers = lib_function (
	"cerver_set_multiple_handlers", [c_void_p, c_uint], c_int,
	"""Lets the cerver have many app handlers, selected by the handler id of each packet.

	Args:
		cerver: The cerver.
		n_handlers: The number of handlers.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_set_check_packets = lib_function (
	"cerver_set_check_packets", [c_void_p, c_bool], None,
	"""Sets if the protocol id and version of every packet are checked with packet_check ().

	Args:
		cerver: The cerver.
		check_packets: True to check them, False by default.
	"""
)

cerver_set_max_bad_packets = lib_function (
	"cerver_set_max_bad_packets", [c_void_p, c_uint8], None,
	"""Sets the bad packets of an authenticated connection before it is dropped.

	Args:
		cerver: The cerver.
		max_bad_packets: The number of bad packets, 0 disables the limit,
			CERVER_DEFAULT_MAX_BAD_PACKETS by default.
	"""
)

cerver_set_admin_enable = lib_function (
	"cerver_set_admin_enable", [c_void_p], c_uint8,
	"""Enables the admin connections of the cerver.

	Args:
		cerver: The cerver.

	Returns:
		0 on success, 1 on error.
	"""
)

# handlers
cerver_handlers_print_info = lib_function (
	"cerver_handlers_print_info", [c_void_p], None,
	"""Prints the state of the handlers of the cerver.

	Args:
		cerver: The cerver.
	"""
)

cerver_handlers_add = lib_function (
	"cerver_handlers_add", [c_void_p, c_void_p], c_uint8,
	"""Adds a handler to the multiple app handlers of the cerver.

	Args:
		cerver: The cerver.
		handler: A Handler of handler_create_with_id (), with an id lower than the number of handlers.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_get_n_handlers = lib_function (
	"cerver_get_n_handlers", [c_void_p], c_uint,
	"""Returns the number of app handlers of the cerver.

	Args:
		cerver: The cerver.

	Returns:
		The number of handlers.
	"""
)

cerver_get_n_handlers_alive = lib_function (
	"cerver_get_n_handlers_alive", [c_void_p], c_uint,
	"""Returns the handlers that are ready to handle packets.

	Args:
		cerver: The cerver.

	Returns:
		The number of handlers.
	"""
)

cerver_get_n_handlers_working = lib_function (
	"cerver_get_n_handlers_working", [c_void_p], c_uint,
	"""Returns the handlers that are handling a packet.

	Args:
		cerver: The cerver.

	Returns:
		The number of handlers.
	"""
)

# create
cerver_create = lib_function (
	"cerver_create", [CerverType, c_char_p, c_uint16, Protocol, c_bool, c_uint16], c_void_p,
	"""Creates a cerver.

	Args:
		type: A CERVER_TYPE_* value.
		name: Its name, as bytes.
		port: The port that it listens.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.
		use_ipv6: True to use IPv6.
		connection_queue: The backlog of listen ().

	Returns:
		The cerver, None on error.
	"""
)

cerver_create_web = lib_function (
	"cerver_create_web", [c_char_p, c_uint16, c_uint16], c_void_p,
	"""Creates a cerver of type CERVER_TYPE_WEB, with its HttpCerver.

	Args:
		name: Its name, as bytes.
		port: The port that it listens.
		connection_queue: The backlog of listen ().

	Returns:
		The cerver, None on error.
	"""
)

# start
cerver_start = lib_function (
	"cerver_start", [c_void_p], c_uint8,
	"""Starts the cerver and blocks while it accepts connections.

	A cerver started in the main thread of Python only stops when a signal interrupts it;
	cerver_run () starts it in a thread and stops it with SIGINT or SIGTERM.

	Args:
		cerver: The cerver.

	Returns:
		0 when it started and was stopped, 1 on error.
	"""
)

# end
cerver_shutdown = lib_function (
	"cerver_shutdown", [c_void_p], c_uint8,
	"""Stops accepting connections and wakes up cerver_start ().

	It can be called from any thread, and it also cancels a start that has not happened yet.

	Args:
		cerver: The cerver.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_teardown = lib_function (
	"cerver_teardown", [c_void_p], c_uint8,
	"""Stops the cerver, drains its connections with its drain policy and releases it.

	Args:
		cerver: The cerver, it must not be used after this call.

	Returns:
		0 on success, 1 on error.
	"""
)
