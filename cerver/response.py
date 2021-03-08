from ctypes import c_char_p, c_uint8, c_void_p, c_uint

from .lib import lib

from .status import http_status

http_response_json_msg_send = lib.http_response_json_msg_send
http_response_json_msg_send.argtypes = [c_void_p, c_uint, c_char_p]
http_response_json_msg_send.restype = c_uint8
