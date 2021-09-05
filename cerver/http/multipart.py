from ctypes import POINTER, c_void_p
from ctypes import c_int, c_uint, c_uint32, c_char_p, c_bool

from ..lib import lib

from ..types.string import String

MultiPartType = c_int

MULTI_PART_TYPE_NONE = 0
MULTI_PART_TYPE_FILE = 1
MULTI_PART_TYPE_VALUE = 2

http_multi_part_get_type = lib.http_multi_part_get_type
http_multi_part_get_type.argtypes = [c_void_p]
http_multi_part_get_type.restype = MultiPartType

http_multi_part_is_file = lib.http_multi_part_is_file
http_multi_part_is_file.argtypes = [c_void_p]
http_multi_part_is_file.restype = c_bool

http_multi_part_is_value = lib.http_multi_part_is_value
http_multi_part_is_value.argtypes = [c_void_p]
http_multi_part_is_value.restype = c_bool

http_multi_part_get_name = lib.http_multi_part_get_name
http_multi_part_get_name.argtypes = [c_void_p]
http_multi_part_get_name.restype = POINTER (String)

http_multi_part_get_filename = lib.http_multi_part_get_filename
http_multi_part_get_filename.argtypes = [c_void_p]
http_multi_part_get_filename.restype = c_char_p

http_multi_part_get_filename_len = lib.http_multi_part_get_filename_len
http_multi_part_get_filename_len.argtypes = [c_void_p]
http_multi_part_get_filename_len.restype = c_int

http_multi_part_get_generated_filename = lib.http_multi_part_get_generated_filename
http_multi_part_get_generated_filename.argtypes = [c_void_p]
http_multi_part_get_generated_filename.restype = c_char_p

http_multi_part_get_generated_filename_len = lib.http_multi_part_get_generated_filename_len
http_multi_part_get_generated_filename_len.argtypes = [c_void_p]
http_multi_part_get_generated_filename_len.restype = c_int

http_multi_part_set_generated_filename = lib.http_multi_part_set_generated_filename

http_multi_part_get_n_reads = lib.http_multi_part_get_n_reads
http_multi_part_get_n_reads.argtypes = [c_void_p]
http_multi_part_get_n_reads.restype = c_uint32

http_multi_part_get_total_wrote = lib.http_multi_part_get_total_wrote
http_multi_part_get_total_wrote.argtypes = [c_void_p]
http_multi_part_get_total_wrote.restype = c_uint32

http_multi_part_get_saved_filename = lib.http_multi_part_get_saved_filename
http_multi_part_get_saved_filename.argtypes = [c_void_p]
http_multi_part_get_saved_filename.restype = c_char_p

http_multi_part_get_saved_filename_len = lib.http_multi_part_get_saved_filename_len
http_multi_part_get_saved_filename_len.argtypes = [c_void_p]
http_multi_part_get_saved_filename_len.restype = c_int

http_multi_part_get_moved_file = lib.http_multi_part_get_moved_file
http_multi_part_get_moved_file.argtypes = [c_void_p]
http_multi_part_get_moved_file.restype = c_bool

http_multi_part_get_value = lib.http_multi_part_get_value
http_multi_part_get_value.argtypes = [c_void_p]
http_multi_part_get_value.restype = c_char_p

http_multi_part_get_value_len = lib.http_multi_part_get_value_len
http_multi_part_get_value_len.argtypes = [c_void_p]
http_multi_part_get_value_len.restype = c_int

http_multi_part_move_file = lib.http_multi_part_move_file
http_multi_part_move_file.argtypes = [c_void_p, c_char_p]
http_multi_part_move_file.restype = c_uint

http_multi_part_headers_print = lib.http_multi_part_headers_print
http_multi_part_headers_print.argtypes = [c_void_p]

http_multi_part_print = lib.http_multi_part_print
http_multi_part_print.argtypes = [c_void_p]
