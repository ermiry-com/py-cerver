from ctypes import c_void_p, c_char_p, c_size_t
from ctypes import c_uint8, c_uint, c_int, c_long, c_double, c_bool

import json

from ..lib import lib

from .content import ContentType, HTTP_CONTENT_TYPE_HTML
from .headers import http_header
from .status import http_status

# correctly deletes the response and all of its data
http_response_delete = lib.http_response_delete
http_response_delete.argtypes = [c_void_p]

# gets a new HTTP response ready to be used
http_response_get = lib.http_response_get
http_response_get.restype = c_void_p

# correctly disposes a HTTP response
http_response_return = lib.http_response_return
http_response_return.argtypes = [c_void_p]

# sets the http response's status code to be set in the header when compilling
http_response_set_status = lib.http_response_set_status
http_response_set_status.argtypes = [c_void_p, http_status]

# sets the response's header, it will replace the existing one
# the data will be deleted when the response gets deleted
http_response_set_header = lib.http_response_set_header
http_response_set_header.argtypes = [c_void_p, c_void_p, c_size_t]

# adds a new header to the response
# the headers will be handled when calling 
# http_response_compile () to generate a continuos header buffer
# returns 0 on success, 1 on error
http_response_add_header = lib.http_response_add_header
http_response_add_header.argtypes = [c_void_p, http_header, c_char_p]
http_response_add_header.restype = c_uint8

# adds a "Content-Type" header to the response
# returns 0 on success, 1 on error
http_response_add_content_type_header = lib.http_response_add_content_type_header
http_response_add_content_type_header.argtypes = [c_void_p, ContentType]
http_response_add_content_type_header.restype = c_uint8

# adds a "Content-Length" header to the response
# returns 0 on success, 1 on error
http_response_add_content_length_header = lib.http_response_add_content_length_header
http_response_add_content_length_header.argtypes = [c_void_p, c_size_t]
http_response_add_content_length_header.restype = c_uint8

# adds a "Content-Type" with value "application/json"
# adds a "Content-Length" header to the response
http_response_add_json_headers = lib.http_response_add_json_headers
http_response_add_json_headers.argtypes = [c_void_p, c_size_t]

# adds an "Access-Control-Allow-Origin" header to the response
# returns 0 on success, 1 on error
http_response_add_cors_header = lib.http_response_add_cors_header
http_response_add_cors_header.argtypes = [c_void_p, c_char_p]
http_response_add_cors_header.restype = c_uint8

# works like http_response_add_cors_header ()
# but takes a HttpOrigin instead of a c string
http_response_add_cors_header_from_origin = lib.http_response_add_cors_header_from_origin
http_response_add_cors_header_from_origin.argtypes = [c_void_p, c_void_p]
http_response_add_cors_header_from_origin.restype = c_uint8

# works like http_response_add_cors_header () but first
# checks if the domain matches any entry in the whitelist
# returns 0 on success, 1 on error
http_response_add_whitelist_cors_header = lib.http_response_add_whitelist_cors_header
http_response_add_whitelist_cors_header.argtypes = [c_void_p, c_char_p]
http_response_add_whitelist_cors_header.restype = c_uint8

# works like http_response_add_whitelist_cors_header ()
# but takes a HttpOrigin instead of a c string
http_response_add_whitelist_cors_header_from_origin = lib.http_response_add_whitelist_cors_header_from_origin
http_response_add_whitelist_cors_header_from_origin.argtypes = [c_void_p, c_void_p]
http_response_add_whitelist_cors_header_from_origin.restype = c_uint8

# checks if the HTTP request's "Origin" header value
# matches any domain in the whitelist
# then adds an "Access-Control-Allow-Origin" header to the response
# returns 0 on success, 1 on error
http_response_add_whitelist_cors_header_from_request = lib.http_response_add_whitelist_cors_header_from_request
http_response_add_whitelist_cors_header_from_request.argtypes = [c_void_p, c_void_p]
http_response_add_whitelist_cors_header_from_request.restype = c_uint8

# sets CORS related header "Access-Control-Allow-Credentials"
# this header is needed when a CORS request has an "Authorization" header
http_response_add_cors_allow_credentials_header = lib.http_response_add_cors_allow_credentials_header
http_response_add_cors_allow_credentials_header.argtypes = [c_void_p]
http_response_add_cors_allow_credentials_header.restype = c_uint8

# sets CORS related header "Access-Control-Allow-Methods"
# to be a list of available methods like "GET, HEAD, OPTIONS"
# this header is needed in preflight OPTIONS request's responses
# returns 0 on success, 1 on error
http_response_add_cors_allow_methods_header = lib.http_response_add_cors_allow_methods_header
http_response_add_cors_allow_methods_header.argtypes = [c_void_p, c_char_p]
http_response_add_cors_allow_methods_header.restype = c_uint8

# sets the response's data (body), it will replace the existing one
# the data will be deleted when the response gets deleted
http_response_set_data = lib.http_response_set_data
http_response_set_data.argtypes = [c_void_p, c_void_p, c_size_t]

