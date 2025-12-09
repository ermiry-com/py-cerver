"""Unit tests for lib.py and utils/utils.py - the C strings of cerver and strtobool.

lib_take_c_string () copies a string that cerver allocated and frees it with the free ()
of the process: a real allocation of libcerver, http_url_encode (), is taken here.
"""

import pytest

from cerver.lib import lib_take_c_string
from cerver.utils.utils import strtobool

from cerver.http.url import http_url_encode_c_string

pytestmark = [pytest.mark.unit]

TRUE_VALUES = ("y", "yes", "t", "true", "on", "1", "TRUE", "Yes")
FALSE_VALUES = ("n", "no", "f", "false", "off", "0", "FALSE", "No")

class TestTakeCString:

	def test_takes_and_frees_a_string_of_cerver (self):
		assert lib_take_c_string (http_url_encode_c_string (b"a b")) == b"a+b"

	def test_null_is_none (self):
		assert lib_take_c_string (None) is None
		assert lib_take_c_string (0) is None

class TestStrtobool:

	@pytest.mark.parametrize ("value", TRUE_VALUES)
	def test_true (self, value):
		assert strtobool (value) == 1

	@pytest.mark.parametrize ("value", FALSE_VALUES)
	def test_false (self, value):
		assert strtobool (value) == 0

	@pytest.mark.parametrize ("value", ["", "maybe", "2", "truth"])
	def test_invalid (self, value):
		with pytest.raises (ValueError):
			strtobool (value)
