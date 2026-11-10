"""The peers of an UDP cerver: the logical connection of each address that sends datagrams."""

from ctypes import c_int, c_void_p, c_uint32, c_size_t
from typing import TypeAlias

from ..lib import lib_function

from .network import NETWORK_ADDRESS_STRING_SIZE

__all__ = [
	"CERVER_UDP_DEFAULT_PEER_TIMEOUT", "CERVER_UDP_DEFAULT_MAX_PEERS",
	"CERVER_UDP_PEERS_CHECK_INTERVAL", "CERVER_UDP_PEER_KEY_SIZE",
	"CERVER_UDP_AMPLIFICATION_FACTOR",
	"UdpDatagram", "UDP_DATAGRAM_INVALID", "UDP_DATAGRAM_PLAIN", "UDP_DATAGRAM_TOKEN",
	"UdpPeerState",
	"UDP_PEER_STATE_PENDING", "UDP_PEER_STATE_OPEN", "UDP_PEER_STATE_AUTHENTICATED",
	"cerver_set_udp_peer_timeout", "cerver_set_udp_max_peers", "cerver_udp_peers_count"
]

# a peer that does not send anything in these secs is removed
CERVER_UDP_DEFAULT_PEER_TIMEOUT = 16

# the peers that an UDP cerver keeps at the same time
CERVER_UDP_DEFAULT_MAX_PEERS = 1024

# how often the receive loop removes the inactive peers, in secs
CERVER_UDP_PEERS_CHECK_INTERVAL = 1

# the ip with its zone and the port of a peer
CERVER_UDP_PEER_KEY_SIZE = NETWORK_ADDRESS_STRING_SIZE + 8

# the answers to a peer that did not prove its address are up to these times what it sent
CERVER_UDP_AMPLIFICATION_FACTOR = 4

# what follows the packet of a datagram
UdpDatagram: TypeAlias = c_int # type: ignore

UDP_DATAGRAM_INVALID = 0
UDP_DATAGRAM_PLAIN = 1
UDP_DATAGRAM_TOKEN = 2

UdpPeerState: TypeAlias = c_int # type: ignore

UDP_PEER_STATE_PENDING = 0
UDP_PEER_STATE_OPEN = 1
UDP_PEER_STATE_AUTHENTICATED = 2

cerver_set_udp_peer_timeout = lib_function (
	"cerver_set_udp_peer_timeout", [c_void_p, c_uint32], None,
	"""Sets the seconds without datagrams after which a peer of an UDP cerver is removed.

	Args:
		cerver: The cerver.
		peer_timeout: The seconds, 0 keeps the peers until the cerver ends,
			CERVER_UDP_DEFAULT_PEER_TIMEOUT by default.
	"""
)

cerver_set_udp_max_peers = lib_function (
	"cerver_set_udp_max_peers", [c_void_p, c_uint32], None,
	"""Sets the peers that an UDP cerver keeps at the same time.

	Args:
		cerver: The cerver.
		max_peers: The number of peers, 0 does not limit them, CERVER_UDP_DEFAULT_MAX_PEERS by default.
	"""
)

cerver_udp_peers_count = lib_function (
	"cerver_udp_peers_count", [c_void_p], c_size_t,
	"""Returns the peers of an UDP cerver, the pending ones too.

	Args:
		cerver: The cerver.

	Returns:
		The number of peers.
	"""
)
