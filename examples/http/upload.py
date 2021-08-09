import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *
import cerver.utils

web_cerver = None

# end
def end (signum, frame):
	# cerver_stats_print (web_cerver, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_cerver))
	cerver_teardown (web_cerver)
	cerver_end ()
	sys.exit ("Done!")

# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	response = http_response_json_msg (
		HTTP_STATUS_OK, b"Test route works!"
	)

	http_response_print (response)
	http_response_send (response, http_receive)
	http_response_delete (response)

# POST /upload
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def upload_handler (http_receive, request):
	http_request_multi_parts_print (request)

	value = http_request_multi_parts_get_value (
		request, b"value"
	)

	if value:
		print (value.decode ('utf-8'))

	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, b"Upload works!"
	)

def iter_good_handler_send_success (http_receive):
	json = "{ \"msg\": \"Iter good route works!\" }"
	json_len = len (json)
	
	response = http_response_create (
		HTTP_STATUS_OK, json.encode ('utf-8'), json_len
	)

	if (response):
		http_response_add_content_type_header (response, HTTP_CONTENT_TYPE_JSON)
		http_response_add_content_length_header (response, json_len)

		http_response_compile (response)

		http_response_print (response)

		http_response_send (response, http_receive)
		http_response_delete (response)

def iter_good_handler_send_failure (http_receive):
	json = "{ \"error\": \"Failed to get multi-part values!\" }"
	json_len = len (json)

	response = http_response_create (
		HTTP_STATUS_BAD_REQUEST, json.encode ('utf-8'), json_len
	)

	if (response):
		http_response_add_content_type_header (response, HTTP_CONTENT_TYPE_JSON)
		http_response_add_content_length_header (response, json_len)

		http_response_compile (response)

		http_response_print (response)

		http_response_send (response, http_receive)
		http_response_delete (response)

# POST /iter/good
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def iter_good_handler (http_receive, request):
	http_request_multi_parts_print (request)

	if (http_request_multi_parts_iter_start (request)):
		mpart = http_request_multi_parts_iter_get_next (request)
		while (mpart):
			if (http_multi_part_is_file (mpart)):
				cerver.utils.printf (
					"FILE: %s - [%d] %s -> [%d] %s\n",
					http_multi_part_get_name (mpart).contents.str,
					http_multi_part_get_filename_len (mpart),
					http_multi_part_get_filename (mpart),
					http_multi_part_get_saved_filename_len (mpart),
					http_multi_part_get_saved_filename (mpart)
				)

			elif (http_multi_part_is_value (mpart)):
				cerver.utils.printf (
					"VALUE: %s - [%d] %s\n",
					http_multi_part_get_name (mpart).contents.str,
					http_multi_part_get_value_len (mpart),
					http_multi_part_get_value (mpart)
				)

			mpart = http_request_multi_parts_iter_get_next (request)

		iter_good_handler_send_success (http_receive)

	# failed to get multi-parts from request
	else:
		iter_good_handler_send_failure (http_receive)

# POST /iter/empty
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def iter_empty_handler (http_receive, request):
	http_request_multi_parts_print (request)

	if (http_request_multi_parts_iter_start (request) is False):
		http_response_json_msg_send (
			http_receive, HTTP_STATUS_OK,
			b"Iter empty route works!"
		)

	else:
		http_response_json_error_send (
			http_receive, HTTP_STATUS_BAD_REQUEST,
			b"Iter empty route bad request!"
		)

# POST /discard
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def discard_handler (http_receive, request):
	http_request_multi_parts_print (request)

	key = http_request_multi_parts_get_value (request, b"key")
	if (key == b"okay"):
		cerver.utils.cerver_log_success (
			b"Success request, keeping multi part files..."
		)

		http_response_json_msg_send (
			http_receive, HTTP_STATUS_OK, b"Success request!"
		)

	else:
		cerver.utils.cerver_log_error (b"key != okay")
		cerver.utils.cerver_log_debug (b"Discarding multi part files...")
		http_request_multi_part_discard_files (request)
		http_response_json_error_send (
			http_receive, HTTP_STATUS_BAD_REQUEST,
			b"Bad request!"
		)

def start ():
	global web_cerver
	web_cerver = cerver_create_web (
		b"web-cerver", 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (web_cerver, 4096)
	cerver_set_thpool_n_threads (web_cerver, 4)
	cerver_set_handler_type (web_cerver, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (web_cerver, True)

	# HTTP configuration
	http_cerver = http_cerver_get (web_cerver)

	files_create_dir (b"uploads", 0o777)
	http_cerver_set_uploads_path (http_cerver, b"uploads")

	http_cerver_set_default_uploads_filename_generator (http_cerver)

	# GET /test
	test_route = http_route_create (REQUEST_METHOD_GET, b"test", test_handler)
	http_cerver_route_register (http_cerver, test_route)

	# POST /upload
	upload_route = http_route_create (REQUEST_METHOD_POST, b"upload", upload_handler)
	http_route_set_modifier (upload_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, upload_route)

	# POST /iter/good
	iter_good_route = http_route_create (REQUEST_METHOD_POST, b"iter/good", iter_good_handler)
	http_route_set_modifier (iter_good_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, iter_good_route)

	# POST /iter/empty
	iter_empty_route = http_route_create (REQUEST_METHOD_POST, b"iter/empty", iter_empty_handler)
	http_route_set_modifier (iter_empty_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, iter_empty_route)

	# POST /discard
	discard_route = http_route_create (REQUEST_METHOD_POST, b"discard", discard_handler)
	http_route_set_modifier (discard_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, discard_route)

	# start
	cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
