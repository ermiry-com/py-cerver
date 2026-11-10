"""The requests of the C clients of clients/ made from Python against the same servers of legacy/.

They check the same status of each request as the clients, and the bodies that the clients only
print, so a server that answers with the right status and a wrong body fails here.
"""

import json
import pytest
import re
import uuid
from pathlib import Path

from e2e.conftest import output
from e2e.conftest import start
from e2e.conftest import stop
from e2e.conftest import wait_listening
from e2e.conftest import SERVER_ADDRESS, REQUEST_SECONDS

import http.client

pytestmark = [pytest.mark.e2e]

TESTS_ROOT = Path (__file__).resolve ().parent.parent
LEGACY_ROOT = TESTS_ROOT / "legacy"

IMAGE = LEGACY_ROOT / "web" / "img" / "ermiry.png"
SECOND_IMAGE = LEGACY_ROOT / "web" / "img" / "github.jpeg"

WEB_PORT = 8080

STATUS_OK = 200
STATUS_BAD_REQUEST = 400
STATUS_UNAUTHORIZED = 401
STATUS_INTERNAL_SERVER_ERROR = 500

# the token of the client of the auth server, signed with the keys of legacy/web/keys
AUTH_TOKEN = re.search (
	r'token = \{ "(Bearer [^"]+)" \}', (TESTS_ROOT / "clients" / "web" / "auth.c").read_text ()
).group (1)

FORM_TYPE = "application/x-www-form-urlencoded"

def request (method: str, path: str, body: bytes | None = None, headers: dict | None = None) -> tuple:
	"""Sends a request to the legacy server and returns its status and its body."""
	connection = http.client.HTTPConnection (SERVER_ADDRESS, WEB_PORT, timeout=REQUEST_SECONDS)
	connection.request (method, path, body=body, headers=headers or dict ())

	response = connection.getresponse ()
	result = (response.status, response.read ())
	connection.close ()

	return result

def multipart (fields: dict, files: dict) -> tuple:
	"""Encodes a multipart/form-data body, files maps a field to a path."""
	boundary = uuid.uuid4 ().hex
	parts = []

	for name, value in fields.items ():
		parts.append (
			f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n".encode ("utf-8")
		)

	for name, path in files.items ():
		parts.append (
			f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"; filename=\"{path.name}\"\r\n"
			"Content-Type: application/octet-stream\r\n\r\n".encode ("utf-8") + path.read_bytes () + b"\r\n"
		)

	parts.append (f"--{boundary}--\r\n".encode ("utf-8"))

	return (b"".join (parts), {"Content-Type": f"multipart/form-data; boundary={boundary}"})

def post_multipart (path: str, fields: dict, files: dict | None = None) -> tuple:
	"""Posts a multipart body."""
	body, headers = multipart (fields, files or dict ())
	return request ("POST", path, body, headers)

def body_json (body: bytes):
	return json.loads (body.decode ("utf-8"))

@pytest.fixture
def legacy (request):
	"""Starts the legacy server of the test (its marker legacy_server) and stops it after the test."""
	script = request.node.get_closest_marker ("legacy_server").args[0]
	process = start (["python3", "-u", script], LEGACY_ROOT)

	if (not wait_listening (process, WEB_PORT)):
		stop (process)
		pytest.fail (f"{script} did not listen:\n{output (process)}")

	yield process

	assert stop (process) is not None, f"{script} did not stop:\n{output (process)}"

@pytest.mark.legacy_server ("web/web.py")
class TestWeb:

	def test_render (self, legacy):
		status, body = request ("GET", "/render")
		assert status == STATUS_OK
		assert body == (LEGACY_ROOT / "web" / "public" / "index.html").read_bytes ()

	def test_render_text (self, legacy):
		status, body = request ("GET", "/render/text")
		assert (status == STATUS_OK) and (b"text_handler () works!" in body)

	def test_render_json (self, legacy):
		status, body = request ("GET", "/render/json")
		assert (status == STATUS_OK) and (body_json (body) == {"msg": "okay"})

	def test_static_file (self, legacy):
		assert request ("GET", "/index.html")[0] == STATUS_OK

@pytest.mark.legacy_server ("web/query.py")
class TestQuery:

	@pytest.mark.parametrize ("path, status", [
		("/query/value?value=test", STATUS_OK),
		("/query/value?hola=test", STATUS_BAD_REQUEST),
		("/query/value", STATUS_BAD_REQUEST),
		("/query/int?value=78", STATUS_OK),
		("/query/int?test=78", STATUS_BAD_REQUEST),
		("/query/int?value=test", STATUS_BAD_REQUEST),
		("/query/float?value=8.78", STATUS_OK),
		("/query/float?hola=8.78", STATUS_BAD_REQUEST),
		("/query/float?hola=test", STATUS_BAD_REQUEST),
		("/query/bool?value=True", STATUS_OK),
		("/query/bool", STATUS_BAD_REQUEST),
		("/query/bool?value=hola", STATUS_BAD_REQUEST)
	])
	def test_query (self, legacy, path, status):
		assert request ("GET", path)[0] == status

