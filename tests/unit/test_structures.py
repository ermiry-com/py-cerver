"""The structures that the package mirrors with ctypes have the layout of the structs of cerver.

The probe of the test image prints the sizeof and the offsetof of each struct compiled against
the headers. A structure that misses a field of its C struct has another size, so a field after
the missing one is read from the wrong bytes: the Job without its id read its work from the id,
and HttpOrigin declared a pointer where C has char value[256].
"""

import ctypes
import pytest

from cerver.client import ClientEventData, ClientErrorData
from cerver.core import Packet, PacketHeader, PacketVersion, PacketsPerType, ProtocolVersion
from cerver.core import ConnectionCustomReceiveData
from cerver.core import AuthData, AuthMethod, CerverErrorEventData, CerverEventData
from cerver.core import CerverUpdate, FileHeader, HandlerData, HandlerStats, RequestStats
from cerver.core import FileSystemStats, SystemCpuSample, SystemLoad, SystemMemory, SystemProcess
from cerver.games import LobbyCreate, LobbyJoin, LobbyRequest
from cerver.games import LobbyPlayerSummary, LobbySettingsSummary, LobbySummary
from cerver.http import BytesRange, HttpOrigin, HttpProxyNetwork
from cerver.http import HttpWebSocketDeflateOptions, HttpWebSocketHandlers, HttpWebSocketUpgrade
from cerver.network import NetworkAddresses, SockaddrStorage, Timespec
from cerver.threads import Job, JobQueueStats, ThpoolStats, WorkerManagerStats
from cerver.types import String
from cerver.utils import Histogram

from probes import PROBE_VALUES, PROBE_SIZE, PROBE_OFFSET

pytestmark = [pytest.mark.unit]

STRUCTURES = {
	"String": String,
	"ProtocolVersion": ProtocolVersion, "PacketVersion": PacketVersion,
	"PacketHeader": PacketHeader, "Packet": Packet, "PacketsPerType": PacketsPerType,
	"HandlerData": HandlerData, "CerverUpdate": CerverUpdate,
	"CerverEventData": CerverEventData, "CerverErrorEventData": CerverErrorEventData,
	"FileHeader": FileHeader, "AuthData": AuthData, "AuthMethod": AuthMethod,
	"SockaddrStorage": SockaddrStorage, "NetworkAddresses": NetworkAddresses, "Timespec": Timespec,
	"ConnectionCustomReceiveData": ConnectionCustomReceiveData,
	"ClientEventData": ClientEventData, "ClientErrorData": ClientErrorData,
	"Job": Job, "ThpoolStats": ThpoolStats, "JobQueueStats": JobQueueStats,
	"WorkerManagerStats": WorkerManagerStats,
	"Histogram": Histogram, "RequestStats": RequestStats, "HandlerStats": HandlerStats,
	"HttpOrigin": HttpOrigin, "BytesRange": BytesRange, "HttpProxyNetwork": HttpProxyNetwork,
	"HttpWebSocketUpgrade": HttpWebSocketUpgrade, "HttpWebSocketHandlers": HttpWebSocketHandlers,
	"HttpWebSocketDeflateOptions": HttpWebSocketDeflateOptions,
	"FileSystemStats": FileSystemStats, "SystemMemory": SystemMemory, "SystemLoad": SystemLoad,
	"SystemCpuSample": SystemCpuSample, "SystemProcess": SystemProcess,
	"LobbyCreate": LobbyCreate, "LobbyJoin": LobbyJoin, "LobbyRequest": LobbyRequest,
	"LobbyPlayerSummary": LobbyPlayerSummary, "LobbySettingsSummary": LobbySettingsSummary,
	"LobbySummary": LobbySummary
}

C_SIZES = PROBE_VALUES[PROBE_SIZE]
C_OFFSETS = PROBE_VALUES[PROBE_OFFSET]

class TestStructures:

	def test_every_structure_is_probed (self):
		assert set (STRUCTURES) == set (C_SIZES)

	@pytest.mark.parametrize ("name", sorted (STRUCTURES))
	def test_size (self, name):
		assert ctypes.sizeof (STRUCTURES[name]) == C_SIZES[name]

	@pytest.mark.parametrize ("field", sorted (C_OFFSETS))
	def test_offset (self, field):
		name, member = field.split (".")
		assert getattr (STRUCTURES[name], member).offset == C_OFFSETS[field]

	def test_packet_pool_fields_are_last (self):
		names = [name for name, _ in Packet._fields_]
		assert names[-4:] == ["release", "release_args", "data_class", "recycle_next"]
