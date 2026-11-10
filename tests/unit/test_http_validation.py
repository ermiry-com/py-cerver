"""Unit tests for http/validation - the body, query, multi-part, image and typed validators.

The getters of cerver are patched where each validator uses them, to real cerver Strings,
to bytes or to None, which is what libcerver returns. Every validator writes its value,
its error, or nothing for an optional value; none raises into the route.

Bugs these tests fixed:
- a body value without a length, like a number, raised TypeError in validate_body_value ()
- a 0 or a False body value was dropped without an error by validate_body_value ()
- the float validator rejected the integer 5 and the int one the float 5.0, the same json number
- a query or multi-part value that was not utf-8 raised UnicodeDecodeError
- a multi-part file that was not saved was missing without an error
- a body number of another type was "required" instead of "invalid" (1.0)
- validate_query_value_with_cast () gave nothing for a missing value and caught every exception (1.0)
- validate_mparts_file_is_image () set its error twice, and the optional one wrote errors (1.0)
"""

import pytest
from datetime import datetime
from hypothesis import given
from hypothesis import strategies
from unittest.mock import patch

from cerver.http.validation import image, multipart, query
from cerver.http.validation import validate_body_float_value_exists
from cerver.http.validation import validate_body_int_value_exists
from cerver.http.validation import validate_body_string_value_exists_ignore_size
from cerver.http.validation import validate_body_value
from cerver.http.validation import validate_body_value_exists
from cerver.http.validation import validate_body_value_with_default
from cerver.http.validation import validate_file_is_image
from cerver.http.validation import validate_mparts_bool
from cerver.http.validation import validate_mparts_exists
from cerver.http.validation import validate_mparts_file_exists
from cerver.http.validation import validate_mparts_file_is_image
from cerver.http.validation import validate_mparts_filename_exists
from cerver.http.validation import validate_mparts_float
from cerver.http.validation import validate_mparts_int
from cerver.http.validation import validate_mparts_int_with_default
from cerver.http.validation import validate_mparts_optional_file_is_image
from cerver.http.validation import validate_mparts_value_with_default
from cerver.http.validation import validate_query_bool_value
from cerver.http.validation import validate_query_exists
from cerver.http.validation import validate_query_float_value
from cerver.http.validation import validate_query_int_limit_value
from cerver.http.validation import validate_query_int_value
from cerver.http.validation import validate_query_value_with_cast
from cerver.http.validation import validate_query_value_with_default
from cerver.http.validation import validation_decode
from cerver.http.validation import validate_body_int, validate_body_float, validate_body_bool
from cerver.http.validation import validate_body_string, validate_body_choice
from cerver.http.validation import validate_body_list, validate_body_date
from cerver.http.validation import validate_query_int, validate_query_list, validate_query_choice

from shared import build_null_string
from shared import build_string

pytestmark = [pytest.mark.unit]

FIELD = "field"

REQUEST = None
VALUES = None
MPART = 1

NOT_UTF8 = b"\xff\xfe"

INT_DEFAULT = 7

ERROR_REQUIRED = f"Field {FIELD} is required."
ERROR_INVALID = f"Field {FIELD} is invalid."
ERROR_MISSING_FILE = f"File {FIELD} is missing."
ERROR_NOT_IMAGE = f"File {FIELD} is not png or jpeg."

def _query (value):
	found = build_null_string () if (value is None) else build_string (value)

	return patch.object (query, "http_query_pairs_get_value", return_value=found)

def _mparts (value):
	return patch.object (multipart, "http_request_multi_parts_get_value", return_value=value)

class TestDecode:

	def test_utf8 (self):
		assert validation_decode ("ñ".encode ("utf-8")) == "ñ"

	def test_not_utf8 (self):
		assert validation_decode (NOT_UTF8) is None

	def test_none (self):
		assert validation_decode (None) is None

