from ctypes import c_char_p, c_uint8, c_void_p, c_uint, c_size_t

from .lib import lib

from .content import ContentType
from .headers import HttpHeader
from .status import http_status

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

# render
# opens the selected file and sends it back to the user
# this method takes care of generating the header based on the file values
# returns 0 on success, 1 on error
http_response_render_file = lib.http_response_render_file
http_response_render_file.argtypes = [c_void_p, c_char_p]
http_response_render_file.restype = c_uint8

# json
http_response_json_msg_send = lib.http_response_json_msg_send
http_response_json_msg_send.argtypes = [c_void_p, c_uint, c_char_p]
http_response_json_msg_send.restype = c_uint8
