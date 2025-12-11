"""The servers of legacy/web/ and legacy/cerver/, the ones the C clients of clients/ use.

Each one is started from legacy/, and must listen, answer an HTTP request (the TCP ping
server only has to listen) and stop with SIGINT in time.
"""

import pytest
import time
from pathlib import Path

from e2e.conftest import e2e_raw
from e2e.conftest import output
from e2e.conftest import start
from e2e.conftest import stop
from e2e.conftest import wait_listening

pytestmark = [pytest.mark.e2e]

LEGACY_ROOT = Path (__file__).resolve ().parent.parent / "legacy"

WEB_PORT = 8080
TCP_PORT = 7000

SETTLE_SECONDS = 1

HTTP_STATUS_LINE = b"HTTP/1.1 "

HTTP_REQUEST = b"GET / HTTP/1.1\r\nHost: localhost\r\n\r\n"

# the modules of legacy/web/ that the servers import, they are not servers
WEB_HELPERS = ("users.py",)

WEB_SERVERS = sorted (
	path.name for path in (LEGACY_ROOT / "web").glob ("*.py") if (path.name not in WEB_HELPERS)
)

class TestLegacyServers:

	def test_every_server_was_found (self):
		assert "web.py" in WEB_SERVERS

	@pytest.mark.parametrize ("script", WEB_SERVERS)
	def test_web_server (self, script):
		process = start (["python3", "-u", f"web/{script}"], LEGACY_ROOT)

		listening = wait_listening (process, WEB_PORT)
		response = e2e_raw (HTTP_REQUEST, WEB_PORT) if (listening) else b""
		code = stop (process)

		assert listening, output (process)
		assert response.startswith (HTTP_STATUS_LINE), output (process)
		assert code is not None, f"{script} did not stop:\n{output (process)}"

	def test_tcp_ping_server (self):
		process = start (["python3", "-u", "cerver/ping.py"], LEGACY_ROOT)

		listening = wait_listening (process, TCP_PORT)

		# the signal stops a cerver started in the main thread only when it interrupts accept (),
		# one that arrives before it is lost; the web servers answered a request, so they were already in their loop
		time.sleep (SETTLE_SECONDS)

		code = stop (process)

		assert listening, output (process)
		assert code is not None, f"ping.py did not stop:\n{output (process)}"
