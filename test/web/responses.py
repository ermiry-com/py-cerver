import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *
from cerver.utils import *

web_service = None

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

# GET /json
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_fetch_handler (http_receive, request):
	json =  b"{\"msg\": \"okay\"}"
	json_len = len (json)

	http_response_render_json (
		http_receive, HTTP_STATUS_OK,
		json, json_len
	)

# POST /json
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_upload_handler (http_receive, request):
	try:
		body = http_request_get_body_json (request)
		if (body):
			cerver_log_success (b"JSON is valid!")
			http_response_json_key_value_send (
				http_receive, HTTP_STATUS_OK,
				b"oki", b"doki"
			)
	except Exception as e:
		print (e)
		cerver_log_error (b"JSON is invalid!")
		http_response_json_key_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST,
			b"bad", b"request"
		)

# POST /json/big
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_upload_big_handler (http_receive, request):
	try:
		body = http_request_get_body_json (request)
		if (body):
			cerver_log_success (b"Big JSON is valid!")
			http_response_json_key_value_send (
				http_receive, HTTP_STATUS_OK,
				b"oki", b"doki"
			)
	except:
		cerver_log_error (b"Big JSON is invalid!")
		http_response_json_key_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST,
			b"bad", b"request"
		)

# GET /json/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_create_handler (http_receive, request):
	json_res = b"{\"msg\": \"okay\"}"
	json_len = len (json_res)

	response = http_response_create_json (
		HTTP_STATUS_OK, json_res, json_len
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/int
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_int_handler (http_receive, request):
	value = 18
	http_response_json_int_value_send (
		http_receive, HTTP_STATUS_OK,
		b"integer", value
	)

# GET /json/int/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_int_create_handler (http_receive, request):
	value = 18
	response = http_response_json_int_value (
		HTTP_STATUS_OK, b"integer", value
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/large
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_large_handler (http_receive, request):
	value = 1800000
	http_response_json_large_int_value_send (
		http_receive, HTTP_STATUS_OK,
		b"large", value
	)

# GET /json/large/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_large_create_handler (http_receive, request):
	value = 1800000
	response = http_response_json_large_int_value (
		HTTP_STATUS_OK, b"large", value
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/real
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_real_handler (http_receive, request):
	value = 18.123
	http_response_json_real_value_send (
		http_receive, HTTP_STATUS_OK,
		b"real", value
	)

# GET /json/real/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_real_create_handler (http_receive, request):
	value = 18.123
	response = http_response_json_real_value (
		HTTP_STATUS_OK, b"real", value
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/bool
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_bool_handler (http_receive, request):
	value = True
	http_response_json_bool_value_send (
		http_receive, HTTP_STATUS_OK,
		b"bool", value
	)

# GET /json/bool/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def json_bool_create_handler (http_receive, request):
	value = True
	response = http_response_json_bool_value (
		HTTP_STATUS_OK, b"bool", value
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/msg
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def msg_handler (http_receive, request):
	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, b"oki"
	)

# GET /json/msg/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def msg_create_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"oki"
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/error
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def error_handler (http_receive, request):
	http_response_json_error_send (
		http_receive, HTTP_STATUS_BAD_REQUEST, b"bad"
	)

# GET /json/error/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def error_create_handler (http_receive, request):
	response = http_response_json_error (
		HTTP_STATUS_BAD_REQUEST, b"bad"
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/key
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def key_handler (http_receive, request):
	http_response_json_key_value_send (
		http_receive,
		HTTP_STATUS_OK, b"key", b"value"
	)

# GET /json/custom
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def custom_handler (http_receive, request):
	http_response_json_custom_send (
		http_receive,
		HTTP_STATUS_OK, b"{\"oki\": \"doki\"}"
	)

# GET /json/custom/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def custom_create_handler (http_receive, request):
	response = http_response_json_custom (
		HTTP_STATUS_OK, b"{\"oki\": \"doki\"}"
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

# GET /json/reference
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def reference_handler (http_receive, request):
	response = b"{\"oki\": \"doki\"}"
	http_response_json_custom_reference_send (
		http_receive,
		HTTP_STATUS_OK, response, len (response)
	)

# GET /json/reference/create
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def reference_create_handler (http_receive, request):
	json_res = b"{\"oki\": \"doki\"}"
	response = http_response_json_custom_reference (
		HTTP_STATUS_OK, json_res, len (json_res)
	)

	if (response):
		http_response_send (response, http_receive)
		http_response_delete (response)

def start ():
	global web_service
	web_service = cerver_create_web (
		b"json-cerver", 8080, 10
	)

	# main configuration
	cerver_set_alias (web_service, b"json")

	cerver_set_receive_buffer_size (web_service, 4096)
	cerver_set_thpool_n_threads (web_service, 4)
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (web_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	# GET /json
	json_route = http_route_create (REQUEST_METHOD_GET, b"json", json_fetch_handler)
	http_cerver_route_register (http_cerver, json_route)

	# POST /json
	http_route_set_handler (json_route, REQUEST_METHOD_POST, json_upload_handler)

	# POST /json/big
	json_big_route = http_route_create (REQUEST_METHOD_POST, b"big", json_upload_big_handler)
	http_route_child_add (json_route, json_big_route)

	# GET /json/create
	create_route = http_route_create (REQUEST_METHOD_GET, b"create", json_create_handler)
	http_route_child_add (json_route, create_route)

	# GET /json/int
	int_route = http_route_create (REQUEST_METHOD_GET, b"int", json_int_handler)
	http_route_child_add (json_route, int_route)

	# GET /json/int/create
	int_create_route = http_route_create (REQUEST_METHOD_GET, b"int/create", json_int_create_handler)
	http_route_child_add (json_route, int_create_route)

	# GET /json/large
	large_route = http_route_create (REQUEST_METHOD_GET, b"large", json_large_handler)
	http_route_child_add (json_route, large_route)

	# GET /json/large/create
	large_create_route = http_route_create (REQUEST_METHOD_GET, b"large/create", json_large_create_handler)
	http_route_child_add (json_route, large_create_route)

	# GET /json/real
	real_route = http_route_create (REQUEST_METHOD_GET, b"real", json_real_handler)
	http_route_child_add (json_route, real_route)

	# GET /json/real/create
	real_create_route = http_route_create (REQUEST_METHOD_GET, b"real/create", json_real_create_handler)
	http_route_child_add (json_route, real_create_route)

	# GET /json/bool
	bool_route = http_route_create (REQUEST_METHOD_GET, b"bool", json_bool_handler)
	http_route_child_add (json_route, bool_route)

	# GET /json/bool/create
	bool_create_route = http_route_create (REQUEST_METHOD_GET, b"bool/create", json_bool_create_handler)
	http_route_child_add (json_route, bool_create_route)

	# GET /json/msg
	msg_route = http_route_create (REQUEST_METHOD_GET, b"msg", msg_handler)
	http_route_child_add (json_route, msg_route)

	# GET /json/msg/create
	msg_create_route = http_route_create (REQUEST_METHOD_GET, b"msg/create", msg_create_handler)
	http_route_child_add (json_route, msg_create_route)

	# GET /json/error
	error_route = http_route_create (REQUEST_METHOD_GET, b"error", error_handler)
	http_route_child_add (json_route, error_route)

	# GET /json/error/create
	error_create_route = http_route_create (REQUEST_METHOD_GET, b"error/create", error_create_handler)
	http_route_child_add (json_route, error_create_route)

	# GET /json/key
	key_route = http_route_create (REQUEST_METHOD_GET, b"key", key_handler)
	http_route_child_add (json_route, key_route)

	# GET /json/custom
	custom_route = http_route_create (REQUEST_METHOD_GET, b"custom", custom_handler)
	http_route_child_add (json_route, custom_route)

	# GET /json/custom/create
	custom_create_route = http_route_create (REQUEST_METHOD_GET, b"custom/create", custom_create_handler)
	http_route_child_add (json_route, custom_create_route)

	# GET /json/reference
	reference_route = http_route_create (REQUEST_METHOD_GET, b"reference", reference_handler)
	http_route_child_add (json_route, reference_route)

	# GET /json/reference/create
	reference_create_route = http_route_create (REQUEST_METHOD_GET, b"reference/create", reference_create_handler)
	http_route_child_add (json_route, reference_create_route)

	# start
	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
