from ctypes import POINTER, CFUNCTYPE, c_void_p
from ctypes import c_int, c_uint, c_uint8, c_char_p, c_bool

import json

from ..lib import lib

from ..types.string import String

from .content import ContentType
from .headers import http_header
from .query import http_query_pairs_get_value

RequestMethod = c_int

REQUEST_METHOD_DELETE = 0
REQUEST_METHOD_GET = 1
REQUEST_METHOD_HEAD = 2
REQUEST_METHOD_POST = 3
REQUEST_METHOD_PUT = 4
REQUEST_METHOD_CONNECT = 5
REQUEST_METHOD_OPTIONS = 6
REQUEST_METHOD_TRACE = 7

REQUEST_METHOD_UNDEFINED = 8

RequestDeleteDecoded = CFUNCTYPE (None, c_void_p)
RequestDeleteCustom = CFUNCTYPE (None, c_void_p)

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
http_request_get_header.argtypes = [c_void_p, http_header]
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

http_request_set_decoded_data = lib.http_request_set_decoded_data
http_request_set_decoded_data.argtypes = [c_void_p, c_void_p]

http_request_set_delete_decoded_data = lib.http_request_set_delete_decoded_data
http_request_set_delete_decoded_data.argtypes = [c_void_p, RequestDeleteDecoded]

http_request_set_default_delete_decoded_data = lib.http_request_set_default_delete_decoded_data
http_request_set_default_delete_decoded_data.argtypes = [c_void_p]

http_request_get_custom_data = lib.http_request_get_custom_data
http_request_get_custom_data.argtypes = [c_void_p]
http_request_get_custom_data.restype = c_void_p

http_request_set_custom_data = lib.http_request_set_custom_data
http_request_set_custom_data.argtypes = [c_void_p, c_void_p]

http_request_set_delete_custom_data = lib.http_request_set_delete_custom_data
http_request_set_delete_custom_data.argtypes = [c_void_p, RequestDeleteCustom]

http_request_set_default_delete_custom_data = lib.http_request_set_default_delete_custom_data
http_request_set_default_delete_custom_data.argtypes = [c_void_p]

http_request_get_body = lib.http_request_get_body
http_request_get_body.argtypes = [c_void_p]
http_request_get_body.restype = POINTER (String)

http_request_get_current_mpart = lib.http_request_get_current_mpart
http_request_get_current_mpart.argtypes = [c_void_p]
http_request_get_current_mpart.restype = c_void_p

http_request_get_n_files = lib.http_request_get_n_files
http_request_get_n_files.argtypes = [c_void_p]
http_request_get_n_files.restype = c_uint8

http_request_get_n_values = lib.http_request_get_n_values
http_request_get_n_values.argtypes = [c_void_p]
http_request_get_n_values.restype = c_uint8

http_request_get_dirname_len = lib.http_request_get_dirname_len
http_request_get_dirname_len.argtypes = [c_void_p]
http_request_get_dirname_len.restype = c_int

http_request_get_dirname = lib.http_request_get_dirname
http_request_get_dirname.argtypes = [c_void_p]
http_request_get_dirname.restype = c_char_p

http_request_set_dirname = lib.http_request_set_dirname

http_request_get_body_values = lib.http_request_get_body_values
http_request_get_body_values.argtypes = [c_void_p]
http_request_get_body_values.restype = c_void_p

def http_get_params_list (request) -> list:
	"""
	Method to get all request's params as a list
	# Parameters
	------------
	### request: HttpRequest
		Reference to a HTTP request instance
	# Returns
	-----------
	The HTTP request's params as a list
	"""
	params = []
	try:
		n_params = http_request_get_n_params (request)
		for idx in range (n_params):
			params.append (
				http_request_get_param_at_idx (
					request, idx
				).contents.str.decode ("utf-8"))

	# error getting values from request
	except:
		params = None

	return params

def http_request_get_query_value (values, query_name):
	"""
	Method to get a query param from request
	# Parameters
	------------
	### values: DoubleList <KeyValuePair>
		Key-value pairs parsed from x-www-form-urlencoded data or query params
	### query_name: string
		The key used to find a matching value
	"""
	value = http_query_pairs_get_value (values, query_name.encode ("utf-8"))
	return value.contents.str.decode ("utf-8")

def http_request_get_body_json (request):
	"""
	Method to get body in a dictionary
	# Parameters
	------------
	### request: HttpRequest
		Reference to a HTTP request instance
	"""
	body_str = http_request_get_body (request)
	body = json.loads (body_str.contents.str.decode ("utf-8"))
	return body

# headers
http_request_headers_print = lib.http_request_headers_print
http_request_headers_print.argtypes = [c_void_p]

http_request_headers_print_full = lib.http_request_headers_print_full
http_request_headers_print_full.argtypes = [c_void_p]

# query
http_request_query_params_print = lib.http_request_query_params_print
http_request_query_params_print.argtypes = [c_void_p]

http_request_query_params_get_value = lib.http_request_query_params_get_value
http_request_query_params_get_value.argtypes = [c_void_p, c_char_p]
http_request_query_params_get_value.restype = POINTER (String)

# multi-parts
http_request_multi_parts_get = lib.http_request_multi_parts_get
http_request_multi_parts_get.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get.restype = c_void_p

http_request_multi_parts_get_value = lib.http_request_multi_parts_get_value
http_request_multi_parts_get_value.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_value.restype = c_char_p

http_request_multi_parts_get_filename = lib.http_request_multi_parts_get_filename
http_request_multi_parts_get_filename.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_filename.restype = c_char_p

http_request_multi_parts_get_saved_filename = lib.http_request_multi_parts_get_saved_filename
http_request_multi_parts_get_saved_filename.argtypes = [c_void_p, c_char_p]
http_request_multi_parts_get_saved_filename.restype = c_char_p

http_request_multi_parts_iter_start = lib.http_request_multi_parts_iter_start
http_request_multi_parts_iter_start.argtypes = [c_void_p]
http_request_multi_parts_iter_start.restype = c_bool

http_request_multi_parts_iter_get_next = lib.http_request_multi_parts_iter_get_next
http_request_multi_parts_iter_get_next.argtypes = [c_void_p]
http_request_multi_parts_iter_get_next.restype = c_void_p

http_request_multi_part_keep_files = lib.http_request_multi_part_keep_files
http_request_multi_part_keep_files.argtypes = [c_void_p]

http_request_multi_part_discard_files = lib.http_request_multi_part_discard_files
http_request_multi_part_discard_files.argtypes = [c_void_p]

http_request_multi_parts_print = lib.http_request_multi_parts_print
http_request_multi_parts_print.argtypes = [c_void_p]

http_request_multi_parts_files_print = lib.http_request_multi_parts_files_print
http_request_multi_parts_files_print.argtypes = [c_void_p]

# body
http_request_body_get_value = lib.http_request_body_get_value
http_request_body_get_value.argtypes = [c_void_p, c_char_p]
http_request_body_get_value.restype = POINTER (String)
