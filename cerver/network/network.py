"""Addresses: resolution of hosts, parsing of ips, comparison and options of sockets."""

from ctypes import POINTER, Structure, byref
from ctypes import c_int, c_int32, c_uint, c_uint16, c_uint64, c_long, c_bool, c_char, c_char_p, c_void_p
from ctypes import create_string_buffer
from typing import TypeAlias

from ..lib import lib_function, lib_take_c_string, lib_c_string, lib_text

__all__ = [
	"IP_TO_STR_LEN", "IPV6_TO_STR_LEN", "MAX_PORT_NUM", "MAX_UDP_PACKET_SIZE",
	"NETWORK_IPV4_MAPPED_OFFSET", "NETWORK_ZONE_SEPARATOR",
	"NETWORK_ADDRESS_STRING_SIZE", "NETWORK_MAX_RESOLVED_ADDRESSES",
	"Protocol", "PROTOCOL_TCP", "PROTOCOL_UDP",
	"SockaddrStorage", "SockaddrStoragePointer",
	"NetworkAddresses", "NetworkAddressesPointer",
	"network_hostname_to_ip_c_string", "network_resolve_address", "network_resolve_addresses",
	"network_parse_address", "sock_address_size", "sock_ip_is_mapped",
	"sock_set_ipv6_only", "sock_set_blocking",
	"sock_ip_to_string_actual", "sock_ip_to_string_c_string", "sock_ip_equal", "sock_ip_port",
	"sock_set_timeout", "sock_set_send_timeout", "sock_set_reusable", "sock_set_reusable_port",
	"network_hostname_to_ip", "network_address_text", "network_resolve", "network_parse"
]

IP_TO_STR_LEN = 16
IPV6_TO_STR_LEN = 46
MAX_PORT_NUM = 65535

# the payload of an IPv4 UDP datagram: 65535 - 20 (IP header) - 8 (UDP header)
MAX_UDP_PACKET_SIZE = 65507

# an IPv4 inside an IPv6 address (::ffff:a.b.c.d) starts after these bytes
NETWORK_IPV4_MAPPED_OFFSET = 12

# separates a link local IPv6 address from its zone (fe80::1%eth0)
NETWORK_ZONE_SEPARATOR = "%"

# INET6_ADDRSTRLEN + IF_NAMESIZE: the IPv6 text, the separator and the interface name
NETWORK_ADDRESS_STRING_SIZE = 62

# the most addresses that a host name resolves to that are kept
NETWORK_MAX_RESOLVED_ADDRESSES = 16

# the size and the alignment of a struct sockaddr_storage
SOCKADDR_STORAGE_SIZE = 128
SOCKADDR_STORAGE_HEADER_SIZE = 16

Protocol: TypeAlias = c_int # type: ignore

PROTOCOL_TCP = 6
PROTOCOL_UDP = 17

class SockaddrStorage (Structure):
	"""A ``struct sockaddr_storage``, an address of any family.

	Attributes:
		family: Its family (AF_INET or AF_INET6).
	"""

	_fields_ = [
		("family", c_uint16),
		("padding", c_char * 6),
		("alignment", c_uint64),
		("data", c_char * (SOCKADDR_STORAGE_SIZE - SOCKADDR_STORAGE_HEADER_SIZE))
	]

SockaddrStoragePointer: TypeAlias = POINTER (SockaddrStorage) # type: ignore

class NetworkAddresses (Structure):
	"""The addresses that a host resolves to, in the order to try them, ``NetworkAddresses``.

	Attributes:
		count: How many addresses it has.
		addresses: The addresses, the first count are valid.
	"""

	_fields_ = [
		("count", c_uint),
		("addresses", SockaddrStorage * NETWORK_MAX_RESOLVED_ADDRESSES)
	]

NetworkAddressesPointer: TypeAlias = POINTER (NetworkAddresses) # type: ignore