# sets a reference to a data buffer to send
# data will not be copied into the response and will not be freed after use
# this method is similar to packet_set_data_ref ()
# returns 0 on success, 1 on error
http_response_set_data_ref = lib.http_response_set_data_ref
http_response_set_data_ref.argtypes = [c_void_p, c_void_p, c_size_t]
http_response_set_data_ref.restype = c_uint8

# creates a new http response with the specified status code
# ability to set the response's data (body); it will be copied to the response
# and the original data can be safely deleted 
http_response_create = lib.http_response_create
http_response_create.argtypes = [http_status, c_void_p, c_size_t]
http_response_create.restype = c_void_p

# merges the response header and the data into the final response
# returns 0 on success, 1 on error
http_response_compile = lib.http_response_compile
http_response_compile.argtypes = [c_void_p]
http_response_compile.restype = c_uint8

http_response_print = lib.http_response_print
http_response_print.argtypes = [c_void_p]

# send
# sends a response through the connection's socket
# returns 0 on success, 1 on error
http_response_send = lib.http_response_send
http_response_send.argtypes = [c_void_p, c_void_p]
http_response_send.restype = c_uint8

# expects a response with an already created header and data
# as this method will send both parts without the need of a continuos response buffer
# use this for maximun efficiency
# returns 0 on success, 1 on error
http_response_send_split = lib.http_response_send_split
http_response_send_split.argtypes = [c_void_p, c_void_p]
http_response_send_split.restype = c_uint8

# creates & sends a response through the connection's socket
# returns 0 on success, 1 on error
http_response_create_and_send = lib.http_response_create_and_send
http_response_create_and_send.argtypes = [http_status, c_void_p, c_size_t, c_void_p]
http_response_create_and_send.restype = c_uint8

def http_send_response (
	http_receive, status_code,
	body, body_len = None,
	content_type = HTTP_CONTENT_TYPE_HTML
):
	"""
	Function to create and send a HTTP response
	# Parameters
	------------
	### http_receive : HttpReceive
		The receive structure associated with the current request
	### status_code : int, optional
		HTTP status code value
	### body: dict, str, bytes
		Value(s) to send in the response's body
	### body_len
		Size of the body to send. Defaults to None (Will be calculated)
	### content_type
		The response's body content type. If body is dict then content_type will be application/json. Defaults to text/html; charset=UTF-8
	"""
	if type (body) is dict:
		body_string = json.dumps (body)
		body_len = len (body_string)
		http_response_render_json (http_receive, status_code, body_string.encode ("utf-8"), body_len)
	else: 
		real_body = body
		if type (body) is str:
			real_body = body.encode ("utf-8")
		if body_len is None:
			body_len = len (body)

		response = http_response_create (
			status_code, real_body, body_len
		)

		http_response_add_content_type_header (response, content_type)

		http_response_add_content_length_header (response, body_len)
		http_response_compile (response)
		http_response_send (response, http_receive)
		http_response_delete (response)

# files
# opens the selected file and sends it back to the client
# takes care of generating the header based on the file values
# returns 0 on success, 1 on error
http_response_send_file = lib.http_response_send_file
http_response_send_file.argtypes = [c_void_p, http_status, c_char_p]
http_response_send_file.restype = c_uint8

# render
# sends the selected text back to the user
# this methods takes care of generating a repsonse with text/html content type
# returns 0 on success, 1 on error
http_response_render_text = lib.http_response_render_text
http_response_render_text.argtypes = [c_void_p, http_status, c_char_p, c_size_t]
http_response_render_text.restype = c_uint8

# sends the selected json back to the user
# this methods takes care of generating a repsonse with application/json content type
# returns 0 on success, 1 on error
http_response_render_json = lib.http_response_render_json
http_response_render_json.argtypes = [c_void_p, http_status, c_char_p, c_size_t]
http_response_render_json.restype = c_uint8

# videos
# handles the transmission of a video to the client
# returns 0 on success, 1 on error
http_response_handle_video = lib.http_response_handle_video
http_response_handle_video.argtypes = [c_void_p, c_char_p]
http_response_handle_video.restype = c_uint8

# json
# creates a HTTP response with the defined status code
# with a custom json message body
# returns a new HTTP response instance ready to be sent
http_response_create_json = lib.http_response_create_json
http_response_create_json.argtypes = [http_status, c_char_p, c_size_t]
http_response_create_json.restype = c_void_p

# creates a HTTP response with the defined status code and a data (body)
# with a json message of type { key: value } that is ready to be sent
# returns a new HTTP response instance
http_response_create_json_key_value = lib.http_response_create_json_key_value
http_response_create_json_key_value.argtypes = [http_status, c_char_p, c_char_p]
http_response_create_json_key_value.restype = c_void_p

# creates a HTTP response with the defined status code
# with a json body of type { "key": int_value }
# returns a new HTTP response instance ready to be sent
http_response_json_int_value = lib.http_response_json_int_value
http_response_json_int_value.argtypes = [http_status, c_char_p, c_int]
http_response_json_int_value.restype = c_void_p

# sends a HTTP response with custom status code
# with a json body of type { "key": int_value }
# returns 0 on success, 1 on error
http_response_json_int_value_send = lib.http_response_json_int_value_send
http_response_json_int_value_send.argtypes = [c_void_p, http_status, c_char_p, c_int]
http_response_json_int_value_send.restype = c_uint8

