import ctypes
import json
import signal, sys

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
	json_errors = json.dumps (errors).encode ("utf-8")

	http_response_render_json (
		http_receive, HTTP_STATUS_BAD_REQUEST,
		json_errors, len (json_errors)
	)

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def service_catch_all_handler (http_receive, request):
	http_send_response (
		http_receive, HTTP_STATUS_NOT_FOUND, {"error": "Not found!"}
	)

# POST /body/exists
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def body_exists_handler (http_receive, request):
	errors = {}

	body_json = http_request_get_body (request)
	if (body_json):
		try:
			loaded_json = json.loads (body_json.contents.str)

			value = validate_body_value_exists (
				loaded_json, "value", errors
			)

			if (not errors):
				http_response_send (none_error, http_receive)

			else:
				service_errors_send (http_receive, errors)

		except Exception as e:
			print (e)
			http_response_send (bad_request_error, http_receive)

	else:
		http_response_send (bad_request_error, http_receive)

# POST /body/exists/ignore
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def body_exists_ignore_handler (http_receive, request):
	errors = {}

	body_json = http_request_get_body (request)
	if (body_json):
		try:
			loaded_json = json.loads (body_json.contents.str)

			value = validate_body_string_value_exists_ignore_size (
				loaded_json, "value", errors
			)

			if (not errors):
				http_response_send (none_error, http_receive)

			else:
				service_errors_send (http_receive, errors)

		except Exception as e:
			print (e)
			http_response_send (bad_request_error, http_receive)

	else:
		http_response_send (bad_request_error, http_receive)

# POST /body/exists/int
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def body_exists_int_handler (http_receive, request):
	errors = {}

	body_json = http_request_get_body (request)
	if (body_json):
		try:
			loaded_json = json.loads (body_json.contents.str)

			value = validate_body_int_value_exists (
				loaded_json, "value", errors
			)

			if (not errors):
				http_response_send (none_error, http_receive)

			else:
				service_errors_send (http_receive, errors)

		except Exception as e:
			print (e)
			http_response_send (bad_request_error, http_receive)

	else:
		http_response_send (bad_request_error, http_receive)

# POST /body/exists/float
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def body_exists_float_handler (http_receive, request):
	errors = {}

	body_json = http_request_get_body (request)
	if (body_json):
		try:
			loaded_json = json.loads (body_json.contents.str)

			value = validate_body_float_value_exists (
				loaded_json, "value", errors
			)

			if (not errors):
				http_response_send (none_error, http_receive)

			else:
				service_errors_send (http_receive, errors)

		except Exception as e:
			print (e)
			http_response_send (bad_request_error, http_receive)

	else:
		http_response_send (bad_request_error, http_receive)

# POST /body/value
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def body_value_handler (http_receive, request):
	errors = {}

	body_json = http_request_get_body (request)
	if (body_json):
		try:
			loaded_json = json.loads (body_json.contents.str)

			value = validate_body_value (
				loaded_json, "value", 8, 32, errors
			)

			if (not errors):
				http_response_send (none_error, http_receive)

			else:
				service_errors_send (http_receive, errors)

		except Exception as e:
			print (e)
			http_response_send (bad_request_error, http_receive)

	else:
		http_response_send (bad_request_error, http_receive)

# POST /mparts/exists
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_exists_handler (http_receive, request):
	errors = {}

	value = validate_mparts_exists (request, "value", errors)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/value
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_value_handler (http_receive, request):
	errors = {}

	value = validate_mparts_value (request, "value", 8, 32, errors)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/int
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_int_handler (http_receive, request):
	errors = {}

	value = validate_mparts_int (request, "value", errors)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/int/default
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_int_default_handler (http_receive, request):
	errors = {}

	value = validate_mparts_int_with_default (
		request, "value", 10, errors
	)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/float
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_float_handler (http_receive, request):
	errors = {}

	value = validate_mparts_float (request, "value", errors)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/float/default
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_float_default_handler (http_receive, request):
	errors = {}

	value = validate_mparts_float_with_default (
		request, "value", 10.6, errors
	)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/bool
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_bool_handler (http_receive, request):
	errors = {}

	value = validate_mparts_bool (request, "value", errors)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/bool/default
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_bool_default_handler (http_receive, request):
	errors = {}

	value = validate_mparts_bool_with_default (
		request, "value", False, errors
	)

	if (not errors):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/upload
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_upload_handler (http_receive, request):
	errors = {}

	# http_request_multi_parts_print (request)

	cuc = validate_mparts_exists (request, "cuc", errors)
	image = validate_mparts_file_exists (request, "image", errors)

	if (not errors):
		print ("Original: ", image["original"])
		print ("Generated: ", image["generated"])
		print ("Saved: ", image["saved"])
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/filenames
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_filenames_handler (http_receive, request):
	errors = {}

	filename = validate_mparts_filename_exists (request, "image", errors)
	saved_filename = validate_mparts_saved_filename_exists (request, "image", errors)

	if (not errors):
		print ("filename: ", filename)
		print ("saved: ", saved_filename)
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/saved
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_saved_handler (http_receive, request):
	errors = {}

	# http_request_multi_parts_print (request)

	cuc = validate_mparts_exists (request, "cuc", errors)
	if (validate_mparts_saved_file_exists (request, "image", errors)):
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/complete
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_complete_handler (http_receive, request):
	errors = {}

	http_request_multi_parts_print (request)

	cuc = validate_mparts_exists (request, "cuc", errors)

	complete = validate_mparts_file_complete (request, "image", errors)

	if (not errors):
		print ("Original: ", complete["original"])
		print ("Generated: ", complete["generated"])
		print ("Saved: ", complete["saved"])
		http_response_send (none_error, http_receive)

	else:
		service_errors_send (http_receive, errors)

