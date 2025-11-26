"""The log of cerver: its configuration and the functions that write to it.

The functions of cerver that write a message are variadic, with the message as a
printf format. The functions of this module always pass the message as an argument
of a ``"%s"`` format, so a ``%`` in a message (like one that comes from a client)
is written as it is instead of being read as a conversion. A message with arguments
is formatted in Python (``message % arguments``) before it reaches cerver, so the
calls written for the variadic functions, like ``cerver_log_success (b"%s", name)``,
keep working. The C functions are kept as ``*_variadic`` for the callers that need
a real printf format.
"""

from ctypes import c_int, c_uint, c_char_p, c_bool
from typing import Any, TypeAlias

from ..lib import lib_function, lib_c_string

__all__ = [
	"LogType",
	"LOG_TYPE_NONE", "LOG_TYPE_ERROR", "LOG_TYPE_WARNING", "LOG_TYPE_SUCCESS",
	"LOG_TYPE_DEBUG", "LOG_TYPE_TEST", "LOG_TYPE_CERVER", "LOG_TYPE_CLIENT",
	"LOG_TYPE_CONNECTION", "LOG_TYPE_HANDLER", "LOG_TYPE_ADMIN", "LOG_TYPE_EVENT",
	"LOG_TYPE_PACKET", "LOG_TYPE_REQ", "LOG_TYPE_FILE", "LOG_TYPE_HTTP",
	"LOG_TYPE_GAME", "LOG_TYPE_PLAYER",
	"LOG_DEFAULT_PATH", "LOG_FILENAME_SIZE", "LOG_MESSAGE_SIZE", "LOG_DEFAULT_UPDATE_INTERVAL",
	"LogOutputType",
	"LOG_OUTPUT_TYPE_NONE", "LOG_OUTPUT_TYPE_STD", "LOG_OUTPUT_TYPE_FILE", "LOG_OUTPUT_TYPE_BOTH",
	"LogTimeType",
	"LOG_TIME_TYPE_NONE", "LOG_TIME_TYPE_TIME", "LOG_TIME_TYPE_DATE", "LOG_TIME_TYPE_BOTH",
	"cerver_log_get_output_type", "cerver_log_set_output_type",
	"cerver_log_set_path", "cerver_log_set_update_interval",
	"cerver_log_time_type_to_string", "cerver_log_time_type_description",
	"cerver_log_get_time_config", "cerver_log_set_time_config",
	"cerver_log_set_local_time", "cerver_log_set_quiet",
	"cerver_log_variadic", "cerver_log_with_date_variadic", "cerver_log_both_variadic",
	"cerver_log_msg_variadic", "cerver_log_error_variadic", "cerver_log_warning_variadic",
	"cerver_log_success_variadic", "cerver_log_debug_variadic", "cerver_log_raw_variadic",
	"cerver_log", "cerver_log_with_date", "cerver_log_both",
	"cerver_log_msg", "cerver_log_error", "cerver_log_warning",
	"cerver_log_success", "cerver_log_debug", "cerver_log_raw",
	"cerver_log_line_break"
]

LogType: TypeAlias = c_int # type: ignore

LOG_TYPE_NONE = 0
LOG_TYPE_ERROR = 1
LOG_TYPE_WARNING = 2
LOG_TYPE_SUCCESS = 3
LOG_TYPE_DEBUG = 4
LOG_TYPE_TEST = 5
LOG_TYPE_CERVER = 6
LOG_TYPE_CLIENT = 7
LOG_TYPE_CONNECTION = 8
LOG_TYPE_HANDLER = 9
LOG_TYPE_ADMIN = 10
LOG_TYPE_EVENT = 11
LOG_TYPE_PACKET = 12
LOG_TYPE_REQ = 13
LOG_TYPE_FILE = 14
LOG_TYPE_HTTP = 15
LOG_TYPE_GAME = 16
LOG_TYPE_PLAYER = 17

LOG_DEFAULT_PATH = "/var/log/cerver"
LOG_FILENAME_SIZE = 1024
LOG_MESSAGE_SIZE = 4096
LOG_DEFAULT_UPDATE_INTERVAL = 1

# the format that writes a message as it is
LOG_MESSAGE_FORMAT = b"%s"

# configuration
LogOutputType: TypeAlias = c_int # type: ignore