network_hostname_to_ip_c_string = lib_function (
	"network_hostname_to_ip", [c_char_p], c_void_p,
	"""Returns the ip of a host name in a new C string, use network_hostname_to_ip ().

	Args:
		hostname: The host name, as bytes.

	Returns:
		The address of the ip that the caller frees, None if it was not found.
	"""
)

network_resolve_address = lib_function (
	"network_resolve_address", [c_char_p, c_uint16, c_bool, SockaddrStoragePointer], c_uint,
	"""Resolves a literal ip or a host name into an address with the port.

	Args:
		host: The ip or the host name, as bytes.
		port: The port.
		prefer_ipv6: An address of this family is taken first.
		address: The SockaddrStorage that gets the address.

	Returns:
		0 on success, 1 if the host could not be resolved.
	"""
)

network_resolve_addresses = lib_function (
	"network_resolve_addresses", [c_char_p, c_uint16, c_bool, c_int, NetworkAddressesPointer], c_uint,
	"""Resolves a literal ip (with its zone) or a host name into every address of the protocol.

	The families alternate, starting with the one of prefer_ipv6, and each one keeps the
	order of getaddrinfo () (RFC 6724). Use network_resolve () for a list of texts.

	Args:
		host: The ip or the host name, as bytes.
		port: The port.
		prefer_ipv6: True to start with the IPv6 addresses.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.
		addresses: The NetworkAddresses that gets them.

	Returns:
		0 on success, 1 if the host could not be resolved.
	"""
)

network_parse_address = lib_function (
	"network_parse_address", [c_char_p, c_uint16, SockaddrStoragePointer], c_uint,
	"""Parses a literal IPv4 or IPv6 address, without a port, into an address.

	A link local IPv6 address can have its zone, as an interface name or index (fe80::1%eth0).

	Args:
		ip: The ip, as bytes.
		port: The port.
		address: The SockaddrStorage that gets the address.

	Returns:
		0 on success, 1 if it is not a valid ip.
	"""
)

sock_address_size = lib_function (
	"sock_address_size", [SockaddrStoragePointer], c_uint,
	"""Returns the size of the address of its family, the size that bind () and connect () expect.

	Args:
		address: The SockaddrStorage.

	Returns:
		The size in bytes.
	"""
)

sock_ip_is_mapped = lib_function (
	"sock_ip_is_mapped", [SockaddrStoragePointer], c_bool,
	"""Returns if an address is an IPv4 inside an IPv6 address (::ffff:a.b.c.d).

	Args:
		address: The SockaddrStorage.

	Returns:
		True for a mapped IPv4.
	"""
)

sock_set_ipv6_only = lib_function (
	"sock_set_ipv6_only", [c_int, c_bool], c_int,
	"""Sets IPV6_V6ONLY in an IPv6 socket.

	Args:
		sock_fd: The socket.
		ipv6_only: False accepts IPv4 connections too (dual stack).

	Returns:
		0 on success, 1 on error.
	"""
)

sock_set_blocking = lib_function (
	"sock_set_blocking", [c_int32, c_bool], c_bool,
	"""Sets if a socket blocks, False sets O_NONBLOCK.

	Args:
		fd: The socket.
		blocking: True to block.

	Returns:
		True on success, False on error.
	"""
)

sock_ip_to_string_actual = lib_function (
	"sock_ip_to_string_actual", [SockaddrStoragePointer, c_void_p], c_uint,
	"""Writes the ip of an address in a buffer of at least NETWORK_ADDRESS_STRING_SIZE bytes.

	A mapped IPv4 is written as the IPv4, and an IPv6 with a scope id with its zone.

	Args:
		address: The SockaddrStorage.
		ip_buffer: A writable buffer.

	Returns:
		0 on success, 1 on error.
	"""
)

sock_ip_to_string_c_string = lib_function (
	"sock_ip_to_string", [SockaddrStoragePointer], c_void_p,
	"""Returns the ip of an address in a new C string, use network_address_text ().

	Args:
		address: The SockaddrStorage.

	Returns:
		The address of the ip that the caller frees, None on error.
	"""
)

