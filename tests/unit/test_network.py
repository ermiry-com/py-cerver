"""Unit tests for the addresses: resolution, parsing, mapped IPv4 and zones."""

import ctypes
import pytest

from cerver.network import network_resolve, network_parse, network_hostname_to_ip
from cerver.network import network_parse_address, sock_ip_equal, sock_ip_is_mapped, sock_address_size
from cerver.network import SockaddrStorage, PROTOCOL_UDP

pytestmark = [pytest.mark.unit]

PORT = 7000

IPV4_SIZE = 16
IPV6_SIZE = 28

def parsed (ip: str) -> SockaddrStorage:
	address = SockaddrStorage ()
	assert network_parse_address (ip.encode ("utf-8"), PORT, ctypes.byref (address)) == 0
	return address

class TestNetwork:

	@pytest.mark.parametrize ("ip", ["127.0.0.1", "::1", "10.1.2.3"])
	def test_parse (self, ip):
		assert network_parse (ip, PORT) == (ip, PORT)

	@pytest.mark.parametrize ("ip", ["", "not an ip", "300.1.1.1", "127.0.0.1:80"])
	def test_parse_invalid (self, ip):
		assert network_parse (ip) is None

	def test_mapped_ipv4_is_written_as_the_ipv4 (self):
		assert network_parse ("::ffff:10.0.0.1", PORT) == ("10.0.0.1", PORT)

	def test_mapped_ipv4_equals_the_ipv4 (self):
		mapped = parsed ("::ffff:10.0.0.1")
		assert sock_ip_is_mapped (ctypes.byref (mapped))
		assert sock_ip_equal (ctypes.byref (mapped), ctypes.byref (parsed ("10.0.0.1")))
		assert not sock_ip_equal (ctypes.byref (mapped), ctypes.byref (parsed ("10.0.0.2")))

	def test_address_size (self):
		assert sock_address_size (ctypes.byref (parsed ("127.0.0.1"))) == IPV4_SIZE
		assert sock_address_size (ctypes.byref (parsed ("::1"))) == IPV6_SIZE

	def test_resolve_localhost (self):
		addresses = network_resolve ("localhost", PORT, protocol=PROTOCOL_UDP)
		assert ("127.0.0.1", PORT) in addresses

	def test_resolve_prefers_its_family (self):
		assert network_resolve ("::1", PORT, prefer_ipv6=True)[0] == ("::1", PORT)

	def test_resolve_unknown_host (self):
		assert network_resolve ("pycerver.invalid", PORT) == []

	def test_hostname_to_ip (self):
		assert network_hostname_to_ip ("localhost") in ("127.0.0.1", "::1")
