"""The packets of the cerver protocol: their header, their creation and how they are sent."""

from ctypes import POINTER, Structure
from ctypes import c_int, c_bool, c_char_p, c_void_p
from ctypes import c_uint, c_uint8, c_uint16, c_uint32, c_uint64, c_size_t, string_at
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"PACKETS_MAX_TYPES", "PACKETS_CURRENT_TYPES",
	"PacketType",
	"PACKET_TYPE_NONE", "PACKET_TYPE_CERVER", "PACKET_TYPE_CLIENT", "PACKET_TYPE_ERROR",
	"PACKET_TYPE_REQUEST", "PACKET_TYPE_AUTH", "PACKET_TYPE_GAME", "PACKET_TYPE_APP",
	"PACKET_TYPE_APP_ERROR", "PACKET_TYPE_CUSTOM", "PACKET_TYPE_TEST", "PACKET_TYPE_BAD",
	"CerverPacketType",
	"CERVER_PACKET_TYPE_NONE", "CERVER_PACKET_TYPE_INFO", "CERVER_PACKET_TYPE_TEARDOWN",
	"ClientPacketType",
	"CLIENT_PACKET_TYPE_NONE", "CLIENT_PACKET_TYPE_CLOSE_CONNECTION", "CLIENT_PACKET_TYPE_DISCONNECT",
	"RequestPacketType",
	"REQUEST_PACKET_TYPE_NONE", "REQUEST_PACKET_TYPE_GET_FILE", "REQUEST_PACKET_TYPE_SEND_FILE",
	"AuthPacketType",
	"AUTH_PACKET_TYPE_NONE", "AUTH_PACKET_TYPE_REQUEST_AUTH", "AUTH_PACKET_TYPE_CLIENT_AUTH",
	"AUTH_PACKET_TYPE_ADMIN_AUTH", "AUTH_PACKET_TYPE_SUCCESS",
	"GamePacketType",
	"GAME_PACKET_TYPE_NONE", "GAME_PACKET_TYPE_GAME_INIT", "GAME_PACKET_TYPE_GAME_START",
	"GAME_PACKET_TYPE_LOBBY_CREATE", "GAME_PACKET_TYPE_LOBBY_JOIN", "GAME_PACKET_TYPE_LOBBY_LEAVE",
	"GAME_PACKET_TYPE_LOBBY_UPDATE", "GAME_PACKET_TYPE_LOBBY_DESTROY",
	"ProtocolID", "ProtocolVersion", "PacketVersion", "PacketVersionPointer",
	"PacketsPerType", "PacketsPerTypePointer",
	"PacketHeader", "PacketHeaderPointer", "Packet", "PacketPointer",
	"packets_get_protocol_id", "packets_set_protocol_id",
	"packets_get_protocol_version", "packets_set_protocol_version",
	"packet_version_new", "packet_version_delete", "packet_version_create",
	"packet_version_copy", "packet_version_print", "packet_version_local",
	"packets_per_type_new", "packets_per_type_delete",
	"packets_per_type_print", "packets_per_type_array_print",
	"packet_header_new", "packet_header_delete", "packet_header_create",
	"packet_header_create_from", "packet_header_copy", "packet_header_print", "packet_header_log",
	"packet_new", "packet_delete", "packet_create",
	"packet_set_network_values", "packet_set_header", "packet_set_header_values",
	"packet_create_data", "packet_set_data", "packet_append_data", "packet_set_data_ref",
	"packet_set_packet", "packet_set_packet_ref", "packet_generate",
	"packet_create_request", "packet_create_ping", "packet_init_request", "packet_init_ping",
	"packet_generate_request",
	"packet_send", "packet_send_unsafe", "packet_send_to", "packet_send_split",
	"packet_send_to_split", "packet_send_pieces", "packet_send_to_socket",
	"packet_send_request", "packet_send_ping",
	"packet_route_between_connections", "packet_check",
	"packet_send_data", "packet_data"
]

PACKETS_MAX_TYPES = 16
PACKETS_CURRENT_TYPES = 10

PacketType: TypeAlias = c_int # type: ignore