sock_ip_equal = lib_function (
	"sock_ip_equal", [SockaddrStoragePointer, SockaddrStoragePointer], c_bool,
	"""Returns if two addresses have the same ip, port and zone.

	A mapped IPv4 (::ffff:a.b.c.d) is equal to the IPv4.

	Args:
		a: A SockaddrStorage.
		b: A SockaddrStorage.

	Returns:
		True if they are equal.
	"""
)

sock_ip_port = lib_function (
	"sock_ip_port", [SockaddrStoragePointer], c_uint16,
	"""Returns the port of an address, in host byte order.

	Args:
		address: The SockaddrStorage.

	Returns:
		The port, 0 for an unknown family.
	"""
)

sock_set_timeout = lib_function (
	"sock_set_timeout", [c_int, c_long], c_int,
	"""Sets a timeout for the receives of a socket (SO_RCVTIMEO).

	Args:
		sock_fd: The socket.
		timeout: The timeout in seconds.

	Returns:
		0 on success, 1 on error.
	"""
)

sock_set_send_timeout = lib_function (
	"sock_set_send_timeout", [c_int, c_long], c_int,
	"""Sets a timeout for the sends of a socket (SO_SNDTIMEO).

	Args:
		sock_fd: The socket.
		timeout: The timeout in seconds.

	Returns:
		0 on success, 1 on error.
	"""
)

sock_set_reusable = lib_function (
	"sock_set_reusable", [c_int], c_int,
	"""Sets SO_REUSEADDR in a socket.

	Args:
		sock_fd: The socket.

	Returns:
		0 on success, 1 on error.
	"""
)

sock_set_reusable_port = lib_function (
	"sock_set_reusable_port", [c_int], c_int,
	"""Sets SO_REUSEPORT in a socket, so other sockets can bind its port.

	Args:
		sock_fd: The socket.

	Returns:
		0 on success, 1 on error.
	"""
)

def network_hostname_to_ip (hostname: str | bytes) -> str | None:
	"""Returns the ip of a host name.

	Args:
		hostname: The host name.

	Returns:
		The ip, None if it was not found.
	"""
	return lib_text (lib_take_c_string (network_hostname_to_ip_c_string (lib_c_string (hostname))))

def network_address_text (address: SockaddrStorage) -> tuple:
	"""Returns the ip and the port of an address.

	Args:
		address: A SockaddrStorage.

	Returns:
		A tuple (ip, port), with the ip as text with its zone.
	"""
	buffer = create_string_buffer (NETWORK_ADDRESS_STRING_SIZE)
	sock_ip_to_string_actual (byref (address), buffer)

	return (lib_text (buffer.value), sock_ip_port (byref (address)))

def network_resolve (
	host: str | bytes, port: int,
	prefer_ipv6: bool = False, protocol: int = PROTOCOL_TCP
) -> list:
	"""Resolves a literal ip or a host name into every address of the protocol.

	Args:
		host: The ip or the host name.
		port: The port.
		prefer_ipv6: True to start with the IPv6 addresses.
		protocol: PROTOCOL_TCP or PROTOCOL_UDP.

	Returns:
		The (ip, port) tuples in the order to try them, empty if the host could not be resolved.
	"""
	result = []

	addresses = NetworkAddresses ()
	if (not network_resolve_addresses (lib_c_string (host), port, prefer_ipv6, protocol, byref (addresses))):
		for index in range (addresses.count):
			result.append (network_address_text (addresses.addresses[index]))

	return result

def network_parse (ip: str | bytes, port: int = 0) -> tuple | None:
	"""Parses a literal ip and returns it in its canonical text.

	Args:
		ip: The ip, with its zone when it is link local.
		port: The port.

	Returns:
		A tuple (ip, port), None if it is not a valid ip.
	"""
	result = None

	address = SockaddrStorage ()
	if (not network_parse_address (lib_c_string (ip), port, byref (address))):
		result = network_address_text (address)

	return result
