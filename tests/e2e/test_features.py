"""The headers that cerver adds to the responses of pycerver, entity tags, compression and streams.

The server identifies its requests and trusts the loopback as a proxy, like nginx
in a private network, and the group of the features has CORS.
"""

import json
import pytest
import uuid
from email.utils import parsedate_to_datetime

from e2e.conftest import e2e_raw
from e2e.conftest import e2e_request

from cerver.http import http_compression_available

pytestmark = [pytest.mark.e2e]

ALLOWED_ORIGIN = "http://allowed.com"

GZIP_MAGIC = b"\x1f\x8b"

class TestHeaders:

	def test_every_response_has_a_date (self, server):
		response = e2e_request ("GET", "/api/e2e/json")

		assert parsedate_to_datetime (response.headers["date"]) is not None
		assert response.headers["connection"] == "close"

	def test_the_request_id_is_kept (self, server):
		response = e2e_request ("GET", "/api/features/client", headers={"X-Request-Id": "nginx-request-7"})

		assert response.headers["x-request-id"] == "nginx-request-7"
		assert json.loads (response.body)["id"] == "nginx-request-7"

	def test_an_invalid_request_id_is_replaced (self, server):
		response = e2e_request ("GET", "/api/features/client", headers={"X-Request-Id": "has spaces"})

		assert uuid.UUID (response.headers["x-request-id"]).version == 4

	def test_a_not_found_has_a_request_id (self, server):
		response = e2e_request ("GET", "/api/missing")

		assert response.status == 404
		assert uuid.UUID (response.headers["x-request-id"]).version == 4

	def test_the_client_address_is_forwarded (self, server):
		assert json.loads (e2e_request ("GET", "/api/features/client").body)["ip"] == "127.0.0.1"

		response = e2e_request ("GET", "/api/features/client", headers={"X-Forwarded-For": "203.0.113.4"})
		assert json.loads (response.body)["ip"] == "203.0.113.4"

		response = e2e_request ("GET", "/api/features/client", headers={"X-Real-IP": "2001:db8::4"})
		assert json.loads (response.body)["ip"] == "2001:db8::4"

	def test_cors_of_the_group (self, server):
		response = e2e_request ("GET", "/api/features/client", headers={"Origin": ALLOWED_ORIGIN})

		assert response.headers["access-control-allow-origin"] == ALLOWED_ORIGIN
		assert "Origin" in response.headers["vary"]

		response = e2e_request ("GET", "/api/features/client", headers={"Origin": "http://other.com"})
		assert "access-control-allow-origin" not in response.headers

class TestConditional:

	def test_the_same_body_is_not_modified (self, server):
		response = e2e_request ("GET", "/api/features/etag")
		etag = response.headers["etag"]

		assert response.status == 200
		assert etag.startswith ("\"")

		response = e2e_request ("GET", "/api/features/etag", headers={"If-None-Match": etag})
		assert response.status == 304
		assert response.body == b""
		assert response.headers["etag"] == etag

	def test_another_entity_tag_is_sent (self, server):
		response = e2e_request ("GET", "/api/features/etag", headers={"If-None-Match": "\"other\""})

		assert response.status == 200
		assert len (json.loads (response.body)["items"]) == 1 << 7

	def test_an_endpoint_without_the_setting (self, server):
		assert "etag" not in e2e_request ("GET", "/api/features/client").headers

class TestCompression:

	def test_the_body_is_compressed (self, server):
		response = e2e_request ("GET", "/api/features/compressed", headers={"Accept-Encoding": "gzip"})

		assert response.status == 200
		assert "Accept-Encoding" in response.headers["vary"]

		if (http_compression_available ()):
			assert response.headers["content-encoding"] == "gzip"
			assert response.body.startswith (GZIP_MAGIC)
			assert int (response.headers["content-length"]) == len (response.body)

		else:
			assert "content-encoding" not in response.headers

	def test_a_client_without_gzip (self, server):
		response = e2e_request ("GET", "/api/features/compressed")

		assert "content-encoding" not in response.headers
		assert len (json.loads (response.body)["items"]) == 1 << 7

class TestStream:

	def test_the_stream_is_chunked (self, server):
		raw = e2e_raw (b"GET /api/features/stream HTTP/1.1\r\nHost: localhost\r\n\r\n")
		head, body = raw.split (b"\r\n\r\n", 1)

		assert b"Transfer-Encoding: chunked" in head
		assert b"Content-Length" not in head
		assert body == b"5\r\nfirst\r\n6\r\nsecond\r\n0\r\n\r\n"

	def test_an_old_client_reads_until_the_end (self, server):
		raw = e2e_raw (b"GET /api/features/stream HTTP/1.0\r\n\r\n")
		head, body = raw.split (b"\r\n\r\n", 1)

		assert b"Transfer-Encoding" not in head
		assert body == b"firstsecond"

	def test_a_chunked_body_is_received (self, server):
		raw = e2e_raw (
			b"POST /api/e2e/body HTTP/1.1\r\nHost: localhost\r\nContent-Type: application/json\r\n"
			b"Transfer-Encoding: chunked\r\n\r\n"
			b"8\r\n{\"key\": \r\n6\r\n\"value\r\n2\r\n\"}\r\n0\r\nX-Trailer: ignored\r\n\r\n"
		)

		head, body = raw.split (b"\r\n\r\n", 1)
		assert head.startswith (b"HTTP/1.1 200")
		assert json.loads (body) == {"key": "value"}