PACKET_TYPE_NONE = 0
PACKET_TYPE_CERVER = 1
PACKET_TYPE_CLIENT = 2
PACKET_TYPE_ERROR = 3
PACKET_TYPE_REQUEST = 4
PACKET_TYPE_AUTH = 5
PACKET_TYPE_GAME = 6
PACKET_TYPE_APP = 7
PACKET_TYPE_APP_ERROR = 8
PACKET_TYPE_CUSTOM = 9
PACKET_TYPE_TEST = 10
PACKET_TYPE_BAD = 11

CerverPacketType: TypeAlias = c_int # type: ignore

CERVER_PACKET_TYPE_NONE = 0
CERVER_PACKET_TYPE_INFO = 1
CERVER_PACKET_TYPE_TEARDOWN = 2

ClientPacketType: TypeAlias = c_int # type: ignore

CLIENT_PACKET_TYPE_NONE = 0
CLIENT_PACKET_TYPE_CLOSE_CONNECTION = 1
CLIENT_PACKET_TYPE_DISCONNECT = 2

RequestPacketType: TypeAlias = c_int # type: ignore

REQUEST_PACKET_TYPE_NONE = 0
REQUEST_PACKET_TYPE_GET_FILE = 1
REQUEST_PACKET_TYPE_SEND_FILE = 2

AuthPacketType: TypeAlias = c_int # type: ignore

AUTH_PACKET_TYPE_NONE = 0
AUTH_PACKET_TYPE_REQUEST_AUTH = 1
AUTH_PACKET_TYPE_CLIENT_AUTH = 2
AUTH_PACKET_TYPE_ADMIN_AUTH = 3
AUTH_PACKET_TYPE_SUCCESS = 4

GamePacketType: TypeAlias = c_int # type: ignore

GAME_PACKET_TYPE_NONE = 0
GAME_PACKET_TYPE_GAME_INIT = 1
GAME_PACKET_TYPE_GAME_START = 2
GAME_PACKET_TYPE_LOBBY_CREATE = 3
GAME_PACKET_TYPE_LOBBY_JOIN = 4
GAME_PACKET_TYPE_LOBBY_LEAVE = 5
GAME_PACKET_TYPE_LOBBY_UPDATE = 6
GAME_PACKET_TYPE_LOBBY_DESTROY = 7

ProtocolID: TypeAlias = c_uint32 # type: ignore

class ProtocolVersion (Structure):
	"""The version of the protocol of an application, ``ProtocolVersion``.

	Attributes:
		major: A packet of another major version is a bad packet.
		minor: A packet of a newer minor version is a bad packet.
	"""

	_fields_ = [
		("major", c_uint16),
		("minor", c_uint16)
	]

class PacketVersion (Structure):
	"""The protocol of the sender of a packet, ``PacketVersion``.

	Attributes:
		protocol_id: The id of the protocol of the application.
		protocol_version: Its version.
	"""

	_fields_ = [
		("protocol_id", ProtocolID),
		("protocol_version", ProtocolVersion)
	]

PacketVersionPointer: TypeAlias = POINTER (PacketVersion) # type: ignore

class PacketsPerType (Structure):
	"""The packets of each type that were sent or received, ``PacketsPerType``."""

	_fields_ = [
		("n_cerver_packets", c_uint64),
		("n_client_packets", c_uint64),
		("n_error_packets", c_uint64),
		("n_request_packets", c_uint64),
		("n_auth_packets", c_uint64),
		("n_game_packets", c_uint64),
		("n_app_packets", c_uint64),
		("n_app_error_packets", c_uint64),
		("n_custom_packets", c_uint64),
		("n_test_packets", c_uint64),
		("n_unknown_packets", c_uint64),
		("n_bad_packets", c_uint64)
	]

PacketsPerTypePointer: TypeAlias = POINTER (PacketsPerType) # type: ignore

class PacketHeader (Structure):
	"""The header of every packet, ``PacketHeader``.

	Attributes:
		packet_type: The main type, a PACKET_TYPE_* value.
		packet_size: The size of the packet, the header and the data.
		handler_id: The app handler of a cerver with multiple handlers.
		request_type: The subtype of the packet.
		sock_fd: The connection of the packet in a load balancer.
		version: The protocol of the sender.
	"""

	_fields_ = [
		("packet_type", PacketType),
		("packet_size", c_size_t),

		("handler_id", c_uint8),

		("request_type", c_uint32),

		("sock_fd", c_uint16),

		("version", PacketVersion)
	]

