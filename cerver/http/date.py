"""The dates of HTTP, IMF-fixdates like "Sun, 06 Nov 1994 08:49:37 GMT"."""

from ctypes import POINTER, byref, create_string_buffer
from ctypes import c_bool, c_char_p, c_long, c_size_t, c_void_p

from ..lib import lib_function, lib_c_string, lib_text

__all__ = [
	"HTTP_DATE_LENGTH", "HTTP_DATE_SIZE",
	"http_date_format", "http_date_current", "http_date_parse",
	"http_date_text", "http_date_seconds"
]

HTTP_DATE_LENGTH = 29
HTTP_DATE_SIZE = HTTP_DATE_LENGTH + 1

http_date_format = lib_function (
	"http_date_format", [c_long, c_void_p], c_size_t,
	"""Writes a time as an IMF-fixdate, the names never depend on the locale.

	Args:
		seconds: The seconds since the epoch.
		date: A writable buffer of at least HTTP_DATE_SIZE bytes.

	Returns:
		The length of the date, 0 on error.
	"""
)

http_date_current = lib_function (
	"http_date_current", [], c_char_p,
	"""Returns the current time as an IMF-fixdate, formatted once per second by each thread.

	Returns:
		The date, as bytes.
	"""
)

http_date_parse = lib_function (
	"http_date_parse", [c_char_p, c_size_t, POINTER (c_long)], c_bool,
	"""Parses an IMF-fixdate, the only format of the conditional requests.

	Args:
		value: The date, as bytes.
		length: Its length.
		seconds: A pointer to a c_long that gets the seconds since the epoch.

	Returns:
		True on success.
	"""
)

def http_date_text (seconds: int) -> str | None:
	"""Returns a time as an IMF-fixdate.

	Args:
		seconds: The seconds since the epoch.

	Returns:
		The date, None on error.
	"""
	result = None

	buffer = create_string_buffer (HTTP_DATE_SIZE)
	if (http_date_format (seconds, buffer)):
		result = lib_text (buffer.value)

	return result

def http_date_seconds (value: str | bytes) -> int | None:
	"""Parses an IMF-fixdate.

	Args:
		value: The date.

	Returns:
		The seconds since the epoch, None if it is not an IMF-fixdate.
	"""
	result = None

	date = lib_c_string (value)
	seconds = c_long (0)
	if (http_date_parse (date, len (date), byref (seconds))):
		result = seconds.value

	return result
