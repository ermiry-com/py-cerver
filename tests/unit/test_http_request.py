"""Unit tests for the readers of a request: the json body, the decoded jwt, the files and the values.

The getters of cerver are patched where each reader uses them, to real cerver Strings,
to a real NULL pointer or to None, which is what libcerver returns.

Bugs these tests fixed:
- http_request_get_body_json () of a request without a body raised: NULL pointer access
- http_jwt_token_decode () of a request without decoded data raised AttributeError
- http_multi_part_get_file () of a file input without a file called .decode () on None
- http_request_get_int_query_value () raised ValueError for a value that is not an integer
- a body with a NUL byte was cut at it, the String of cerver has its length
"""

import json
import pytest
from ctypes import create_string_buffer
from unittest.mock import patch

from cerver.http import multipart
from cerver.http.cerver import auth
from cerver.http.cerver.auth import http_jwt_token_decode
from cerver.http.multipart import http_multi_part_get_file
from cerver.http.requests import body, query, values
from cerver.http.requests.body import http_request_get_body_json
from cerver.http.requests.query import http_request_get_int_query_value
from cerver.http.requests.query import http_request_get_float_query_value
from cerver.http.requests.query import http_request_get_bool_query_value
from cerver.http.requests.values import http_request_get_body_string
from cerver.http.requests.values import http_request_content_type_is_multi_part
from cerver.http.requests.values import http_request_get_decoded_json
from cerver.types import string_bytes, string_text

from shared import build_null_string
from shared import build_string

pytestmark = [pytest.mark.unit]

REQUEST = None
MPART = None
VALUES = None

NOT_UTF8 = b"\xff\xfe"

class TestStrings:

	def test_text_with_its_length (self):
		assert string_bytes (build_string (b"a\x00b")) == b"a\x00b"

	def test_null (self):
		assert string_bytes (build_null_string ()) is None
		assert string_text (build_null_string ()) is None

	def test_not_utf8 (self):
		assert string_text (build_string (NOT_UTF8)) is None

class TestBodyJson:

	def _body (self, value):
		with patch.object (body, "http_request_get_body", return_value=value):
			return http_request_get_body_json (REQUEST)

	def test_object (self):
		content = {"name": "ñandú"}
		assert self._body (build_string (json.dumps (content).encode ("utf-8"))) == content

	def test_without_body (self):
		assert self._body (build_null_string ()) is None

	@pytest.mark.parametrize ("content", [b"{", b"[1]", b"null", NOT_UTF8, b"", b"{\"a\": 1}\x00junk"])
	def test_body_that_is_not_an_object (self, content):
		assert self._body (build_string (content)) is None

	def test_body_string (self):
		with patch.object (values, "http_request_get_body", return_value=build_string ("ñ".encode ("utf-8"))):
			assert http_request_get_body_string (REQUEST) == "ñ"

class TestContentTypeMultiPart:

	@pytest.mark.parametrize ("content_type, expected", [
		(b"multipart/form-data; boundary=x", True),
		(b"Multipart/Form-Data; boundary=x", True),
		(b"application/json", False)
	])
	def test_content_type (self, content_type, expected):
		with patch.object (values, "http_request_get_header", return_value=build_string (content_type)):
			assert http_request_content_type_is_multi_part (REQUEST) is expected

	def test_without_content_type (self):
		with patch.object (values, "http_request_get_header", return_value=build_null_string ()):
			assert http_request_content_type_is_multi_part (REQUEST) is False

class TestJwtDecode:

	def _decoded (self, value, reader):
		with patch.object (auth, "http_request_get_decoded_data", return_value=value):
			with patch.object (values, "http_request_get_decoded_data", return_value=value):
				return reader (REQUEST)

	@pytest.mark.parametrize ("reader", [http_jwt_token_decode, http_request_get_decoded_json])
	def test_decoded_data (self, reader):
		data = create_string_buffer (b"{\"id\": \"token\"}")
		assert self._decoded (data, reader) == {"id": "token"}

	@pytest.mark.parametrize ("reader", [http_jwt_token_decode, http_request_get_decoded_json])
	def test_without_decoded_data (self, reader):
		assert self._decoded (None, reader) is None

	@pytest.mark.parametrize ("reader", [http_jwt_token_decode, http_request_get_decoded_json])
	def test_decoded_data_that_is_not_json (self, reader):
		data = create_string_buffer (b"not json")
		assert self._decoded (data, reader) is None

class TestQueryValues:

	def _value (self, content, reader):
		found = build_null_string () if (content is None) else build_string (content)
		with patch.object (query, "http_query_pairs_get_value", return_value=found):
			return reader (VALUES, "key")

	@pytest.mark.parametrize ("content, expected", [(b"5", 5), (b"-2", -2), (b"5.5", None), (b"x", None), (None, None)])
	def test_int (self, content, expected):
		assert self._value (content, http_request_get_int_query_value) == expected

	@pytest.mark.parametrize ("content, expected", [(b"5.5", 5.5), (b"x", None), (None, None)])
	def test_float (self, content, expected):
		assert self._value (content, http_request_get_float_query_value) == expected

	@pytest.mark.parametrize ("content, expected", [(b"true", True), (b"0", False), (b"maybe", None), (NOT_UTF8, None)])
	def test_bool (self, content, expected):
		assert self._value (content, http_request_get_bool_query_value) == expected

class TestMultiPartFile:

	def _file (self, original, generated, saved):
		patches = (
			patch.object (multipart, "http_multi_part_is_file", return_value=True),
			patch.object (multipart, "http_multi_part_get_filename", return_value=original),
			patch.object (multipart, "http_multi_part_get_generated_filename", return_value=generated),
			patch.object (multipart, "http_multi_part_get_saved_filename", return_value=saved)
		)

		for active in patches:
			active.start ()

		try:
			return http_multi_part_get_file (MPART)

		finally:
			for active in patches:
				active.stop ()

	def test_saved_file (self):
		assert self._file (b"photo.jpg", b"1-photo.jpg", b"/tmp/1-photo.jpg") == {
			"original": "photo.jpg", "generated": "1-photo.jpg", "saved": "/tmp/1-photo.jpg"
		}

	def test_file_input_without_file (self):
		assert self._file (None, None, None) == {"original": None, "saved": None}

	def test_filename_that_is_not_utf8 (self):
		assert self._file (NOT_UTF8, None, b"/tmp/1") == {"original": None, "saved": "/tmp/1"}

	def test_value_part (self):
		with patch.object (multipart, "http_multi_part_is_file", return_value=False):
			assert http_multi_part_get_file (MPART) == dict ()
