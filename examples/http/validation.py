import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *

web_service = None

none_error = http_response_json_key_value (
	HTTP_STATUS_OK, b"oki", b"doki"
)

bad_request_error = http_response_json_key_value (
	HTTP_STATUS_BAD_REQUEST, b"error", b"Bad request!"
)

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

def service_errors_send (http_receive, errors):
	json_errors = json.dumps (errors).encode ('utf-8')

	http_response_render_json (
		http_receive, HTTP_STATUS_BAD_REQUEST,
		json_errors, len (json_errors)
	)

# POST /body
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def body_handler (http_receive, request):
	errors = {}

	body_json = http_request_get_body (request)
	if (body_json is not None):
		try:
			loaded_json = json.loads (body_json.contents.str)

			name = validate_body_value (loaded_json, "name", 1, 32, errors)
			email = validate_body_value_exists (loaded_json, "email", errors)
			username = validate_body_value (loaded_json, "username", 1, 32, errors)

			if (not errors):
				http_response_send (none_error, http_receive)

			else:
				service_errors_send (http_receive, errors)

		except Exception as e:
			http_response_send (bad_request_error, http_receive)

	else:
		http_response_send (bad_request_error, http_receive)

# POST /upload
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def upload_handler (http_receive, request):
	errors = {}

	http_request_multi_parts_print (request)

	cuc = validate_mparts_exists (request, "cuc", errors)

	image = validate_mparts_file_exists (request, "image", errors)

	if (not errors):
		print ("Original: ", image["original"])
		print ("Generated: ", image["generated"])
		print ("Saved: ", image["saved"])
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /image
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def image_handler (http_receive, request):
	errors = {}

	cuc = validate_mparts_exists (request, "cuc", errors)

	image = validate_mparts_file_is_image (request, "image", errors)

	n_refris = validate_mparts_int_with_default (request, "n_refris", 0, errors)
	n_puertas = validate_mparts_int_with_default (request, "n_puertas", 0, errors)

	test = validate_mparts_bool_with_default (request, "test", False, errors)

	if (not errors):
		print ("Type: ", image["type"])
		print ("Original: ", image["original"])
		print ("Generated: ", image["generated"])
		print ("Saved: ", image["saved"])
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

def start ():
	global web_service
	web_service = cerver_create_web (
		b"web-service", 8080, 10
	)

	# main configuration
	cerver_set_alias (web_service, b"web")

	cerver_set_receive_buffer_size (web_service, 4096)
	cerver_set_thpool_n_threads (web_service, 4)
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (web_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	files_create_dir (b"uploads", 0o777)
	http_cerver_set_uploads_path (http_cerver, b"uploads")

	http_cerver_set_default_uploads_filename_generator (http_cerver)

	# POST /body
	body_route = http_route_create (REQUEST_METHOD_POST, b"body", body_handler)
	http_cerver_route_register (http_cerver, body_route)

	# POST /upload
	upload_route = http_route_create (REQUEST_METHOD_POST, b"upload", upload_handler)
	http_route_set_modifier (upload_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, upload_route)

	# POST /image
	image_route = http_route_create (REQUEST_METHOD_POST, b"image", image_handler)
	http_route_set_modifier (image_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, image_route)

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