# creates a HTTP response with the defined status code
# with a json body of type { "key": large_int_value }
# returns a new HTTP response instance ready to be sent
http_response_json_large_int_value = lib.http_response_json_large_int_value
http_response_json_large_int_value.argtypes = [http_status, c_char_p, c_long]
http_response_json_large_int_value.restype = c_void_p

# sends a HTTP response with custom status code
# with a json body of type { "key": large_int_value }
# returns 0 on success, 1 on error
http_response_json_large_int_value_send = lib.http_response_json_large_int_value_send
http_response_json_large_int_value_send.argtypes = [c_void_p, http_status, c_char_p, c_long]
http_response_json_large_int_value_send.restype = c_uint8

# creates a HTTP response with the defined status code
# with a json body of type { "key": double_value }
# returns a new HTTP response instance ready to be sent
http_response_json_real_value = lib.http_response_json_real_value
http_response_json_real_value.argtypes = [http_status, c_char_p, c_double]
http_response_json_real_value.restype = c_void_p

# sends a HTTP response with custom status code
# with a json body of type { "key": double_value }
# returns 0 on success, 1 on error
http_response_json_real_value_send = lib.http_response_json_real_value_send
http_response_json_real_value_send.argtypes = [c_void_p, http_status, c_char_p, c_double]
http_response_json_real_value_send.restype = c_uint8

# creates a HTTP response with the defined status code
# with a json body of type { "key": bool_value }
# returns a new HTTP response instance ready to be sent
http_response_json_bool_value = lib.http_response_json_bool_value
http_response_json_bool_value.argtypes = [http_status, c_char_p, c_bool]
http_response_json_bool_value.restype = c_void_p

# sends a HTTP response with custom status code
# with a json body of type { "key": bool_value }
# returns 0 on success, 1 on error
http_response_json_bool_value_send = lib.http_response_json_bool_value_send
http_response_json_bool_value_send.argtypes = [c_void_p, http_status, c_char_p, c_bool]
http_response_json_bool_value_send.restype = c_uint8

# creates a HTTP response with the defined status code and a data (body)
# with a json message of type { msg: "your message" } ready to be sent
# returns a new HTTP response instance
http_response_json_msg = lib.http_response_json_msg
http_response_json_msg.argtypes = [http_status, c_char_p]
http_response_json_msg.restype = c_void_p

# creates and sends a HTTP json message response
# with the defined status code & message
# returns 0 on success, 1 on error
http_response_json_msg_send = lib.http_response_json_msg_send
http_response_json_msg_send.argtypes = [c_void_p, http_status, c_char_p]
http_response_json_msg_send.restype = c_uint8

# creates a HTTP response with the defined status code and a data (body)
# with a json message of type { error: "your error message" } ready to be sent
# returns a new HTTP response instance
http_response_json_error = lib.http_response_json_error
http_response_json_error.argtypes = [http_status, c_char_p]
http_response_json_error.restype = c_void_p

# creates and sends a HTTP json error response
# with the defined status code & message
# returns 0 on success, 1 on error
http_response_json_error_send = lib.http_response_json_error_send
http_response_json_error_send.argtypes = [c_void_p, http_status, c_char_p]
http_response_json_error_send.restype = c_uint8

# creates a HTTP response with the defined status code and a data (body)
# with a json meesage of type { key: value } ready to be sent
# returns a new HTTP response instance
http_response_json_key_value = lib.http_response_json_key_value
http_response_json_key_value.argtypes = [http_status, c_char_p, c_char_p]
http_response_json_key_value.restype = c_void_p

# creates and sends a HTTP custom json response
# with the defined status code & key-value
# returns 0 on success, 1 on error
http_response_json_key_value_send = lib.http_response_json_key_value_send
http_response_json_key_value_send.argtypes = [c_void_p, http_status, c_char_p, c_char_p]
http_response_json_key_value_send.restype = c_uint8

# creates a http response with the defined status code
# and the body with the custom json
http_response_json_custom = lib.http_response_json_custom
http_response_json_custom.argtypes = [http_status, c_char_p]
http_response_json_custom.restype = c_void_p

# creates and sends a http custom json response with the defined status code
# returns 0 on success, 1 on error
http_response_json_custom_send = lib.http_response_json_custom_send
http_response_json_custom_send.argtypes = [c_void_p, http_status, c_char_p]
http_response_json_custom_send.restype = c_uint8

# creates a http response with the defined status code
# and the body with a reference to a custom json
http_response_json_custom_reference = lib.http_response_json_custom_reference
http_response_json_custom_reference.argtypes = [http_status, c_char_p, c_size_t]
http_response_json_custom_reference.restype = c_void_p

# creates and sends a http custom json reference response
# with the defined status code
# returns 0 on success, 1 on error
http_response_json_custom_reference_send = lib.http_response_json_custom_reference_send
http_response_json_custom_reference_send.argtypes = [c_void_p, http_status, c_char_p, c_size_t]
http_response_json_custom_reference_send.restype = c_uint8
