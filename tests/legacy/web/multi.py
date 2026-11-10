import os, signal, sys
import ctypes

from datetime import datetime

from cerver import *
from cerver.http import *
import cerver.utils

web_service = None

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

# POST /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	result = False
	not_empty = True

	http_request_multi_parts_print (request)

	if (http_request_multi_parts_iter_start (request)):
		mpart = http_request_multi_parts_iter_get_next (request)
		while (mpart):
			if (http_multi_part_is_not_empty (mpart)):
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

			else:
				cerver.utils.cerver_log_error (b"mpart is empty!")
				not_empty = False

			mpart = http_request_multi_parts_iter_get_next (request)

		result = True

	if (result and not_empty):
		http_response_json_key_value_send (
			http_receive, HTTP_STATUS_OK, b"oki", b"doki"
		)

	else:
		http_response_json_bool_value_send (
			http_receive, HTTP_STATUS_BAD_REQUEST, b"result", False
		)

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def custom_uploads_filename_generator (
	http_receive, request
):
	mpart = http_request_get_current_mpart (request)

	now = datetime.now ()
	timestamp = datetime.timestamp (now)
	timestamp = int (timestamp * 1000)

	http_multi_part_set_generated_filename (
		mpart,
		b"%d-%ld-%s",
		http_receive_get_sock_fd (http_receive),
		timestamp,
		http_multi_part_get_filename (mpart)
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

	files_create_dir (b"uploads", 0o777)
	http_cerver_set_uploads_path (http_cerver, b"uploads")

	http_cerver_set_default_uploads_filename_generator (http_cerver)
	http_cerver_set_default_uploads_dirname_generator (http_cerver)

	# POST /test
	test_route = http_route_create (REQUEST_METHOD_POST, b"test", test_handler)
	http_route_set_modifier (test_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, test_route)

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