@pytest.mark.legacy_server ("web/responses.py")
class TestResponses:

	@pytest.mark.parametrize ("path, expected", [
		("/json", {"msg": "okay"}),
		("/json/create", {"msg": "okay"}),
		("/json/int", {"integer": 18}),
		("/json/int/create", {"integer": 18}),
		("/json/large", {"large": 1800000}),
		("/json/large/create", {"large": 1800000}),
		("/json/bool", {"bool": True}),
		("/json/bool/create", {"bool": True}),
		("/json/msg", {"msg": "oki"}),
		("/json/msg/create", {"msg": "oki"}),
		("/json/key", {"key": "value"}),
		("/json/custom", {"oki": "doki"}),
		("/json/custom/create", {"oki": "doki"}),
		("/json/reference", {"oki": "doki"}),
		("/json/reference/create", {"oki": "doki"})
	])
	def test_json (self, legacy, path, expected):
		status, body = request ("GET", path)
		assert (status == STATUS_OK) and (body_json (body) == expected)

	@pytest.mark.parametrize ("path", ["/json/real", "/json/real/create"])
	def test_real (self, legacy, path):
		status, body = request ("GET", path)
		assert (status == STATUS_OK) and (body_json (body)["real"] == pytest.approx (18.123))

	@pytest.mark.parametrize ("path", ["/json/error", "/json/error/create"])
	def test_error (self, legacy, path):
		status, body = request ("GET", path)
		assert (status == STATUS_BAD_REQUEST) and (body_json (body) == {"error": "bad"})

	@pytest.mark.parametrize ("name", ["small.json", "big.json"])
	def test_post_json (self, legacy, name):
		path = "/json" if (name == "small.json") else "/json/big"
		status, body = request ("POST", path, (TESTS_ROOT / "data" / name).read_bytes (), {"Content-Type": "application/json"})
		assert (status == STATUS_OK) and (body_json (body) == {"oki": "doki"})

@pytest.mark.legacy_server ("web/auth.py")
class TestAuth:

	def test_public_route (self, legacy):
		assert request ("GET", "/test")[0] == STATUS_OK

	def test_token (self, legacy):
		assert request ("GET", "/auth/token", headers={"Authorization": AUTH_TOKEN})[0] == STATUS_OK

	def test_without_token (self, legacy):
		assert request ("GET", "/auth/token")[0] == STATUS_UNAUTHORIZED

	@pytest.mark.parametrize ("key, status", [("okay", STATUS_OK), ("bad", STATUS_UNAUTHORIZED)])
	def test_custom (self, legacy, key, status):
		assert post_multipart ("/auth/custom", {"key": key})[0] == status

@pytest.mark.legacy_server ("web/wrapper.py")
class TestWrapper:

	def test_main (self, legacy):
		status, body = request ("GET", "/")
		assert (status == STATUS_OK) and (body_json (body) == {"oki": "doki!"})

	def test_echo (self, legacy):
		assert request ("GET", "/echo?value=test")[0] == STATUS_OK

@pytest.mark.legacy_server ("web/worker.py")
class TestWorker:

	def test_flow (self, legacy):
		assert request ("GET", "/")[0] == STATUS_OK
		assert post_multipart ("/work", {"value": "test"})[0] == STATUS_OK
		assert request ("GET", "/work/start")[0] == STATUS_INTERNAL_SERVER_ERROR
		assert request ("GET", "/work/stop")[0] == STATUS_OK
		assert request ("GET", "/work/stop")[0] == STATUS_INTERNAL_SERVER_ERROR
		assert request ("GET", "/work/start")[0] == STATUS_OK

@pytest.mark.legacy_server ("web/admin.py")
class TestAdmin:

	@pytest.mark.parametrize ("path", ["/", "/cerver/info", "/cerver/stats", "/cerver/stats/filesystems"])
	def test_admin (self, legacy, path):
		assert request ("GET", path)[0] == STATUS_OK

@pytest.mark.legacy_server ("web/upload.py")
class TestUpload:

	def test_upload (self, legacy):
		assert request ("GET", "/test")[0] == STATUS_OK
		assert post_multipart ("/upload", {}, {"file": IMAGE})[0] == STATUS_OK

	@pytest.mark.parametrize ("key, status", [("okay", STATUS_OK), ("discard", STATUS_BAD_REQUEST)])
	def test_discard (self, legacy, key, status):
		assert post_multipart ("/discard", {"key": key}, {"file": IMAGE})[0] == status

@pytest.mark.legacy_server ("web/multiple.py")
class TestMultiple:

	def test_two_files (self, legacy):
		assert post_multipart ("/multiple", {}, {"one": IMAGE, "two": SECOND_IMAGE})[0] == STATUS_OK

	@pytest.mark.parametrize ("key, status", [("okay", STATUS_OK), ("discard", STATUS_BAD_REQUEST)])
	def test_discard (self, legacy, key, status):
		assert post_multipart ("/discard", {"key": key}, {"file": IMAGE})[0] == status

@pytest.mark.legacy_server ("web/jobs.py")
class TestJobs:

	def test_job (self, legacy):
		assert request ("GET", "/")[0] == STATUS_OK
		assert post_multipart ("/jobs", {"value": "test"})[0] == STATUS_OK