PacketHeaderPointer: TypeAlias = POINTER (PacketHeader) # type: ignore

class Packet (Structure):
	"""A packet that is sent or received, ``Packet``.

	Attributes:
		cerver: The cerver of the packet.
		client: The client of the packet.
		connection: The connection of the packet.
		lobby: The lobby of the packet.
		packet_type: The main type, a PACKET_TYPE_* value.
		req_type: The subtype of the packet.
		data_size: The size of the data.
		data: The data, without the header.
		header: The header.
		release: Called by packet_delete () before the packet is released (an UDP peer).
		release_args: The argument of release.
	"""

	_fields_ = [
		("cerver", c_void_p),
		("client", c_void_p),
		("connection", c_void_p),
		("lobby", c_void_p),

		("packet_type", PacketType),
		("req_type", c_uint32),

		("data_size", c_size_t),
		("data", c_void_p),
		("data_ptr", c_char_p),
		("data_end", c_char_p),
		("data_ref", c_bool),

		("remaining_data", c_size_t),

		("header", PacketHeader),

		("version", PacketVersion),

		("packet_size", c_size_t),
		("packet", c_void_p),
		("packet_ref", c_bool),

		("release", c_void_p),
		("release_args", c_void_p)
	]

PacketPointer: TypeAlias = POINTER (Packet) # type: ignore

# protocol
packets_get_protocol_id = lib_function (
	"packets_get_protocol_id", [], ProtocolID,
	"""Returns the protocol id of the application.

	Returns:
		The protocol id.
	"""
)

packets_set_protocol_id = lib_function (
	"packets_set_protocol_id", [ProtocolID], None,
	"""Sets the protocol id of the application, packet_check () rejects a packet with another one.

	Args:
		protocol_id: The protocol id.
	"""
)

packets_get_protocol_version = lib_function (
	"packets_get_protocol_version", [], ProtocolVersion,
	"""Returns the protocol version of the application.

	Returns:
		A ProtocolVersion.
	"""
)

packets_set_protocol_version = lib_function (
	"packets_set_protocol_version", [ProtocolVersion], None,
	"""Sets the protocol version of the application, packet_check () validates it.

	Args:
		version: A ProtocolVersion.
	"""
)

# version
packet_version_new = lib_function (
	"packet_version_new", [], PacketVersionPointer,
	"""Allocates an empty packet version.

	Returns:
		The PacketVersion, released with packet_version_delete ().
	"""
)

packet_version_delete = lib_function (
	"packet_version_delete", [PacketVersionPointer], None,
	"""Releases a packet version.

	Args:
		version: The PacketVersion.
	"""
)

packet_version_create = lib_function (
	"packet_version_create", [], PacketVersionPointer,
	"""Creates a packet version with the protocol of the application.

	Returns:
		The PacketVersion, released with packet_version_delete ().
	"""
)

