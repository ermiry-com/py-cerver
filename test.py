import os
import ctypes

import cerver

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	print ("Main handler!")
	cerver.http_response_json_msg_send (http_receive, 200, "Main handler!".encode ('utf-8'))

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def hola_handler (http_receive, request):
	print ("Hola handler!")
	cerver.http_response_json_msg_send (http_receive, 200, "Hola handler!".encode ('utf-8'))

web_cerver = cerver.cerver_create_web ("web-cerver".encode ('utf-8'), 8080, 10)

# main configuration
cerver.cerver_set_receive_buffer_size (web_cerver, 4096);
cerver.cerver_set_thpool_n_threads (web_cerver, 4);
cerver.cerver_set_handler_type (web_cerver, cerver.CERVER_HANDLER_TYPE_THREADS);

cerver.cerver_set_reusable_address_flags (web_cerver, True);

# HTTP configuration
http_cerver = cerver.http_cerver_get (web_cerver)

# GET /
main_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "/".encode ('utf-8'), main_handler)
cerver.http_cerver_route_register (http_cerver, main_route)

# GET /hola
hola_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "hola".encode ('utf-8'), hola_handler)
cerver.http_cerver_route_register (http_cerver, hola_route)

# start
cerver.cerver_start (web_cerver)