"""Unit tests for the helpers of HTTP that do not need a request: dates, entity tags, proxies,
request ids, tree paths, compression, JWT values and the prebuilt responses.

Bugs these tests fixed:
- http_jwt_create () dropped a float value without an error and shared its default dict
- http_send_response () passed a JSON list to ctypes, which raised
"""

import ctypes
import pytest

from cerver.http import http_date_text, http_date_seconds, http_date_current, HTTP_DATE_LENGTH
from cerver.http import http_etag, http_etag_none_match
from cerver.http import http_proxy_network_has
from cerver.http import http_request_id_is_valid, http_request_id_generate, HTTP_REQUEST_ID_SIZE
from cerver.http import http_tree_path_error
from cerver.http import http_compression_accepts_gzip, http_compression_is_compressible
from cerver.http import http_jwt_create, http_cerver_auth_jwt_delete
from cerver.http import HttpPrebuiltResponses, HTTP_STATUS_NOT_FOUND
from cerver.http import http_route_duration_buckets, HTTP_ROUTE_STATS_DURATION_BUCKETS
from cerver.http import http_request_method_str, http_request_method_is_valid
from cerver.http import REQUEST_METHOD_PATCH, REQUEST_METHOD_MSEARCH, REQUEST_METHOD_QUERY
from cerver.http import REQUEST_METHOD_UNDEFINED, REQUEST_METHOD_SIZE
from cerver.http import jwt_alg_str, jwt_str_alg, JWT_ALG_RS256
from cerver.http.responses.core import http_send_response_body
from cerver.http import HTTP_CONTENT_TYPE_JSON, HTTP_CONTENT_TYPE_HTML
from cerver.http import HTTP_HEADER_SET_COOKIE, HTTP_HEADER_LOCATION, HTTP_HEADER_CONTENT_TYPE
from cerver.http import HTTP_HEADER_UNDEFINED, HTTP_STATUS_OK
from cerver.http import http_response_create, http_response_delete, http_response_add_header
from cerver.http import http_response_add_custom_header_value
from cerver.http import http_response_header_set, http_response_header_add
from cerver.http import http_response_header_remove, http_response_header_count
from cerver.http import http_response_header_value
from cerver.http import http_response_header_set_by_name, http_response_header_add_by_name
from cerver.http import http_response_header_remove_by_name, http_response_header_count_by_name
from cerver.http import http_response_header_value_by_name

pytestmark = [pytest.mark.unit]

EPOCH_DATE = "Thu, 01 Jan 1970 00:00:00 GMT"
KNOWN_SECONDS = 784111777
KNOWN_DATE = "Sun, 06 Nov 1994 08:49:37 GMT"

class TestDates:

	def test_format (self):
		assert http_date_text (0) == EPOCH_DATE
		assert http_date_text (KNOWN_SECONDS) == KNOWN_DATE

	def test_parse (self):
		assert http_date_seconds (KNOWN_DATE) == KNOWN_SECONDS
		assert http_date_seconds ("Sunday, 06-Nov-94 08:49:37 GMT") is None

	def test_current (self):
		assert len (http_date_current ()) == HTTP_DATE_LENGTH

class TestEntityTags:

	def test_strong_tag (self):
		tag = http_etag (b"body")
		assert tag.startswith ("\"") and tag.endswith ("\"")
		assert http_etag (b"body", compressed=True) != tag

	def test_none_match (self):
		tag = http_etag (b"body").encode ("utf-8")
		assert http_etag_none_match (tag, len (tag), tag, len (tag))
		assert http_etag_none_match (b"*", 1, tag, len (tag))
		assert not http_etag_none_match (b"\"other\"", 7, tag, len (tag))

class TestProxies:

	@pytest.mark.parametrize ("cidr, ip, inside", [
		("10.0.0.0/8", "10.1.2.3", True), ("10.0.0.0/8", "11.0.0.1", False),
		("fc00::/7", "fd00::1", True), ("192.168.1.1", "192.168.1.1", True)
	])
	def test_network (self, cidr, ip, inside):
		assert http_proxy_network_has (cidr, ip) == inside

	def test_invalid_network (self):
		with pytest.raises (ValueError):
			http_proxy_network_has ("10.0.0.0/99", "10.0.0.1")

class TestRequestIds:

	def test_valid (self):
		assert http_request_id_is_valid (b"abc-123_x.y", 11)
		assert not http_request_id_is_valid (b"with space", 10)

	def test_generate (self):
		buffer = ctypes.create_string_buffer (HTTP_REQUEST_ID_SIZE)
		assert http_request_id_generate (buffer) == 0
		assert http_request_id_is_valid (buffer.value, len (buffer.value))

