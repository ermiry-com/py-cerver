import os, signal, sys
import ctypes

import cerver

web_cerver = None

# end
def end (signum, frame):
	# cerver.cerver_stats_print (web_cerver, False, False)
	cerver.http_cerver_all_stats_print (cerver.http_cerver_get (web_cerver))
	cerver.cerver_teardown (web_cerver)
	cerver.cerver_end ()
	sys.exit ("Done!")

# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
	response = cerver.http_response_json_msg (
		cerver.HTTP_STATUS_OK, "Test route works!".encode ('utf-8')
	)

	cerver.http_response_print (response)
	cerver.http_response_send (response, http_receive)
	cerver.http_response_delete (response)

# POST /upload
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def upload_handler (http_receive, request):
	cerver.http_request_multi_parts_print (request)

	value = cerver.http_request_multi_parts_get_value (
		request, "value".encode ('utf-8')
	)

	if value:
		print (value.contents.str)

	cerver.http_response_json_msg_send (
		http_receive, 200, "Upload works!".encode ('utf-8')
	)

def start ():
	global web_cerver
	web_cerver = cerver.cerver_create_web (
		"web-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver.cerver_set_receive_buffer_size (web_cerver, 4096);
	cerver.cerver_set_thpool_n_threads (web_cerver, 4);
	cerver.cerver_set_handler_type (web_cerver, cerver.CERVER_HANDLER_TYPE_THREADS);

	cerver.cerver_set_reusable_address_flags (web_cerver, True);

	# HTTP configuration
	http_cerver = cerver.http_cerver_get (web_cerver)

	os.mkdir ("uploads")
	cerver.http_cerver_set_uploads_path (http_cerver, "uploads".encode ('utf-8'))

	# GET /test
	test_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "test".encode ('utf-8'), test_handler)
	cerver.http_cerver_route_register (http_cerver, test_route)

	# POST /upload
	upload_route = cerver.http_route_create (cerver.REQUEST_METHOD_POST, "upload".encode ('utf-8'), upload_handler)
	cerver.http_route_set_modifier (upload_route, cerver.HTTP_ROUTE_MODIFIER_MULTI_PART)
	cerver.http_cerver_route_register (http_cerver, upload_route)

	# start
	cerver.cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver.cerver_init ()

	cerver.cerver_version_print_full ()

	start ()
