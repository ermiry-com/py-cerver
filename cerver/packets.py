from ctypes import c_int, c_uint8, c_uint16, c_uint32, c_size_t, c_void_p, c_char_p, c_bool, Structure

from .lib import lib

PacketType = c_int

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

ProtocolID = c_uint32

class ProtocolVersion (Structure):
	_fields_ = [
		("major", c_uint16),
		("minor", c_uint16)
	]

class PacketVersion (Structure):
	_fields_ = [
		("protocol_id", ProtocolID),
		("protocol_version", ProtocolVersion)
	]

class PacketHeader (Structure):
	_fields_ = [
		("packet_type", PacketType),
		("packet_size", c_size_t),

		("handler_id", c_uint8),

		("request_type", c_uint32),

		("sock_fd", c_uint16)
	]

class Packet (Structure):
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
		("packet_ref", c_bool)
	]

packet_send_request = lib.packet_send_request
packet_send_request.argtypes = [PacketType, c_uint32, c_void_p, c_void_p, c_void_p, c_void_p]
packet_send_request.restype = c_uint8