LOG_OUTPUT_TYPE_NONE = 0
LOG_OUTPUT_TYPE_STD = 1
LOG_OUTPUT_TYPE_FILE = 2
LOG_OUTPUT_TYPE_BOTH = 3

cerver_log_get_output_type = lib_function (
	"cerver_log_get_output_type", [], LogOutputType,
	"""Returns the current output of the log.

	Returns:
		A LOG_OUTPUT_TYPE_* value.
	"""
)

cerver_log_set_output_type = lib_function (
	"cerver_log_set_output_type", [LogOutputType], None,
	"""Sets where the log writes its messages.

	Args:
		type: LOG_OUTPUT_TYPE_STD (stdout and stderr), LOG_OUTPUT_TYPE_FILE or LOG_OUTPUT_TYPE_BOTH.
	"""
)

cerver_log_set_path = lib_function (
	"cerver_log_set_path", [c_char_p], c_uint,
	"""Sets the directory where the log files are written.

	Args:
		pathname: The directory, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

cerver_log_set_update_interval = lib_function (
	"cerver_log_set_update_interval", [c_uint], None,
	"""Sets how often the log file is synced to disk.

	Args:
		interval: The interval in seconds, LOG_DEFAULT_UPDATE_INTERVAL by default.
	"""
)

LogTimeType: TypeAlias = c_int # type: ignore

LOG_TIME_TYPE_NONE = 0
LOG_TIME_TYPE_TIME = 1
LOG_TIME_TYPE_DATE = 2
LOG_TIME_TYPE_BOTH = 3

cerver_log_time_type_to_string = lib_function (
	"cerver_log_time_type_to_string", [LogTimeType], c_char_p,
	"""Returns the name of a log time type.

	Args:
		type: A LOG_TIME_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_log_time_type_description = lib_function (
	"cerver_log_time_type_description", [LogTimeType], c_char_p,
	"""Returns the description of a log time type.

	Args:
		type: A LOG_TIME_TYPE_* value.

	Returns:
		The description, as bytes.
	"""
)

cerver_log_get_time_config = lib_function (
	"cerver_log_get_time_config", [], LogTimeType,
	"""Returns how the log writes the time of each message.

	Returns:
		A LOG_TIME_TYPE_* value.
	"""
)

cerver_log_set_time_config = lib_function (
	"cerver_log_set_time_config", [LogTimeType], None,
	"""Sets how the log writes the time of each message.

	Args:
		type: LOG_TIME_TYPE_NONE, LOG_TIME_TYPE_TIME (24h), LOG_TIME_TYPE_DATE
			(day/month/year) or LOG_TIME_TYPE_BOTH.
	"""
)

cerver_log_set_local_time = lib_function (
	"cerver_log_set_local_time", [c_bool], None,
	"""Sets if the time of the messages is the local time instead of UTC.

	Args:
		value: True for the local time.
	"""
)

cerver_log_set_quiet = lib_function (
	"cerver_log_set_quiet", [c_bool], None,
	"""Sets if the log only writes the success, warning and error messages.

	Args:
		value: True to ignore every other type.
	"""
)

# public
cerver_log_variadic = lib_function (
	"cerver_log", None, None,
	"""Writes a message with two types, the first one sets its color (variadic).

	Args:
		first_type: A LOG_TYPE_* value, as c_int.
		second_type: A LOG_TYPE_* value, as c_int.
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_with_date_variadic = lib_function (
	"cerver_log_with_date", None, None,
	"""Works like cerver_log_variadic () but always writes the date and the time.

	Args:
		first_type: A LOG_TYPE_* value, as c_int.
		second_type: A LOG_TYPE_* value, as c_int.
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_both_variadic = lib_function (
	"cerver_log_both", None, None,
	"""Writes a message to the standard output and to the log file, ignoring the quiet option.

	Args:
		first_type: A LOG_TYPE_* value, as c_int.
		second_type: A LOG_TYPE_* value, as c_int.
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_msg_variadic = lib_function (
	"cerver_log_msg", None, None,
	"""Writes a message without a type, like printf () (variadic).

	Args:
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_error_variadic = lib_function (
	"cerver_log_error", None, None,
	"""Writes a red error message to stderr (variadic).

	Args:
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_warning_variadic = lib_function (
	"cerver_log_warning", None, None,
	"""Writes a yellow warning message to stderr (variadic).

	Args:
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_success_variadic = lib_function (
	"cerver_log_success", None, None,
	"""Writes a green success message to stdout (variadic).

	Args:
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_debug_variadic = lib_function (
	"cerver_log_debug", None, None,
	"""Writes a debug message to stdout (variadic).

	Args:
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_raw_variadic = lib_function (
	"cerver_log_raw", None, None,
	"""Writes a message without a type and without a line break (variadic).

	Args:
		format: A printf format, as bytes, followed by its arguments.
	"""
)

cerver_log_line_break = lib_function (
	"cerver_log_line_break", [], None,
	"""Writes a line break."""
)

def log_argument (argument: Any, as_bytes: bool) -> Any:
	"""Returns an argument as the same kind of text of its message, any other value as it is."""
	result = argument
	if (as_bytes and isinstance (argument, str)):
		result = argument.encode ("utf-8")

	elif ((not as_bytes) and isinstance (argument, (bytes, bytearray))):
		result = bytes (argument).decode ("utf-8", "replace")

	return result

def log_message (message: str | bytes, arguments: tuple = ()) -> c_char_p:
	"""Returns a message of the caller, formatted with its arguments, as the argument of the format."""
	if (arguments):
		as_bytes = isinstance (message, (bytes, bytearray))
		message = message % tuple (log_argument (argument, as_bytes) for argument in arguments)

	return c_char_p (lib_c_string (message))

def cerver_log (first_type: int, second_type: int, message: str | bytes, *arguments: Any) -> None:
	"""Writes a message with two types, the first one sets its color.

	Args:
		first_type: A LOG_TYPE_* value.
		second_type: A LOG_TYPE_* value, LOG_TYPE_NONE for a single one.
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	cerver_log_variadic (
		LogType (first_type), LogType (second_type),
		c_char_p (LOG_MESSAGE_FORMAT), log_message (message, arguments)
	)

def cerver_log_with_date (first_type: int, second_type: int, message: str | bytes, *arguments: Any) -> None:
	"""Writes a message with two types, always with the date and the time.

	Args:
		first_type: A LOG_TYPE_* value.
		second_type: A LOG_TYPE_* value, LOG_TYPE_NONE for a single one.
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	cerver_log_with_date_variadic (
		LogType (first_type), LogType (second_type),
		c_char_p (LOG_MESSAGE_FORMAT), log_message (message, arguments)
	)

def cerver_log_both (first_type: int, second_type: int, message: str | bytes, *arguments: Any) -> None:
	"""Writes a message to the standard output and to the log file, ignoring the quiet option.

	Args:
		first_type: A LOG_TYPE_* value.
		second_type: A LOG_TYPE_* value, LOG_TYPE_NONE for a single one.
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	cerver_log_both_variadic (
		LogType (first_type), LogType (second_type),
		c_char_p (LOG_MESSAGE_FORMAT), log_message (message, arguments)
	)

def log_write (function: Any, message: str | bytes, arguments: tuple) -> None:
	"""Writes a message with a variadic function of a single format."""
	function (c_char_p (LOG_MESSAGE_FORMAT), log_message (message, arguments))

def cerver_log_msg (message: str | bytes, *arguments: Any) -> None:
	"""Writes a message without a type.

	Args:
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	log_write (cerver_log_msg_variadic, message, arguments)

def cerver_log_error (message: str | bytes, *arguments: Any) -> None:
	"""Writes a red error message to stderr.

	Args:
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	log_write (cerver_log_error_variadic, message, arguments)

def cerver_log_warning (message: str | bytes, *arguments: Any) -> None:
	"""Writes a yellow warning message to stderr.

	Args:
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	log_write (cerver_log_warning_variadic, message, arguments)

def cerver_log_success (message: str | bytes, *arguments: Any) -> None:
	"""Writes a green success message to stdout.

	Args:
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	log_write (cerver_log_success_variadic, message, arguments)

def cerver_log_debug (message: str | bytes, *arguments: Any) -> None:
	"""Writes a debug message to stdout.

	Args:
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	log_write (cerver_log_debug_variadic, message, arguments)

def cerver_log_raw (message: str | bytes, *arguments: Any) -> None:
	"""Writes a message without a type and without a line break.

	Args:
		message: The message, written as it is when it has no arguments.
		*arguments: The values of the ``%`` conversions of the message, formatted in Python.
	"""
	log_write (cerver_log_raw_variadic, message, arguments)
