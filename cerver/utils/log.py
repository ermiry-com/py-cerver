from ctypes import c_int, c_uint, c_char_p, c_bool

from ..lib import lib

LogType = c_int

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

# config
LogOutputType = c_int

LOG_OUTPUT_TYPE_NONE = 0
LOG_OUTPUT_TYPE_STD	 = 1
LOG_OUTPUT_TYPE_FILE = 2
LOG_OUTPUT_TYPE_BOTH = 3

cerver_log_get_output_type = lib.cerver_log_get_output_type
cerver_log_get_output_type.restype = LogOutputType

cerver_log_set_output_type = lib.cerver_log_set_output_type
cerver_log_set_output_type.argtypes = [LogOutputType]

cerver_log_set_path = lib.cerver_log_set_path
cerver_log_set_path.argtypes = [c_char_p]
cerver_log_set_path.restype = c_uint

cerver_log_set_update_interval = lib.cerver_log_set_update_interval
cerver_log_set_update_interval.argtypes = [c_uint]

LogTimeType = c_int

LOG_TIME_TYPE_NONE = 0
LOG_TIME_TYPE_TIME = 1
LOG_TIME_TYPE_DATE = 2
LOG_TIME_TYPE_BOTH = 3

cerver_log_time_type_to_string = lib.cerver_log_time_type_to_string
cerver_log_time_type_to_string.argtypes = [LogTimeType]
cerver_log_time_type_to_string.restype = c_char_p

cerver_log_time_type_description = lib.cerver_log_time_type_description
cerver_log_time_type_description.argtypes = [LogTimeType]
cerver_log_time_type_description.restype = c_char_p

cerver_log_get_time_config = lib.cerver_log_get_time_config
cerver_log_get_time_config.restype = LogTimeType

cerver_log_set_time_config = lib.cerver_log_set_time_config
cerver_log_set_time_config.argtypes = [LogTimeType]

cerver_log_set_local_time = lib.cerver_log_set_local_time
cerver_log_set_local_time.argtypes = [c_bool]

cerver_log_set_quiet = lib.cerver_log_set_quiet
cerver_log_set_quiet.argtypes = [c_bool]

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
