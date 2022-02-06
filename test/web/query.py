import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *
from cerver.utils import cerver_log_success, cerver_log_error

web_service = None

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

# GET /query
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def query_handler (http_receive, request):
	http_response_json_bool_value_send (
		http_receive, HTTP_STATUS_OK, b"result", True
	)

# GET /query/value
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def value_handler (http_receive, request):
	query_params = http_request_get_query_params (request)
	query_value = http_request_get_query_value (query_params, "value")

	if (query_value):
		cerver_log_success (b"Got query value!")

		print (query_value)

		http_response_json_bool_value_send (
			http_receive, HTTP_STATUS_OK, b"result", True
		)

	else:
		cerver_log_error (b"Failed to get query value!")

		http_response_json_bool_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST, b"result", False
		)

# GET /query/int
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def int_handler (http_receive, request):
	result = False

	query_params = http_request_get_query_params (request)

	try:
		query_value = http_request_get_int_query_value (query_params, "value")

		if (query_value):
			if (type (query_value) == int):
				cerver_log_success (b"Got int query value!")

				print (query_value)

				http_response_json_bool_value_send (
					http_receive, HTTP_STATUS_OK, b"result", True
				)

				result = True

	except Exception as e:
		print (e)

	if (not result):
		cerver_log_error (b"Failed to get int query value!")

		http_response_json_bool_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST, b"result", False
		)

# GET /query/float
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def float_handler (http_receive, request):
	result = False

	query_params = http_request_get_query_params (request)

	try:
		query_value = http_request_get_float_query_value (query_params, "value")

		if (query_value):
			if (type (query_value) == float):
				cerver_log_success (b"Got float query value!")

				print (query_value)

				http_response_json_bool_value_send (
					http_receive, HTTP_STATUS_OK, b"result", True
				)

				result = True
	
	except Exception as e:
		print (e)

	if (not result):
		cerver_log_error (b"Failed to get float query value!")

		http_response_json_bool_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST, b"result", False
		)

# GET /query/bool
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def bool_handler (http_receive, request):
	result = False

	query_params = http_request_get_query_params (request)

	try:
		query_value = http_request_get_bool_query_value (query_params, "value")

		if (query_value):
			if (type (query_value) == bool):
				cerver_log_success (b"Got bool query value!")

				print (query_value)

				http_response_json_bool_value_send (
					http_receive, HTTP_STATUS_OK, b"result", True
				)

				result = True

	except Exception as e:
		print (e)

	if (not result):
		cerver_log_error (b"Failed to get bool query value!")

		http_response_json_bool_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST, b"result", False
		)

def start ():
	global web_service
	web_service = cerver_create_web (
		b"web-service", 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (web_service, 4096)
	cerver_set_thpool_n_threads (web_service, 4)
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (web_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	# GET /query
	query_route = http_route_create (REQUEST_METHOD_GET, b"query", query_handler)
	http_cerver_route_register (http_cerver, query_route)

	# GET /query/value
	value_route = http_route_create (REQUEST_METHOD_GET, b"value", value_handler)
	http_route_child_add (query_route, value_route)

	# GET /query/int
	int_route = http_route_create (REQUEST_METHOD_GET, b"int", int_handler)
	http_route_child_add (query_route, int_route)

	# GET /query/float
	float_route = http_route_create (REQUEST_METHOD_GET, b"float", float_handler)
	http_route_child_add (query_route, float_route)

	# GET /query/bool
	bool_route = http_route_create (REQUEST_METHOD_GET, b"bool", bool_handler)
	http_route_child_add (query_route, bool_route)

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
