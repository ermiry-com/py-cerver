"""Unit tests for http/url.py - the url encode and decode of cerver.

Bugs these tests fixed (in cerver, src/cerver/http/url.c):
- http_url_encode (None) and http_url_decode (None) passed NULL to strlen (): a segfault
- an incomplete or invalid escape was dropped or decoded into garbage
"""

import pytest
from hypothesis import given
from hypothesis import strategies

from cerver.http import http_url_decode
from cerver.http import http_url_encode

pytestmark = [pytest.mark.unit]

class TestUrl:

	def test_encode (self):
		assert http_url_encode (b"a file/with spaces") == b"a+file%2fwith+spaces"

	def test_decode (self):
		assert http_url_decode (b"a+file%2fwith+spaces") == b"a file/with spaces"

	def test_none (self):
		assert http_url_encode (None) is None
		assert http_url_decode (None) is None

	@pytest.mark.parametrize ("value", [b"%", b"abc%", b"%a", b"%zz", b"%g1"])
	def test_invalid_escapes_are_kept (self, value):
		assert http_url_decode (value) == value

	def test_bytes_over_ascii (self):
		assert http_url_encode ("ñ".encode ("utf-8")) == b"%c3%b1"

class TestUrlFuzz:

	pytestmark = [pytest.mark.fuzz]

	@given (value=strategies.binary ().filter (lambda value: b"\x00" not in value))
	def test_decode_of_the_encode_is_the_value (self, value):
		assert http_url_decode (http_url_encode (value)) == value

	@given (value=strategies.binary ().filter (lambda value: b"\x00" not in value))
	def test_decode_never_grows (self, value):
		assert len (http_url_decode (value)) <= len (value)