class TestTree:

	def test_valid_path (self):
		assert http_tree_path_error ("/users/:id<objectid>") is None

	def test_invalid_path (self):
		assert http_tree_path_error ("/users/*rest/more")

	def test_duration_buckets (self):
		buckets = http_route_duration_buckets ()
		assert len (buckets) == HTTP_ROUTE_STATS_DURATION_BUCKETS
		assert buckets == sorted (buckets)

class TestCompression:

	def test_accepts_gzip (self):
		assert http_compression_accepts_gzip (b"gzip, br", 8)
		assert not http_compression_accepts_gzip (b"gzip;q=0", 8)

	def test_compressible (self):
		assert http_compression_is_compressible (b"application/json", 16)
		assert not http_compression_is_compressible (b"image/png", 9)

class TestNames:

	def test_method (self):
		assert http_request_method_str (REQUEST_METHOD_PATCH) == b"PATCH"
		assert http_request_method_str (REQUEST_METHOD_MSEARCH) == b"M-SEARCH"
		assert http_request_method_str (REQUEST_METHOD_QUERY) == b"QUERY"
		assert http_request_method_str (REQUEST_METHOD_UNDEFINED) == b"Undefined"

	def test_methods_of_llhttp (self):
		# the 34 methods of HTTP and QUERY, without PRI and the RTSP methods (34 to 45)
		valid = [method for method in range (REQUEST_METHOD_SIZE) if http_request_method_is_valid (method)]
		assert len (valid) == 35
		assert valid[-1] == REQUEST_METHOD_QUERY
		assert not any (http_request_method_is_valid (method) for method in range (34, 46))
		assert not http_request_method_is_valid (REQUEST_METHOD_UNDEFINED)

	def test_algorithm (self):
		assert jwt_alg_str (JWT_ALG_RS256) == b"RS256"
		assert jwt_str_alg (b"RS256") == JWT_ALG_RS256

class TestJwtValues:

	def test_supported_values (self):
		http_cerver_auth_jwt_delete (http_jwt_create ({"id": "1", "count": 2, "admin": True}))

	@pytest.mark.parametrize ("value", [1.5, None, [1]])
	def test_unsupported_value (self, value):
		with pytest.raises (TypeError):
			http_jwt_create ({"value": value})

class TestResponses:

	@pytest.mark.parametrize ("body, expected, content_type", [
		({"a": 1}, b"{\"a\": 1}", HTTP_CONTENT_TYPE_JSON),
		([1, 2], b"[1, 2]", HTTP_CONTENT_TYPE_JSON),
		("ñ", "ñ".encode ("utf-8"), HTTP_CONTENT_TYPE_HTML),
		(None, b"", HTTP_CONTENT_TYPE_HTML)
	])
	def test_body (self, body, expected, content_type):
		assert http_send_response_body (body, HTTP_CONTENT_TYPE_HTML) == (expected, content_type)

	def test_prebuilt (self):
		responses = HttpPrebuiltResponses ()
		responses.add ("not_found", HTTP_STATUS_NOT_FOUND, {"error": "Not found!"})
		responses.add ("not_found", HTTP_STATUS_NOT_FOUND, {"error": "Replaced!"})

		assert len (responses.responses) == 1

		responses.delete ()
		assert not responses.responses

FIRST_COOKIE = b"session=first; Path=/"
SECOND_COOKIE = b"theme=dark; Path=/"

# longer than the 256 bytes that a header of a response had
LONG_VALUE = b"v" * 700

