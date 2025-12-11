"""The C clients of clients/ against the servers of legacy/, each pair like run.sh ran them.

The clients are compiled in the test image (/opt/pycerver/clients) against its libcerver,
they run from the root of the package (they read ./tests/data and ./images) and each one
exits 0 only when every response of its server had the status and the body it expects.
"""

import pytest
import subprocess
import time
from pathlib import Path

from e2e.conftest import output
from e2e.conftest import start
from e2e.conftest import stop
from e2e.conftest import wait_listening

pytestmark = [pytest.mark.e2e]

PACKAGE_ROOT = Path (__file__).resolve ().parent.parent.parent
LEGACY_ROOT = PACKAGE_ROOT / "tests" / "legacy"

CLIENTS = Path ("/opt/pycerver/clients/client")

WEB_PORT = 8080
TCP_PORT = 7000

# the ping server must be in its accept () before a signal can stop it
SETTLE_SECONDS = 1

CLIENT_SECONDS = 120

# the client of each server
WEB_PAIRS = {
	"web": "web/web.py",
	"query": "web/query.py",
	"json": "web/responses.py",
	"auth": "web/auth.py",
	"api": "web/api.py",
	"multi": "web/multi.py",
	"upload": "web/upload.py",
	"multiple": "web/multiple.py",
	"jobs": "web/jobs.py",
	"worker": "web/worker.py",
	"admin": "web/admin.py",
	"validation": "web/validation.py",
	"wrapper": "web/wrapper.py"
}

def run_pair (server: str, port: int, client: Path) -> None:
	"""Starts the server, runs its client and stops the server, failing with both outputs."""
	process = start (["python3", "-u", server], LEGACY_ROOT)

	listening = wait_listening (process, port)
	assert listening, output (process)

	time.sleep (SETTLE_SECONDS)

	result = subprocess.run (
		[str (client)], cwd=PACKAGE_ROOT,
		capture_output=True, text=True, errors="replace", timeout=CLIENT_SECONDS
	)

	code = stop (process)

	assert result.returncode == 0, f"{client.name} exited {result.returncode}:\n{result.stdout[-4000:]}\n{result.stderr[-2000:]}\nserver:\n{output (process)}"
	assert code is not None, f"{server} did not stop:\n{output (process)}"

class TestClients:

	def test_every_client_was_compiled (self):
		for client in WEB_PAIRS:
			assert (CLIENTS / "web" / client).is_file ()

	def test_ping (self):
		run_pair ("cerver/ping.py", TCP_PORT, CLIENTS / "ping")

	@pytest.mark.parametrize ("client", sorted (WEB_PAIRS))
	def test_web (self, client):
		run_pair (WEB_PAIRS[client], WEB_PORT, CLIENTS / "web" / client)
