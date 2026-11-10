"""The trusted proxies whose X-Forwarded-For and X-Real-IP give the address of the client."""

from ctypes import POINTER, Structure, byref
from ctypes import c_bool, c_char_p, c_int, c_size_t, c_ubyte, c_uint, c_uint8, c_void_p
from typing import TypeAlias

from ..lib import lib_function, lib_c_string

__all__ = [
	"HTTP_PROXY_ADDRESS_SIZE",
	"HttpTrustedProxies",
	"HTTP_TRUSTED_PROXIES_NONE", "HTTP_TRUSTED_PROXIES_LIST",
	"HTTP_TRUSTED_PROXIES_PRIVATE", "HTTP_TRUSTED_PROXIES_ALL",
	"HTTP_CERVER_DEFAULT_TRUSTED_PROXIES",
	"HttpProxyNetwork", "HttpProxyNetworkPointer",
	"http_trusted_proxies_string", "http_trusted_proxies_description",
	"http_proxy_network_parse", "http_proxy_network_contains", "http_proxy_is_trusted",
	"http_cerver_set_trusted_proxies", "http_cerver_add_trusted_proxy",
	"http_proxy_network_has"
]

# the bytes of an IPv6 address, an IPv4 one uses the first 4
HTTP_PROXY_ADDRESS_SIZE = 16

# from which peers X-Forwarded-For and X-Real-IP are used to find the address of the client
HttpTrustedProxies: TypeAlias = c_int # type: ignore

HTTP_TRUSTED_PROXIES_NONE = 0
HTTP_TRUSTED_PROXIES_LIST = 1
HTTP_TRUSTED_PROXIES_PRIVATE = 2
HTTP_TRUSTED_PROXIES_ALL = 3

HTTP_CERVER_DEFAULT_TRUSTED_PROXIES = HTTP_TRUSTED_PROXIES_NONE

class HttpProxyNetwork (Structure):
	"""An IPv4 or IPv6 network, ``HttpProxyNetwork``.

	Attributes:
		family: AF_INET or AF_INET6.
		address: The bytes of the address.
		prefix: The bits of the prefix.
	"""

	_fields_ = [
		("family", c_int),
		("address", c_ubyte * HTTP_PROXY_ADDRESS_SIZE),
		("prefix", c_uint)
	]

HttpProxyNetworkPointer: TypeAlias = POINTER (HttpProxyNetwork) # type: ignore

http_trusted_proxies_string = lib_function (
	"http_trusted_proxies_string", [HttpTrustedProxies], c_char_p,
	"""Returns the name of a trusted proxies mode.

	Args:
		trusted_proxies: An HTTP_TRUSTED_PROXIES_* value.

	Returns:
		The name, as bytes.
	"""
)

http_trusted_proxies_description = lib_function (
	"http_trusted_proxies_description", [HttpTrustedProxies], c_char_p,
	"""Returns the description of a trusted proxies mode.

	Args:
		trusted_proxies: An HTTP_TRUSTED_PROXIES_* value.

	Returns:
		The description, as bytes.
	"""
)

http_proxy_network_parse = lib_function (
	"http_proxy_network_parse", [c_char_p, HttpProxyNetworkPointer], c_bool,
	"""Parses a network in CIDR notation, an address without a prefix is a single host.

	Args:
		cidr: The network, as bytes, like b"172.16.0.0/12" or b"fc00::/7".
		network: The HttpProxyNetwork that gets it.

	Returns:
		True on success.
	"""
)

http_proxy_network_contains = lib_function (
	"http_proxy_network_contains", [HttpProxyNetworkPointer, c_char_p, c_size_t], c_bool,
	"""Returns if an address is inside a network.

	Args:
		network: The HttpProxyNetwork.
		ip: The IPv4 or IPv6 address, as bytes.
		ip_length: Its length.

	Returns:
		True if it is inside.
	"""
)

http_proxy_is_trusted = lib_function (
	"http_proxy_is_trusted", [c_void_p, c_char_p, c_size_t], c_bool,
	"""Returns if an HTTP cerver trusts the forwarded headers sent by an address.

	Args:
		http_cerver: The HttpCerver.
		ip: The address of the peer, as bytes.
		ip_length: Its length.

	Returns:
		True if it is a trusted proxy.
	"""
)

http_cerver_set_trusted_proxies = lib_function (
	"http_cerver_set_trusted_proxies", [c_void_p, HttpTrustedProxies], None,
	"""Sets from which peers X-Forwarded-For and X-Real-IP give the address of the client.

	Args:
		http_cerver: The HttpCerver.
		trusted_proxies: HTTP_TRUSTED_PROXIES_NONE (the default), HTTP_TRUSTED_PROXIES_LIST
			(the networks of http_cerver_add_trusted_proxy ()), HTTP_TRUSTED_PROXIES_PRIVATE
			or HTTP_TRUSTED_PROXIES_ALL.
	"""
)

http_cerver_add_trusted_proxy = lib_function (
	"http_cerver_add_trusted_proxy", [c_void_p, c_char_p], c_uint8,
	"""Adds a network in CIDR notation to the trusted proxies, an invalid one stops the cerver when it starts.

	Args:
		http_cerver: The HttpCerver.
		cidr: The network, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

def http_proxy_network_has (cidr: str | bytes, ip: str | bytes) -> bool:
	"""Returns if an address is inside a network in CIDR notation.

	Args:
		cidr: The network, like "10.0.0.0/8".
		ip: The address.

	Returns:
		True if the network is valid and the address is inside.

	Raises:
		ValueError: If the network is not valid.
	"""
	network = HttpProxyNetwork ()
	if (not http_proxy_network_parse (lib_c_string (cidr), byref (network))):
		raise ValueError (f"Invalid network {cidr!r}")

	address = lib_c_string (ip)
	return bool (http_proxy_network_contains (byref (network), address, len (address)))
