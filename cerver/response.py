from ctypes import c_char_p, c_uint8, c_void_p, c_uint, c_size_t

import json

from .lib import lib

from .content import ContentType, HTTP_CONTENT_TYPE_HTML
from .headers import HttpHeader
from .status import http_status

http_response_delete = lib.http_response_delete
http_response_delete.argtypes = [c_void_p]

# get a new HTTP response ready to be used
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

# adds a new header to the response, the headers will be handled when calling 
# http_response_compile () to generate a continuos header buffer
# returns 0 on success, 1 on error
http_response_add_header = lib.http_response_add_header
http_response_add_header.argtypes = [c_void_p, HttpHeader, c_char_p]
http_response_add_header.restype = c_uint8

# adds a HTTP_HEADER_CONTENT_TYPE header to the response
# returns 0 on success, 1 on error
http_response_add_content_type_header = lib.http_response_add_content_type_header
http_response_add_content_type_header.argtypes = [c_void_p, ContentType]
http_response_add_content_type_header.restype = c_uint8

# adds a HTTP_HEADER_CONTENT_LENGTH header to the response
# returns 0 on success, 1 on error
http_response_add_content_length_header = lib.http_response_add_content_length_header
http_response_add_content_length_header.argtypes = [c_void_p, c_size_t]
http_response_add_content_length_header.restype = c_uint8

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
http_response_create.argtypes = [c_uint, c_void_p, c_size_t]
http_response_create.restype = c_void_p

# merge the response header and the data into the final response
# returns 0 on success, 1 on error
http_response_compile = lib.http_response_compile
http_response_compile.argtypes = [c_void_p]
http_response_compile.restype = c_uint8

http_response_print = lib.http_response_print
http_response_print.argtypes = [c_void_p]

# send
# sends a response to the connection's socket
# returns 0 on success, 1 on error
http_response_send = lib.http_response_send
http_response_send.argtypes = [c_void_p, c_void_p]
http_response_send.restype = c_uint8

# expects a response with an already created header and data
# as this method will send both parts withput the need of a continuos response buffer
# use this for maximun efficiency
# returns 0 on success, 1 on error
http_response_send_split = lib.http_response_send_split
http_response_send_split.argtypes = [c_void_p, c_void_p]
http_response_send_split.restype = c_uint8

# creates & sends a response to the connection's socket
# returns 0 on success, 1 on error
http_response_create_and_send = lib.http_response_create_and_send
http_response_create_and_send.argtypes = [c_uint, c_void_p, c_size_t, c_void_p]
http_response_create_and_send.restype = c_uint8

# render
# sends the selected text back to the user
# this methods takes care of generating a repsonse with text/html content type
# returns 0 on success, 1 on error
http_response_render_text = lib.http_response_render_text
http_response_render_text.argtypes = [c_void_p, c_char_p, c_size_t]
http_response_render_text.restype = c_uint8

# sends the selected json back to the user
# this methods takes care of generating a repsonse with application/json content type
# returns 0 on success, 1 on error
http_response_render_json = lib.http_response_render_json
http_response_render_json.argtypes = [c_void_p, c_char_p, c_size_t]
http_response_render_json.restype = c_uint8

# opens the selected file and sends it back to the user
# this method takes care of generating the header based on the file values
# returns 0 on success, 1 on error
http_response_render_file = lib.http_response_render_file
http_response_render_file.argtypes = [c_void_p, c_char_p]
http_response_render_file.restype = c_uint8

# json
http_response_create_json = lib.http_response_create_json
http_response_create_json.argtypes = [http_status, c_char_p, c_size_t]
http_response_create_json.restype = c_void_p

http_response_create_json_key_value = lib.http_response_create_json_key_value
http_response_create_json_key_value.argtypes = [http_status, c_char_p, c_char_p]
http_response_create_json_key_value.restype = c_void_p

http_response_json_msg = lib.http_response_json_msg
http_response_json_msg.argtypes = [http_status, c_char_p]
http_response_json_msg.restype = c_void_p

http_response_json_msg_send = lib.http_response_json_msg_send
http_response_json_msg_send.argtypes = [c_void_p, c_uint, c_char_p]
http_response_json_msg_send.restype = c_uint8

http_response_json_error = lib.http_response_json_error
http_response_json_error.argtypes = [http_status, c_char_p]
http_response_json_error.restype = c_void_p

http_response_json_error_send = lib.http_response_json_error_send
http_response_json_error_send.argtypes = [c_void_p, c_uint, c_char_p]
http_response_json_error_send.restype = c_uint8

http_response_json_key_value = lib.http_response_json_key_value
http_response_json_key_value.argtypes = [http_status, c_char_p, c_char_p]
http_response_json_key_value.restype = c_void_p

http_response_json_key_value_send = lib.http_response_json_key_value_send
http_response_json_key_value_send.argtypes = [c_void_p, c_uint, c_char_p, c_char_p]
http_response_json_key_value_send.restype = c_uint8

def http_send_response (
	http_receive, status_code,
	body, body_len = None,
	content_type = HTTP_CONTENT_TYPE_HTML
):
	"""
	Function to create and send a http_response
	# Parameters
	------------
	### http_receive : HttpReceive
		The receive structure associated with the current request
	### status_code : int, optional
		http status code. Defaults to 200.
	### body: dict, str, bytes
		Value(s) to send
	### body_len
		Size of the body to send. Defaults to None (Will be calculated)
	### content_type
		Content type of the body. If body is dict then content_type will be application/json. Defaults to text/html; charset=UTF-8
	"""
	if type (body) is dict:
		body_string = json.dumps (body)
		body_len = len (body_string)
		http_response_render_json (http_receive, body_string.encode ("utf-8"), body_len)
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