class TestBodyValue:

	@pytest.mark.parametrize ("value", ["abc", [1, 2, 3], {"a": 1, "b": 2, "c": 3}])
	def test_value_with_length (self, value):
		errors = dict ()
		assert validate_body_value ({FIELD: value}, FIELD, 1, 3, errors) == value
		assert not errors

	@pytest.mark.parametrize ("value", [5, 5.5, True, 0, False])
	def test_value_without_length_is_invalid (self, value):
		errors = dict ()
		assert validate_body_value ({FIELD: value}, FIELD, 1, 3, errors) is None
		assert errors == {FIELD: ERROR_INVALID}

	def test_value_out_of_its_length (self):
		errors = dict ()
		assert validate_body_value ({FIELD: "abcd"}, FIELD, 1, 3, errors) is None
		assert FIELD in errors

	@pytest.mark.parametrize ("body", [dict (), {FIELD: ""}, {FIELD: None}])
	def test_missing_value_is_required (self, body):
		errors = dict ()
		assert validate_body_value (body, FIELD, 1, 3, errors) is None
		assert errors == {FIELD: ERROR_REQUIRED}

	def test_exists_keeps_a_zero (self):
		errors = dict ()
		assert validate_body_value_exists ({FIELD: 0}, FIELD, errors) == 0
		assert not errors

	@pytest.mark.parametrize ("body, expected", [({FIELD: 0}, 0), ({FIELD: ""}, "default"), ({FIELD: None}, "default"), (dict (), "default")])
	def test_with_default (self, body, expected):
		assert validate_body_value_with_default (body, FIELD, "default") == expected

	def test_string_ignore_size (self):
		errors = dict ()
		assert validate_body_string_value_exists_ignore_size ({FIELD: ""}, FIELD, errors) == ""
		assert validate_body_string_value_exists_ignore_size ({FIELD: 5}, FIELD, errors) is None
		assert errors == {FIELD: ERROR_INVALID}

class TestBodyNumbers:

	@pytest.mark.parametrize ("value, expected", [(5, 5), (5.0, 5), (-3, -3)])
	def test_int (self, value, expected):
		errors = dict ()
		result = validate_body_int_value_exists ({FIELD: value}, FIELD, errors)
		assert (result == expected) and (type (result) is int)
		assert not errors

	@pytest.mark.parametrize ("value", [5.5, "5", True, None])
	def test_int_of_another_type_is_invalid (self, value):
		errors = dict ()
		assert validate_body_int_value_exists ({FIELD: value}, FIELD, errors) is None
		assert errors == {FIELD: ERROR_INVALID}

	def test_missing_int_is_required (self):
		errors = dict ()
		assert validate_body_int_value_exists (dict (), FIELD, errors) is None
		assert errors == {FIELD: ERROR_REQUIRED}

	@pytest.mark.parametrize ("value, expected", [(5.5, 5.5), (5, 5.0), (0, 0.0)])
	def test_float (self, value, expected):
		errors = dict ()
		result = validate_body_float_value_exists ({FIELD: value}, FIELD, errors)
		assert (result == expected) and (type (result) is float)
		assert not errors

	@pytest.mark.parametrize ("value", ["5.5", True, None])
	def test_float_of_another_type_is_invalid (self, value):
		errors = dict ()
		assert validate_body_float_value_exists ({FIELD: value}, FIELD, errors) is None
		assert errors == {FIELD: ERROR_INVALID}

class TestQuery:

	def test_exists (self):
		errors = dict ()
		with _query (b"value"):
			assert validate_query_exists (VALUES, FIELD, errors) == "value"

	@pytest.mark.parametrize ("value", [None, b"", NOT_UTF8])
	def test_exists_missing (self, value):
		errors = dict ()
		with _query (value):
			assert validate_query_exists (VALUES, FIELD, errors) is None

		assert errors == {FIELD: ERROR_REQUIRED}

	def test_value_with_default (self):
		with _query (NOT_UTF8):
			assert validate_query_value_with_default (VALUES, FIELD, "default") == "default"

	@pytest.mark.parametrize ("validator", [validate_query_int_value, validate_query_float_value, validate_query_bool_value])
	def test_typed_value_that_is_not_utf8_is_invalid (self, validator):
		errors = dict ()
		with _query (NOT_UTF8):
			assert validator (VALUES, FIELD, errors) is None

		assert errors == {FIELD: ERROR_INVALID}

	@pytest.mark.parametrize ("content, expected", [(b"-5", 1), (b"500", 10), (b"4", 4)])
	def test_int_limit (self, content, expected):
		errors = dict ()
		with _query (content):
			assert validate_query_int_limit_value (VALUES, FIELD, 1, 10, errors) == expected

	def test_with_cast (self):
		errors = dict ()
		with _query (b"a,b"):
			assert validate_query_value_with_cast (VALUES, FIELD, lambda value: value.split (","), errors) == ["a", "b"]

	def test_with_cast_missing_is_required (self):
		errors = dict ()
		with _query (None):
			assert validate_query_value_with_cast (VALUES, FIELD, int, errors) is None

		assert errors == {FIELD: ERROR_REQUIRED}

	def test_with_cast_does_not_hide_other_errors (self):
		def broken (value):
			raise KeyError (value)

		with _query (b"x"):
			with pytest.raises (KeyError):
				validate_query_value_with_cast (VALUES, FIELD, broken, dict ())