packet_version_copy = lib_function (
	"packet_version_copy", [PacketVersionPointer, PacketVersionPointer], c_uint8,
	"""Copies a packet version.

	Args:
		dest: The PacketVersion that gets the values.
		source: The PacketVersion to copy.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_version_print = lib_function (
	"packet_version_print", [PacketVersionPointer], None,
	"""Prints a packet version.

	Args:
		version: The PacketVersion.
	"""
)

packet_version_local = lib_function (
	"packet_version_local", [], PacketVersion,
	"""Returns the protocol id and version of this process.

	Returns:
		A PacketVersion.
	"""
)

# types
packets_per_type_new = lib_function (
	"packets_per_type_new", [], PacketsPerTypePointer,
	"""Allocates the counters of packets by type.

	Returns:
		The PacketsPerType, released with packets_per_type_delete ().
	"""
)

packets_per_type_delete = lib_function (
	"packets_per_type_delete", [c_void_p], None,
	"""Releases the counters of packets by type.

	Args:
		packets_per_type_ptr: The PacketsPerType.
	"""
)

packets_per_type_print = lib_function (
	"packets_per_type_print", [PacketsPerTypePointer], None,
	"""Prints the counters of packets by type.

	Args:
		packets_per_type: The PacketsPerType.
	"""
)

packets_per_type_array_print = lib_function (
	"packets_per_type_array_print", [POINTER (c_uint64)], None,
	"""Prints an array of PACKETS_MAX_TYPES counters of packets.

	Args:
		packets: The array of c_uint64.
	"""
)

# header
packet_header_new = lib_function (
	"packet_header_new", [], PacketHeaderPointer,
	"""Allocates an empty packet header.

	Returns:
		The PacketHeader, released with packet_header_delete ().
	"""
)

packet_header_delete = lib_function (
	"packet_header_delete", [PacketHeaderPointer], None,
	"""Releases a packet header.

	Args:
		header: The PacketHeader.
	"""
)

packet_header_create = lib_function (
	"packet_header_create", [PacketType, c_size_t, c_uint32], PacketHeaderPointer,
	"""Creates a packet header.

	Args:
		packet_type: A PACKET_TYPE_* value.
		packet_size: The size of the packet, the header and the data.
		req_type: The subtype of the packet.

	Returns:
		The PacketHeader, released with packet_header_delete ().
	"""
)

packet_header_create_from = lib_function (
	"packet_header_create_from", [PacketHeaderPointer], PacketHeaderPointer,
	"""Creates a copy of a packet header.

	Args:
		source: The PacketHeader to copy.

	Returns:
		The new PacketHeader, released with packet_header_delete ().
	"""
)

packet_header_copy = lib_function (
	"packet_header_copy", [PacketHeaderPointer, PacketHeaderPointer], c_uint8,
	"""Copies the values of a packet header.

	Args:
		dest: The PacketHeader that gets the values.
		source: The PacketHeader to copy.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_header_print = lib_function (
	"packet_header_print", [PacketHeaderPointer], None,
	"""Prints a packet header.

	Args:
		header: The PacketHeader.
	"""
)

packet_header_log = lib_function (
	"packet_header_log", [PacketHeaderPointer], None,
	"""Writes a packet header in the log.

	Args:
		header: The PacketHeader.
	"""
)

# packets
packet_new = lib_function (
	"packet_new", [], PacketPointer,
	"""Allocates an empty packet.

	Returns:
		The Packet, released with packet_delete ().
	"""
)

packet_delete = lib_function (
	"packet_delete", [c_void_p], None,
	"""Releases a packet with its data, after calling its release.

	Args:
		ptr: The Packet.
	"""
)

packet_create = lib_function (
	"packet_create", [PacketType, c_uint32, c_void_p, c_size_t], PacketPointer,
	"""Creates a packet with a copy of its data, packet_generate () prepares it to be sent.

	Args:
		type: A PACKET_TYPE_* value.
		req_type: The subtype of the packet.
		data: The data, as bytes, or None.
		data_size: The size of the data.

	Returns:
		The Packet, released with packet_delete ().
	"""
)

packet_set_network_values = lib_function (
	"packet_set_network_values", [PacketPointer, c_void_p, c_void_p, c_void_p, c_void_p], None,
	"""Sets to whom the packet is sent.

	Args:
		packet: The Packet.
		cerver: The cerver, or None.
		client: The client, or None.
		connection: The connection.
		lobby: The lobby, or None.
	"""
)

packet_set_header = lib_function (
	"packet_set_header", [PacketPointer, PacketHeaderPointer], None,
	"""Copies a header into the packet.

	Args:
		packet: The Packet.
		header: The PacketHeader.
	"""
)

packet_set_header_values = lib_function (
	"packet_set_header_values",
	[PacketPointer, PacketType, c_size_t, c_uint8, c_uint32, c_uint16],
	None,
	"""Sets the values of the header of the packet.

	Args:
		packet: The Packet.
		packet_type: A PACKET_TYPE_* value.
		packet_size: The size of the packet.
		handler_id: The app handler of a cerver with multiple handlers.
		request_type: The subtype of the packet.
		sock_fd: The connection of the packet in a load balancer.
	"""
)

packet_create_data = lib_function (
	"packet_create_data", [PacketPointer, c_size_t], c_uint,
	"""Allocates the data of the packet.

	Args:
		packet: The Packet.
		data_size: The size of the data.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_set_data = lib_function (
	"packet_set_data", [PacketPointer, c_void_p, c_size_t], c_uint8,
	"""Sets a copy of the data in the packet, replacing the previous one.

	Args:
		packet: The Packet.
		data: The data, as bytes.
		data_size: The size of the data.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_append_data = lib_function (
	"packet_append_data", [PacketPointer, c_void_p, c_size_t], c_uint8,
	"""Appends a copy of the data to the data of the packet.

	Args:
		packet: The Packet.
		data: The data, as bytes.
		data_size: The size of the data.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_set_data_ref = lib_function (
	"packet_set_data_ref", [PacketPointer, c_void_p, c_size_t], c_uint8,
	"""Sets a reference to the data of the packet, it is not copied nor released.

	Args:
		packet: The Packet.
		data: The data, kept alive by the caller while the packet is used.
		data_size: The size of the data.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_set_packet = lib_function (
	"packet_set_packet", [PacketPointer, c_void_p, c_size_t], c_uint8,
	"""Sets a copy of a complete packet (with its header) to send.

	Args:
		packet: The Packet.
		data: The bytes of the packet.
		data_size: Their size.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_set_packet_ref = lib_function (
	"packet_set_packet_ref", [PacketPointer, c_void_p, c_size_t], c_uint8,
	"""Sets a reference to a complete packet (with its header) to send.

	Args:
		packet: The Packet.
		data: The bytes of the packet, kept alive by the caller.
		packet_size: Their size.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_generate = lib_function (
	"packet_generate", [PacketPointer], c_uint8,
	"""Prepares the packet to be sent: its header and its data in a single buffer.

	Args:
		packet: The Packet.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_create_request = lib_function (
	"packet_create_request", [PacketType, c_uint32], PacketPointer,
	"""Creates a request packet without data, ready to be sent.

	Args:
		packet_type: A PACKET_TYPE_* value.
		request_type: The subtype of the packet.

	Returns:
		The Packet, released with packet_delete ().
	"""
)

packet_create_ping = lib_function (
	"packet_create_ping", [], PacketPointer,
	"""Creates a ping packet (PACKET_TYPE_TEST), ready to be sent.

	Returns:
		The Packet, released with packet_delete ().
	"""
)

packet_init_request = lib_function (
	"packet_init_request", [PacketPointer, PacketType, c_uint32], None,
	"""Initializes an allocated packet as a request.

	Args:
		packet: The Packet.
		packet_type: A PACKET_TYPE_* value.
		request_type: The subtype of the packet.
	"""
)

packet_init_ping = lib_function (
	"packet_init_ping", [PacketPointer], None,
	"""Initializes an allocated packet as a ping.

	Args:
		packet: The Packet.
	"""
)

packet_generate_request = lib_function (
	"packet_generate_request", [PacketType, c_uint32, c_void_p, c_size_t], PacketPointer,
	"""Creates a request packet with a copy of its data, ready to be sent.

	Args:
		packet_type: A PACKET_TYPE_* value.
		req_type: The subtype of the packet.
		data: The data, as bytes, or None.
		data_size: The size of the data.

	Returns:
		The Packet, released with packet_delete ().
	"""
)

packet_send = lib_function (
	"packet_send", [PacketPointer, c_int, POINTER (c_size_t), c_bool], c_uint8,
	"""Sends a packet with its network values.

	Args:
		packet: The Packet.
		flags: The flags of send ().
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		raw: True to send only the data, without the header.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_unsafe = lib_function (
	"packet_send_unsafe", [PacketPointer, c_int, POINTER (c_size_t), c_bool], c_uint8,
	"""Works like packet_send () without locking the write mutex of the socket.

	Args:
		packet: The Packet.
		flags: The flags of send ().
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		raw: True to send only the data, without the header.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_to = lib_function (
	"packet_send_to",
	[PacketPointer, POINTER (c_size_t), c_bool, c_void_p, c_void_p, c_void_p, c_void_p],
	c_uint8,
	"""Sends a packet to a destination.

	Args:
		packet: The Packet.
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		raw: True to send only the data, without the header.
		cerver: The cerver, or None.
		client: The client, or None.
		connection: The connection.
		lobby: The lobby, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_split = lib_function (
	"packet_send_split", [PacketPointer, c_int, POINTER (c_size_t)], c_uint8,
	"""Sends the header and the data of a packet without joining them in a buffer.

	Args:
		packet: The Packet.
		flags: The flags of send ().
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_to_split = lib_function (
	"packet_send_to_split",
	[PacketPointer, POINTER (c_size_t), c_void_p, c_void_p, c_void_p, c_void_p],
	c_uint8,
	"""Works like packet_send_split () to a destination.

	Args:
		packet: The Packet.
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		cerver: The cerver, or None.
		client: The client, or None.
		connection: The connection.
		lobby: The lobby, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_pieces = lib_function (
	"packet_send_pieces",
	[PacketPointer, POINTER (c_void_p), POINTER (c_size_t), c_uint32, c_int, POINTER (c_size_t)],
	c_uint8,
	"""Sends the header of a packet and then each one of the pieces.

	Args:
		packet: The Packet, with its header and its network values.
		pieces: An array of the addresses of the pieces.
		sizes: An array of their sizes.
		n_pieces: The number of pieces.
		flags: The flags of send ().
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_to_socket = lib_function (
	"packet_send_to_socket", [PacketPointer, c_void_p, c_int, POINTER (c_size_t), c_bool], c_uint8,
	"""Sends a packet to a socket.

	Args:
		packet: The Packet.
		socket: The Socket.
		flags: The flags of send ().
		total_sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		raw: True to send only the data, without the header.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_request = lib_function (
	"packet_send_request",
	[PacketType, c_uint32, c_void_p, c_void_p, c_void_p, c_void_p],
	c_uint8,
	"""Sends a packet of a type without data.

	Args:
		packet_type: A PACKET_TYPE_* value.
		request_type: The subtype of the packet.
		cerver: The cerver, or None.
		client: The client, or None.
		connection: The connection.
		lobby: The lobby, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_send_ping = lib_function (
	"packet_send_ping", [c_void_p, c_void_p, c_void_p, c_void_p], c_uint8,
	"""Sends a ping packet (PACKET_TYPE_TEST).

	Args:
		cerver: The cerver, or None.
		client: The client, or None.
		connection: The connection.
		lobby: The lobby, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_route_between_connections = lib_function (
	"packet_route_between_connections",
	[c_void_p, c_void_p, PacketHeaderPointer, POINTER (c_size_t)],
	c_uint8,
	"""Routes a packet from a connection to another one with splice ().

	Args:
		from: The connection that has the packet.
		to: The connection that gets it.
		header: The PacketHeader of the packet.
		sent: A pointer to a c_size_t that gets the bytes that were sent, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

packet_check = lib_function (
	"packet_check", [PacketPointer], c_bool,
	"""Returns if a packet has the protocol id and a compatible version of the application.

	Args:
		packet: The Packet.

	Returns:
		False for a bad packet.
	"""
)

def packet_send_data (
	packet_type: int, request_type: int, data: bytes | None,
	cerver: int | None, client: int | None, connection: int
) -> int:
	"""Creates, generates, sends and releases a packet with data.

	Args:
		packet_type: A PACKET_TYPE_* value.
		request_type: The subtype of the packet.
		data: The data, or None.
		cerver: The cerver, or None in a client.
		client: The client.
		connection: The connection.

	Returns:
		0 on success, 1 on error.
	"""
	result = 1

	packet = packet_create (packet_type, request_type, data, len (data) if (data) else 0)
	if (packet):
		packet_set_network_values (packet, cerver, client, connection, None)
		if (not packet_generate (packet)):
			result = packet_send (packet, 0, None, False)

		packet_delete (packet)

	return result

def packet_data (packet) -> bytes:
	"""Returns a copy of the data of a packet.

	Args:
		packet: A PacketPointer, like the packet of a HandlerData.

	Returns:
		The bytes of the data, empty if it has none.
	"""
	result = b""

	contents = packet.contents
	if (contents.data and contents.data_size):
		result = string_at (contents.data, contents.data_size)

	return result
