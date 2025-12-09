"""Unit tests for the core helpers: the library, the callbacks, the log, files, strings and events.

Bugs these tests fixed:
- a message with a % was read by cerver_log_* as a printf conversion (a crash with %s)
- the calls with format arguments of the services, cerver_log_both (t, t, b"%s", value), kept working
- a String with a NUL byte was cut at it by the readers of the package
"""

import ctypes
import os
import pytest
import subprocess
import sys
import tempfile

from cerver import callbacks
from cerver.callbacks import callback_keep, callback_wrap, callback_release
from cerver.core import files_get_file_extension, files_sanitize, files_sanitize_complete
from cerver.core import file_read, file_n_read, file_exists
from cerver.core import cerver_create_web, cerver_teardown, cerver_is_running, cerver_type_to_string
from cerver.core import cerver_event_on, cerver_event_unregister, CERVER_EVENT_STARTED, CERVER_TYPE_WEB
from cerver.core import cerver_error_type_description, CERVER_ERROR_FILE_NOT_FOUND
from cerver.core import cerver_auth_error_to_string, CERVER_AUTH_ERROR_FAILED
from cerver.core import timer_get_current_time
from cerver.lib import lib_c_string, lib_text, lib_candidates, CERVER_LIBRARY_VARIABLE
from cerver.types import str_new, string_take_text, string_bytes

pytestmark = [pytest.mark.unit]

LOG_TIMEOUT_SECONDS = 16

CallbackType = ctypes.CFUNCTYPE (None, ctypes.c_void_p)

def _callback (value):
	return None

class TestLibrary:

	def test_configured_path_goes_first (self, monkeypatch):
		monkeypatch.setenv (CERVER_LIBRARY_VARIABLE, "/opt/custom/libcerver.so")
		assert lib_candidates ()[0] == "/opt/custom/libcerver.so"

	def test_c_string (self):
		assert lib_c_string ("ñ") == "ñ".encode ("utf-8")
		assert lib_c_string (b"x") == b"x"
		assert lib_c_string (None) is None

	def test_text (self):
		assert lib_text (b"abc") == "abc"
		assert lib_text (b"\xff") is None
		assert lib_text (None) is None

class TestCallbacks:

	def test_wrap_keeps_the_callback (self):
		callback = callback_wrap (_callback, CallbackType)
		assert isinstance (callback, CallbackType)
		assert callbacks.callbacks[id (callback)] is callback

	def test_wrap_of_a_callback_is_the_same (self):
		callback = CallbackType (_callback)
		assert callback_wrap (callback, CallbackType) is callback

	def test_release (self):
		callback = callback_keep (CallbackType (_callback))
		callback_release (callback)
		assert id (callback) not in callbacks.callbacks

	def test_a_plain_function_is_rejected_by_a_callback_argument (self):
		from cerver.http import http_cerver_set_catch_all_route

		with pytest.raises (ctypes.ArgumentError):
			http_cerver_set_catch_all_route (None, _callback)

LOG_SCRIPT = """
import sys
from cerver import cerver_init, cerver_end
from cerver.utils import cerver_log_error, cerver_log_success, cerver_log_msg, cerver_log_both
from cerver.utils import LOG_TYPE_NONE, LOG_TYPE_HTTP
message = sys.argv[1]
cerver_init ()
cerver_log_error (message)
cerver_log_success (message.encode ("utf-8"))
cerver_log_msg (message)
cerver_log_both (LOG_TYPE_NONE, LOG_TYPE_HTTP, message)
cerver_end ()
"""

LOG_WRITES = 4

LOG_ARGUMENTS_SCRIPT = """
import sys
from cerver import cerver_init, cerver_end
from cerver.utils import cerver_log_error, cerver_log_success, cerver_log_both
from cerver.utils import LOG_TYPE_NONE
value = sys.argv[1]
cerver_init ()
cerver_log_both (LOG_TYPE_NONE, LOG_TYPE_NONE, "Version: %s - %s".encode ("utf-8"), value.encode ("utf-8"), b"end")
cerver_log_success (b"Bytes: %s", value)
cerver_log_error ("Text: %s %d", value.encode ("utf-8"), 7)
cerver_end ()
"""

class TestLog:

	@pytest.mark.parametrize ("value", ["1.0", "with %s and %n"])
	def test_messages_with_arguments_are_formatted (self, value):
		result = subprocess.run (
			[sys.executable, "-c", LOG_ARGUMENTS_SCRIPT, value],
			capture_output=True, text=True, errors="replace", timeout=LOG_TIMEOUT_SECONDS
		)

		output = result.stdout + result.stderr

		assert result.returncode == 0, result.stderr
		assert f"Version: {value} - end" in output
		assert f"Bytes: {value}" in output
		assert f"Text: {value} 7" in output

	@pytest.mark.parametrize ("message", ["plain", "with %s and %d and %n", "ñandú %%"])
	def test_messages_are_written_as_they_are (self, message):
		result = subprocess.run (
			[sys.executable, "-c", LOG_SCRIPT, message],
			capture_output=True, text=True, errors="replace", timeout=LOG_TIMEOUT_SECONDS
		)

		assert result.returncode == 0, result.stderr
		assert (result.stdout + result.stderr).count (message) == LOG_WRITES

class TestFiles:

	def test_extension (self):
		assert files_get_file_extension ("photo.final.png") == "png"
		assert files_get_file_extension ("without") is None

	def test_sanitize (self):
		assert files_sanitize ("a b/c?d.png") == "abcd.png"
		assert files_sanitize_complete ("a b/c?d.png") == "ab/cd.png"

	def test_read (self):
		with tempfile.NamedTemporaryFile (delete=False) as temporary:
			temporary.write (b"abc\x00def")

		try:
			assert file_exists (temporary.name.encode ("utf-8"))
			assert file_read (temporary.name) == b"abc\x00def"
			assert file_n_read (temporary.name, 3) == b"abc"

		finally:
			os.unlink (temporary.name)

	def test_read_missing (self):
		assert file_read ("/tmp/pycerver-missing-file") is None

class TestStrings:

	def test_string_of_cerver (self):
		assert string_take_text (str_new (b"value")) == "value"

	def test_bytes_with_its_length (self):
		string = str_new (b"ab")
		assert string_bytes (string) == b"ab"
		string_take_text (string)

class TestDescriptions:

	def test_type (self):
		assert cerver_type_to_string (CERVER_TYPE_WEB) == b"Web"

	def test_error (self):
		assert cerver_error_type_description (CERVER_ERROR_FILE_NOT_FOUND)

	def test_auth_error (self):
		assert cerver_auth_error_to_string (CERVER_AUTH_ERROR_FAILED) == b"Failed Auth"

	def test_time (self):
		assert timer_get_current_time () > 0

class TestEvents:

	def test_register_and_unregister (self):
		cerver = cerver_create_web (b"events-test", 0, 1)
		try:
			assert cerver_event_on (cerver, CERVER_EVENT_STARTED, lambda cerver, client, connection: None) == 0
			assert cerver_event_unregister (cerver, CERVER_EVENT_STARTED) == 0
			assert not cerver_is_running (cerver)

		finally:
			cerver_teardown (cerver)
