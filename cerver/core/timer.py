"""The clock and the time formats of cerver."""

from ctypes import c_void_p, c_char_p, c_double

from ..lib import lib_function

from ..types.string import StringPointer

__all__ = [
	"CERVER_TIMER_BUFFER_SIZE",
	"timespec_delete", "timer_get_timespec", "timer_elapsed_time",
	"timer_sleep_for_seconds", "timer_get_current_time",
	"timer_get_gmt_time", "timer_get_local_time",
	"timer_time_to_string_actual", "timer_time_to_string",
	"timer_date_to_string_actual", "timer_date_to_string",
	"timer_date_and_time_to_string_actual", "timer_date_and_time_to_string",
	"timer_time_to_string_custom"
]

CERVER_TIMER_BUFFER_SIZE = 128

timespec_delete = lib_function (
	"timespec_delete", [c_void_p], None,
	"""Releases a timespec of timer_get_timespec ().

	Args:
		timespec_ptr: The timespec.
	"""
)

timer_get_timespec = lib_function (
	"timer_get_timespec", [], c_void_p,
	"""Returns the current monotonic time in a new timespec.

	Returns:
		The timespec, released with timespec_delete ().
	"""
)

timer_elapsed_time = lib_function (
	"timer_elapsed_time", [c_void_p, c_void_p], c_double,
	"""Returns the seconds between two timespecs.

	Args:
		start: The first timespec.
		end: The last timespec.

	Returns:
		The elapsed seconds.
	"""
)

timer_sleep_for_seconds = lib_function (
	"timer_sleep_for_seconds", [c_double], None,
	"""Sleeps the calling thread.

	Args:
		seconds: The seconds, with a fraction.
	"""
)

timer_get_current_time = lib_function (
	"timer_get_current_time", [], c_double,
	"""Returns the current time.

	Returns:
		The seconds since the epoch, with a fraction.
	"""
)

timer_get_gmt_time = lib_function (
	"timer_get_gmt_time", [], c_void_p,
	"""Returns the current UTC time as a struct tm of the thread.

	Returns:
		The struct tm, it must not be released.
	"""
)

timer_get_local_time = lib_function (
	"timer_get_local_time", [], c_void_p,
	"""Returns the current local time as a struct tm of the thread.

	Returns:
		The struct tm, it must not be released.
	"""
)

timer_time_to_string_actual = lib_function (
	"timer_time_to_string_actual", [c_void_p, c_void_p], None,
	"""Writes the 24h time of a struct tm in a buffer.

	Args:
		timeinfo: The struct tm.
		buffer: A writable buffer of at least CERVER_TIMER_BUFFER_SIZE bytes.
	"""
)

timer_time_to_string = lib_function (
	"timer_time_to_string", [c_void_p], StringPointer,
	"""Returns the 24h time of a struct tm.

	Args:
		timeinfo: The struct tm.

	Returns:
		A new StringPointer.
	"""
)

timer_date_to_string_actual = lib_function (
	"timer_date_to_string_actual", [c_void_p, c_void_p], None,
	"""Writes the day/month/year of a struct tm in a buffer.

	Args:
		timeinfo: The struct tm.
		buffer: A writable buffer of at least CERVER_TIMER_BUFFER_SIZE bytes.
	"""
)

timer_date_to_string = lib_function (
	"timer_date_to_string", [c_void_p], StringPointer,
	"""Returns the day/month/year of a struct tm.

	Args:
		timeinfo: The struct tm.

	Returns:
		A new StringPointer.
	"""
)

timer_date_and_time_to_string_actual = lib_function (
	"timer_date_and_time_to_string_actual", [c_void_p, c_void_p], None,
	"""Writes the day/month/year and the 24h time of a struct tm in a buffer.

	Args:
		timeinfo: The struct tm.
		buffer: A writable buffer of at least CERVER_TIMER_BUFFER_SIZE bytes.
	"""
)

timer_date_and_time_to_string = lib_function (
	"timer_date_and_time_to_string", [c_void_p], StringPointer,
	"""Returns the day/month/year and the 24h time of a struct tm.

	Args:
		timeinfo: The struct tm.

	Returns:
		A new StringPointer.
	"""
)

timer_time_to_string_custom = lib_function (
	"timer_time_to_string_custom", [c_void_p, c_char_p], StringPointer,
	"""Returns the time of a struct tm with a strftime () format.

	Args:
		timeinfo: The struct tm.
		format: The format, as bytes.

	Returns:
		A new StringPointer.
	"""
)
