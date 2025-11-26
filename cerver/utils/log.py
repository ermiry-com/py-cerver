"""The log of cerver: its configuration and the functions that write to it."""

from ctypes import c_int, c_uint, c_char_p, c_bool
from typing import TypeAlias

from ..lib import lib, lib_function

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
cerver_log = lib.cerver_log
cerver_log_with_date = lib.cerver_log_with_date
cerver_log_both = lib.cerver_log_both
cerver_log_msg = lib.cerver_log_msg
cerver_log_error = lib.cerver_log_error
cerver_log_warning = lib.cerver_log_warning
cerver_log_success = lib.cerver_log_success
cerver_log_debug = lib.cerver_log_debug
cerver_log_raw = lib.cerver_log_raw
cerver_log_line_break = lib.cerver_log_line_break
