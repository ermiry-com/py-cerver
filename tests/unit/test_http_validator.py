"""Unit tests for http/validator.py - the validators of the typed route params.

Each validator of cerver is compared with a python reference of its format,
on fixed values and on any bytes from hypothesis.
"""

import pytest
import re
from hypothesis import given
from hypothesis import strategies

from cerver.http import http_param_validate_int
from cerver.http import http_param_validate_objectid
from cerver.http import http_param_validate_uuid

pytestmark = [pytest.mark.unit]

OBJECTID = re.compile (rb"[0-9a-fA-F]{24}")
INTEGER = re.compile (rb"-?[0-9]+")
UUID = re.compile (rb"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")

def _objectid (value: bytes) -> bool:
	return http_param_validate_objectid (value, len (value))

def _integer (value: bytes) -> bool:
	return http_param_validate_int (value, len (value))

def _uuid (value: bytes) -> bool:
	return http_param_validate_uuid (value, len (value))

class TestValidators:

	@pytest.mark.parametrize ("value, valid", [
		(b"507f1f77bcf86cd799439011", True),
		(b"507F1F77BCF86CD799439011", True),
		(b"507f1f77bcf86cd79943901", False),
		(b"507f1f77bcf86cd79943901g", False),
		(b"", False)
	])
	def test_objectid (self, value, valid):
		assert _objectid (value) == valid

	@pytest.mark.parametrize ("value, valid", [
		(b"0", True), (b"-12", True), (b"123456789", True),
		(b"-", False), (b"", False), (b"1.5", False), (b"+1", False), (b"1a", False)
	])
	def test_integer (self, value, valid):
		assert _integer (value) == valid

	@pytest.mark.parametrize ("value, valid", [
		(b"123e4567-e89b-12d3-a456-426614174000", True),
		(b"123e4567e89b12d3a456426614174000", False),
		(b"123e4567-e89b-12d3-a456-42661417400g", False),
		(b"", False)
	])
	def test_uuid (self, value, valid):
		assert _uuid (value) == valid

class TestValidatorsFuzz:

	pytestmark = [pytest.mark.fuzz]

	@given (value=strategies.binary (max_size=64) | strategies.from_regex (OBJECTID, fullmatch=True))
	def test_objectid_is_the_reference (self, value):
		assert _objectid (value) == bool (OBJECTID.fullmatch (value))

	@given (value=strategies.binary (max_size=32) | strategies.from_regex (INTEGER, fullmatch=True))
	def test_integer_is_the_reference (self, value):
		assert _integer (value) == bool (INTEGER.fullmatch (value))

	@given (value=strategies.binary (max_size=64) | strategies.from_regex (UUID, fullmatch=True))
	def test_uuid_is_the_reference (self, value):
		assert _uuid (value) == bool (UUID.fullmatch (value))