class TestMultiParts:

	def test_exists (self):
		errors = dict ()
		with _mparts (b"value"):
			assert validate_mparts_exists (REQUEST, FIELD, errors) == "value"

	@pytest.mark.parametrize ("value", [None, b"", NOT_UTF8])
	def test_exists_missing (self, value):
		errors = dict ()
		with _mparts (value):
			assert validate_mparts_exists (REQUEST, FIELD, errors) is None

		assert errors == {FIELD: ERROR_REQUIRED}

	def test_value_with_default (self):
		with _mparts (NOT_UTF8):
			assert validate_mparts_value_with_default (REQUEST, FIELD, "default") == "default"

	@pytest.mark.parametrize ("validator", [validate_mparts_int, validate_mparts_float, validate_mparts_bool])
	def test_typed_value_that_is_not_utf8_is_invalid (self, validator):
		errors = dict ()
		with _mparts (NOT_UTF8):
			assert validator (REQUEST, FIELD, errors) is None

		assert errors == {FIELD: ERROR_INVALID}

	def test_int_with_default (self):
		with _mparts (NOT_UTF8):
			assert validate_mparts_int_with_default (REQUEST, FIELD, INT_DEFAULT) == INT_DEFAULT

		with _mparts (b"3"):
			assert validate_mparts_int_with_default (REQUEST, FIELD, INT_DEFAULT) == 3

class TestMultiPartFiles:

	def _patches (self, module, saved, exists: bool):
		patches = [
			patch.object (module, "http_request_multi_parts_get", return_value=MPART),
			patch.object (module, "http_multi_part_is_file", return_value=True),
			patch.object (module, "http_multi_part_get_saved_filename", return_value=saved),
			patch.object (module, "http_multi_part_get_file", return_value={"saved": "x"})
		]

		if (hasattr (module, "file_exists")):
			patches.append (patch.object (module, "file_exists", return_value=exists))

		return patches

	def _run (self, module, validator, saved, exists: bool, *arguments):
		patches = self._patches (module, saved, exists)
		for active in patches:
			active.start ()

		try:
			return validator (REQUEST, FIELD, *arguments)

		finally:
			for active in patches:
				active.stop ()

	def test_saved_file (self):
		errors = dict ()
		assert self._run (multipart, validate_mparts_file_exists, b"/tmp/x", True, errors) == {"saved": "x"}
		assert not errors

	@pytest.mark.parametrize ("saved, exists", [(None, False), (b"/tmp/gone", False)])
	def test_file_that_was_not_saved_is_missing (self, saved, exists):
		errors = dict ()
		assert self._run (multipart, validate_mparts_file_exists, saved, exists, errors) is None
		assert errors == {FIELD: ERROR_MISSING_FILE}

	def test_filename_that_is_not_utf8_is_missing (self):
		errors = dict ()
		with patch.object (multipart, "http_request_multi_parts_get_filename", return_value=NOT_UTF8):
			assert validate_mparts_filename_exists (REQUEST, FIELD, errors) is None

		assert errors == {FIELD: ERROR_MISSING_FILE}

	@pytest.mark.parametrize ("filename", [None, "", "/tmp/cerver-test-missing.png"])
	def test_missing_image_is_not_an_image (self, filename):
		errors = dict ()
		assert validate_file_is_image (filename, FIELD, errors) == 0
		assert errors == {FIELD: ERROR_NOT_IMAGE}

	def test_file_that_is_not_an_image_has_a_single_error (self):
		errors = dict ()
		assert self._run (image, validate_mparts_file_is_image, b"/tmp/cerver-test-missing", False, errors) is None
		assert errors == {FIELD: ERROR_NOT_IMAGE}

	def test_optional_image_never_writes_errors (self):
		errors = dict ()
		assert self._run (image, validate_mparts_optional_file_is_image, b"/tmp/cerver-test-missing", False, errors) is None
		assert not errors

