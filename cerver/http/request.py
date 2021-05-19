from ctypes import c_int, c_uint, c_void_p, c_char_p, c_bool, POINTER

import json

from ..lib import lib

from ..types.string import String

from .content import ContentType
from .headers import HttpHeader
from .query import http_query_pairs_get_value

RequestMethod = c_int

REQUEST_METHOD_DELETE = 0
REQUEST_METHOD_GET = 1
REQUEST_METHOD_HEAD = 2
REQUEST_METHOD_POST = 3
REQUEST_METHOD_PUT = 4

# getters
http_request_get_method = lib.http_request_get_method
http_request_get_method.argtypes = [c_void_p]
http_request_get_method.restype = RequestMethod

http_request_get_url = lib.http_request_get_url
http_request_get_url.argtypes = [c_void_p]
http_request_get_url.restype = POINTER (String)

http_request_get_query = lib.http_request_get_query
http_request_get_query.argtypes = [c_void_p]
http_request_get_query.restype = POINTER (String)

http_request_get_query_params = lib.http_request_get_query_params
http_request_get_query_params.argtypes = [c_void_p]
http_request_get_query_params.restype = c_void_p

http_request_get_n_params = lib.http_request_get_n_params
http_request_get_n_params.argtypes = [c_void_p]
http_request_get_n_params.restype = c_uint

http_request_get_param_at_idx = lib.http_request_get_param_at_idx
http_request_get_param_at_idx.argtypes = [c_void_p, c_uint]
http_request_get_param_at_idx.restype = POINTER (String)

http_request_get_header = lib.http_request_get_header
http_request_get_header.argtypes = [c_void_p, HttpHeader]
http_request_get_header.restype = POINTER (String)

http_request_get_content_type = lib.http_request_get_content_type
http_request_get_content_type.argtypes = [c_void_p]
http_request_get_content_type.restype = ContentType

http_request_get_content_type_string = lib.http_request_get_content_type_string
http_request_get_content_type_string.argtypes = [c_void_p]
http_request_get_content_type_string.restype = POINTER (String)

http_request_content_type_is_json = lib.http_request_content_type_is_json
http_request_content_type_is_json.argtypes = [c_void_p]
http_request_content_type_is_json.restype = c_bool

http_request_get_decoded_data = lib.http_request_get_decoded_data
http_request_get_decoded_data.argtypes = [c_void_p]
http_request_get_decoded_data.restype = c_void_p

http_request_get_body = lib.http_request_get_body
http_request_get_body.argtypes = [c_void_p]
http_request_get_body.restype = POINTER (String)

http_request_get_body_values = lib.http_request_get_body_values
http_request_get_body_values.argtypes = [c_void_p]
http_request_get_body_values.restype = c_void_p

def http_request_get_query_value (values, query_name):
	"""
	Function to get a query param from request
	# Parameters
	------------
	### values: DoubleList <KeyValuePair>
		key-value pairs parsed from x-www-form-urlencoded data or query params
	### query_name: string
		the key used to find a matching value
	"""
	value = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	return value.contents.str.decode ("utf-8")

def http_request_get_body_json (request):
	"""
	Function to get body in a dictionary
	# Parameters
	------------
	### request: HttpRequest
		reference to a HTTP request instance
	"""
	body_str = http_request_get_body (request)
	body = json.loads (body_str.contents.str.decode ("utf-8"))
	return body

# headers
http_request_headers_print = lib.http_request_headers_print
http_request_headers_print.argtypes = [c_void_p]

# query
http_request_query_params_print = lib.http_request_query_params_print
http_request_query_params_print.argtypes = [c_void_p]

http_request_query_params_get_value = lib.http_request_query_params_get_value
http_request_query_params_get_value.argtypes = [c_void_p, c_char_p]
http_request_query_params_get_value.restype = POINTER (String)

# multi-parts
http_request_multi_parts_get_value = lib.http_request_multi_parts_get_value
http_request_multi_parts_get_value.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_value.restype = POINTER (String)

http_request_multi_parts_get_filename = lib.http_request_multi_parts_get_filename
http_request_multi_parts_get_filename.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_filename.restype = c_char_p

http_request_multi_parts_get_saved_filename = lib.http_request_multi_parts_get_saved_filename
http_request_multi_parts_get_saved_filename.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_saved_filename.restype = c_char_p

http_request_multi_part_keep_files = lib.http_request_multi_part_keep_files
http_request_multi_part_keep_files.argtypes = [c_void_p]

http_request_multi_part_discard_files = lib.http_request_multi_part_discard_files
http_request_multi_part_discard_files.argtypes = [c_void_p]

http_request_multi_parts_print = lib.http_request_multi_parts_print
http_request_multi_parts_print.argtypes = [c_void_p]

# body
http_request_body_get_value = lib.http_request_body_get_value
http_request_body_get_value.argtypes = [c_void_p, c_char_p]
http_request_body_get_value.restype = POINTER (String)