# POST /mparts/image
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def mparts_image_handler (http_receive, request):
	errors = {}

	http_request_multi_parts_print (request)

	cuc = validate_mparts_exists (request, "cuc", errors)

	image = validate_mparts_file_is_image (request, "image", errors)

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

	# POST /body/exists
	exists_route = http_route_create (REQUEST_METHOD_POST, b"body/exists", body_exists_handler)
	http_cerver_route_register (http_cerver, exists_route)

	# POST /body/exists/ignore
	exists_ignore_route = http_route_create (REQUEST_METHOD_POST, b"body/exists/ignore", body_exists_ignore_handler)
	http_cerver_route_register (http_cerver, exists_ignore_route)

	# POST /body/exists/int
	exists_int_route = http_route_create (REQUEST_METHOD_POST, b"body/exists/int", body_exists_int_handler)
	http_cerver_route_register (http_cerver, exists_int_route)

	# POST /body/exists/float
	exists_float_route = http_route_create (REQUEST_METHOD_POST, b"body/exists/float", body_exists_float_handler)
	http_cerver_route_register (http_cerver, exists_float_route)

	# POST /body/value
	value_route = http_route_create (REQUEST_METHOD_POST, b"body/value", body_value_handler)
	http_cerver_route_register (http_cerver, value_route)

	# POST /mparts/exists
	mparts_exists_route = http_route_create (REQUEST_METHOD_POST, b"mparts/exists", mparts_exists_handler)
	http_route_set_modifier (mparts_exists_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_exists_route)

	# POST /mparts/value
	mparts_value_route = http_route_create (REQUEST_METHOD_POST, b"mparts/value", mparts_value_handler)
	http_route_set_modifier (mparts_value_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_value_route)

	# POST /mparts/int
	mparts_int_route = http_route_create (REQUEST_METHOD_POST, b"mparts/int", mparts_int_handler)
	http_route_set_modifier (mparts_int_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_int_route)

	# POST /mparts/int/default
	mparts_int_default_route = http_route_create (REQUEST_METHOD_POST, b"mparts/int/default", mparts_int_default_handler)
	http_route_set_modifier (mparts_int_default_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_int_default_route)

	# POST /mparts/float
	mparts_float_route = http_route_create (REQUEST_METHOD_POST, b"mparts/float", mparts_float_handler)
	http_route_set_modifier (mparts_float_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_float_route)

	# POST /mparts/float/default
	mparts_float_default_route = http_route_create (REQUEST_METHOD_POST, b"mparts/float/default", mparts_float_default_handler)
	http_route_set_modifier (mparts_float_default_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_float_default_route)

	# POST /mparts/bool
	mparts_bool_route = http_route_create (REQUEST_METHOD_POST, b"mparts/bool", mparts_bool_handler)
	http_route_set_modifier (mparts_bool_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_bool_route)

	# POST /mparts/bool/default
	mparts_bool_default_route = http_route_create (REQUEST_METHOD_POST, b"mparts/bool/default", mparts_bool_default_handler)
	http_route_set_modifier (mparts_bool_default_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_bool_default_route)

	# POST /mparts/upload
	mparts_upload_route = http_route_create (REQUEST_METHOD_POST, b"mparts/upload", mparts_upload_handler)
	http_route_set_modifier (mparts_upload_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_upload_route)

	# POST /mparts/filenames
	mparts_filenames_route = http_route_create (REQUEST_METHOD_POST, b"mparts/filenames", mparts_filenames_handler)
	http_route_set_modifier (mparts_filenames_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_filenames_route)

	# POST /mparts/saved
	mparts_saved_route = http_route_create (REQUEST_METHOD_POST, b"mparts/saved", mparts_saved_handler)
	http_route_set_modifier (mparts_saved_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_saved_route)

	# POST /mparts/complete
	mparts_complete_route = http_route_create (REQUEST_METHOD_POST, b"mparts/complete", mparts_complete_handler)
	http_route_set_modifier (mparts_complete_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_complete_route)

	# POST /mparts/image
	mparts_image_route = http_route_create (REQUEST_METHOD_POST, b"mparts/image", mparts_image_handler)
	http_route_set_modifier (mparts_image_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, mparts_image_route)

	# add a catch all route
	http_cerver_set_catch_all_route (http_cerver, service_catch_all_handler)

	# start
	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	start ()