class TestTyped:

	@pytest.mark.parametrize ("value, expected", [(5, 5), (5.0, 5), ("7", 7)])
	def test_int (self, value, expected):
		errors = dict ()
		assert validate_body_int ({FIELD: value}, FIELD, errors) == expected
		assert not errors

	@pytest.mark.parametrize ("value", [5.5, True, "x", [1]])
	def test_int_invalid (self, value):
		errors = dict ()
		assert validate_body_int ({FIELD: value}, FIELD, errors) is None
		assert errors == {FIELD: ERROR_INVALID}

	def test_int_range (self):
		errors = dict ()
		assert validate_body_int ({FIELD: 11}, FIELD, errors, minimum=1, maximum=10) is None
		assert errors == {FIELD: f"Field {FIELD} must be between 1 and 10."}

	def test_optional_with_default (self):
		errors = dict ()
		assert validate_body_int (dict (), FIELD, errors, required=False, default=3) == 3
		assert not errors

	def test_required (self):
		errors = dict ()
		assert validate_body_float (dict (), FIELD, errors) is None
		assert errors == {FIELD: ERROR_REQUIRED}

	@pytest.mark.parametrize ("value, expected", [(True, True), ("no", False), ("1", True)])
	def test_bool (self, value, expected):
		assert validate_body_bool ({FIELD: value}, FIELD, dict ()) is expected

	def test_string_length (self):
		errors = dict ()
		assert validate_body_string ({FIELD: "abcd"}, FIELD, errors, max_len=3) is None
		assert FIELD in errors

	def test_choice (self):
		errors = dict ()
		assert validate_body_choice ({FIELD: "b"}, FIELD, errors, ("a", "b")) == "b"
		assert validate_body_choice ({FIELD: "c"}, FIELD, errors, ("a", "b")) is None
		assert errors == {FIELD: f"Field {FIELD} must be one of a, b."}

	def test_list (self):
		errors = dict ()
		assert validate_body_list ({FIELD: [1, "2"]}, FIELD, errors, item=int) == [1, 2]
		assert validate_body_list ({FIELD: [1, 2, 3]}, FIELD, errors, max_items=2) is None
		assert FIELD in errors

	def test_date (self):
		errors = dict ()
		assert validate_body_date ({FIELD: "2026-11-09"}, FIELD, errors) == datetime (2026, 11, 9)
		assert validate_body_date ({FIELD: "not a date"}, FIELD, errors) is None
		assert errors == {FIELD: ERROR_INVALID}

	def test_query_int_and_list (self):
		errors = dict ()
		with _query (b"4"):
			assert validate_query_int (VALUES, FIELD, errors, minimum=1) == 4

		with _query (b"a,b"):
			assert validate_query_list (VALUES, FIELD, errors) == ["a", "b"]

		with _query (NOT_UTF8):
			assert validate_query_choice (VALUES, FIELD, errors, ("a",)) is None

		assert FIELD in errors

class TestValidationFuzz:

	pytestmark = [pytest.mark.fuzz]

	@given (value=strategies.binary ())
	def test_query_validators_end_in_a_value_or_an_error (self, value):
		for validator in (validate_query_exists, validate_query_int_value, validate_query_float_value, validate_query_bool_value):
			errors = dict ()
			with _query (value):
				result = validator (VALUES, FIELD, errors)

			assert (result is None) == (FIELD in errors)

	@given (value=strategies.binary ())
	def test_mparts_validators_end_in_a_value_or_an_error (self, value):
		for validator in (validate_mparts_exists, validate_mparts_int, validate_mparts_float, validate_mparts_bool):
			errors = dict ()
			with _mparts (value):
				result = validator (REQUEST, FIELD, errors)

			assert (result is None) == (FIELD in errors)

	@given (value=strategies.none () | strategies.booleans () | strategies.integers () | strategies.floats (allow_nan=False) | strategies.text () | strategies.lists (strategies.integers ()))
	def test_body_value_never_raises (self, value):
		errors = dict ()
		result = validate_body_value ({FIELD: value}, FIELD, 1, 8, errors)

		assert (result is None) == (FIELD in errors)

	@given (value=strategies.none () | strategies.booleans () | strategies.integers () | strategies.floats () | strategies.text () | strategies.lists (strategies.integers ()))
	def test_typed_validators_never_raise (self, value):
		for validator in (validate_body_int, validate_body_float, validate_body_bool, validate_body_string, validate_body_list, validate_body_date):
			errors = dict ()
			result = validator ({FIELD: value}, FIELD, errors)

			assert (result is None) == (FIELD in errors)