class TestResponseHeaders:
	"""The headers of a response are a list since cerver 2.1b-11: a header can be repeated,
	it can have any name, and a value that would end its line is rejected."""

	@pytest.fixture
	def response (self):
		response = http_response_create (HTTP_STATUS_OK, None, 0)
		assert response

		yield response

		http_response_delete (response)

	def test_repeated (self, response):
		assert http_response_header_add (response, HTTP_HEADER_SET_COOKIE, FIRST_COOKIE) == 0
		assert http_response_header_add (response, HTTP_HEADER_SET_COOKIE, SECOND_COOKIE) == 0

		assert http_response_header_count (response, HTTP_HEADER_SET_COOKIE) == 2
		assert http_response_header_value (response, HTTP_HEADER_SET_COOKIE) == FIRST_COOKIE
		assert http_response_header_value (response, HTTP_HEADER_SET_COOKIE, 1) == SECOND_COOKIE
		assert http_response_header_value (response, HTTP_HEADER_SET_COOKIE, 2) is None
		assert http_response_header_value (response, HTTP_HEADER_LOCATION) is None

	def test_set_replaces (self, response):
		assert http_response_header_add (response, HTTP_HEADER_SET_COOKIE, FIRST_COOKIE) == 0
		assert http_response_header_add (response, HTTP_HEADER_SET_COOKIE, SECOND_COOKIE) == 0
		assert http_response_header_set (response, HTTP_HEADER_SET_COOKIE, b"only=one") == 0

		assert http_response_header_count (response, HTTP_HEADER_SET_COOKIE) == 1
		assert http_response_header_value (response, HTTP_HEADER_SET_COOKIE) == b"only=one"

	def test_add_header_keeps_replacing (self, response):
		assert http_response_add_header (response, HTTP_HEADER_LOCATION, b"/first") == 0
		assert http_response_add_header (response, HTTP_HEADER_LOCATION, b"/second") == 0
		assert http_response_header_count (response, HTTP_HEADER_LOCATION) == 1
		assert http_response_header_value (response, HTTP_HEADER_LOCATION) == b"/second"

		assert http_response_add_custom_header_value (response, HTTP_HEADER_LOCATION, "/third") == 0
		assert http_response_header_count (response, HTTP_HEADER_LOCATION) == 1
		assert http_response_header_value (response, HTTP_HEADER_LOCATION) == b"/third"

	def test_remove (self, response):
		assert http_response_header_add (response, HTTP_HEADER_SET_COOKIE, FIRST_COOKIE) == 0
		assert http_response_header_add (response, HTTP_HEADER_LOCATION, b"/home") == 0
		assert http_response_header_add (response, HTTP_HEADER_SET_COOKIE, SECOND_COOKIE) == 0

		assert http_response_header_remove (response, HTTP_HEADER_SET_COOKIE) == 2
		assert http_response_header_remove (response, HTTP_HEADER_SET_COOKIE) == 0
		assert http_response_header_count (response, HTTP_HEADER_SET_COOKIE) == 0
		assert http_response_header_value (response, HTTP_HEADER_LOCATION) == b"/home"

	def test_by_name (self, response):
		assert http_response_header_add_by_name (response, b"X-Trace", b"one") == 0
		assert http_response_header_add_by_name (response, b"x-trace", b"two") == 0

		assert http_response_header_count_by_name (response, b"X-TRACE") == 2
		assert http_response_header_value_by_name (response, "x-Trace") == b"one"
		assert http_response_header_value_by_name (response, "x-Trace", 1) == b"two"
		assert http_response_header_value_by_name (response, "X-Other") is None

		assert http_response_header_set_by_name (response, b"X-Trace", b"three") == 0
		assert http_response_header_count_by_name (response, b"x-trace") == 1
		assert http_response_header_value_by_name (response, b"X-TRACE") == b"three"

		assert http_response_header_remove_by_name (response, b"x-trace") == 1
		assert http_response_header_count_by_name (response, b"X-Trace") == 0

	def test_known_name_is_its_type (self, response):
		assert http_response_header_add_by_name (response, b"content-type", b"text/plain") == 0

		assert http_response_header_count (response, HTTP_HEADER_CONTENT_TYPE) == 1
		assert http_response_header_value (response, HTTP_HEADER_CONTENT_TYPE) == b"text/plain"
		assert http_response_header_value_by_name (response, "Content-Type") == b"text/plain"

	@pytest.mark.parametrize ("value", [
		b"/home\r\nSet-Cookie: stolen=1", b"/home\nX-Other: 1", b"/home\r"
	])
	def test_value_that_ends_its_line_is_rejected (self, response, value):
		assert http_response_header_add (response, HTTP_HEADER_LOCATION, value) == 1
		assert http_response_header_set (response, HTTP_HEADER_LOCATION, value) == 1
		assert http_response_add_header (response, HTTP_HEADER_LOCATION, value) == 1
		assert http_response_add_custom_header_value (response, HTTP_HEADER_LOCATION, value) == 1
		assert http_response_header_add_by_name (response, b"X-Trace", value) == 1

		assert http_response_header_count (response, HTTP_HEADER_LOCATION) == 0
		assert http_response_header_count_by_name (response, b"X-Trace") == 0

	@pytest.mark.parametrize ("name", [b"", b"X Trace", b"X-Trace:", b"X-Trace\r\n"])
	def test_name_that_is_not_a_token_is_rejected (self, response, name):
		assert http_response_header_add_by_name (response, name, b"one") == 1
		assert http_response_header_set_by_name (response, name, b"one") == 1

	def test_undefined_header_is_rejected (self, response):
		assert http_response_header_add (response, HTTP_HEADER_UNDEFINED, b"one") == 1
		assert http_response_add_header (response, HTTP_HEADER_UNDEFINED, b"one") == 1

	def test_long_value_is_complete (self, response):
		assert http_response_add_header (response, HTTP_HEADER_SET_COOKIE, LONG_VALUE) == 0
		assert http_response_header_value (response, HTTP_HEADER_SET_COOKIE) == LONG_VALUE
