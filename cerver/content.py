from ctypes import c_int, c_char_p, c_bool

from .lib import lib

ContentType = c_int

HTTP_CONTENT_TYPE_NONE		= 0
HTTP_CONTENT_TYPE_HTML		= 1
HTTP_CONTENT_TYPE_CSS		= 2
HTTP_CONTENT_TYPE_JS		= 3
HTTP_CONTENT_TYPE_JSON		= 4
HTTP_CONTENT_TYPE_OCTET		= 5
HTTP_CONTENT_TYPE_JPG		= 6
HTTP_CONTENT_TYPE_PNG		= 7
HTTP_CONTENT_TYPE_ICO		= 8
HTTP_CONTENT_TYPE_GIF		= 9
HTTP_CONTENT_TYPE_MP3		= 10

http_content_type_string = lib.http_content_type_string
http_content_type_string.argtypes = [ContentType]
http_content_type_string.restype = c_char_p

http_content_type_description = lib.http_content_type_description
http_content_type_description.argtypes = [ContentType]
http_content_type_description.restype = c_char_p

http_content_type_by_string = lib.http_content_type_by_string
http_content_type_by_string.argtypes = [c_char_p]
http_content_type_by_string.restype = ContentType

http_content_type_by_extension = lib.http_content_type_by_extension
http_content_type_by_extension.argtypes = [c_char_p]
http_content_type_by_extension.restype = c_char_p

http_content_type_is_json = lib.http_content_type_is_json
http_content_type_is_json.argtypes = [c_char_p]
http_content_type_is_json.restype = c_bool
