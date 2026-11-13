"""The web server of the e2e tier, started by the tests as a subprocess.

cerver_run () runs cerver in a thread and the main thread waits for SIGINT or SIGTERM, so the
signal is handled by python and the cerver stops with cerver_shutdown () and cerver_teardown ();
the process exits 0 only when the start, the shutdown and the teardown succeeded.
"""

import sys
import threading
import time
from ctypes import c_void_p

from cerver import CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_create_web
from cerver import cerver_run
from cerver import cerver_set_handler_type
from cerver import cerver_set_reusable_address_flags
from cerver import cerver_set_thpool_n_threads
from cerver.http import HTTP_CONTENT_TYPE_TXT
from cerver.http import HTTP_HEADER_CONTENT_TYPE
from cerver.http import HTTP_MIDDLEWARE_RESULT_CONTINUE
from cerver.http import HTTP_MIDDLEWARE_RESULT_STOP
from cerver.http import HTTP_ROUTE_MODIFIER_MULTI_PART
from cerver.http import REQUEST_METHOD_QUERY
from cerver.http import HTTP_STATUS_BAD_REQUEST
from cerver.http import HTTP_STATUS_FORBIDDEN
from cerver.http import HTTP_STATUS_OK
from cerver.http import HTTP_STATUS_SEE_OTHER
from cerver.http import http_cerver_get
from cerver.http import http_cerver_set_default_uploads_filename_generator
from cerver.http import http_cerver_set_method_not_allowed
from cerver.http import http_cerver_set_not_found_handler
from cerver.http import http_cerver_set_uploads_delete_when_done
from cerver.http import http_cerver_set_uploads_path
from cerver.http import http_multi_part_get_file
from cerver.http import http_request_get_body_json
from cerver.http import http_request_get_header
from cerver.http import http_request_get_param_at_idx
from cerver.http import http_request_multi_parts_iter_get_next
from cerver.http import http_request_multi_parts_iter_start
from cerver.http import http_send_response
from cerver.http import redirect
from cerver.http import HTTP_TRUSTED_PROXIES_PRIVATE
from cerver.http import http_cerver_add_origin_to_whitelist
from cerver.http import http_cerver_set_request_id
from cerver.http import http_cerver_set_trusted_proxies
from cerver.http import http_group_set_cors
from cerver.http import http_request_get_client_ip
from cerver.http import http_request_get_id
from cerver.http import http_response_add_content_type_header
from cerver.http import http_response_get
from cerver.http import http_response_return
from cerver.http import http_response_set_status
from cerver.http import http_response_stream_begin
from cerver.http import http_response_stream_write
from cerver.http import HTTP_CLIENT_STATE_CONNECTED
from cerver.http import http_client_state_string
from cerver.http import http_receive_get_client_state
from cerver.http import http_receive_is_client_gone
from cerver.http.decorators import HttpGroup

from cerver import files_create_dir

SERVER_NAME = b"pycerver-e2e"
SERVER_THREADS = 4
SERVER_CONNECTION_QUEUE = 16

UPLOADS_PATH = b"/tmp/pycerver-e2e-uploads"
UPLOADS_MODE = 0o755

BLOCK_HEADER = "X-Block"

UNICODE_TEXT = "ñandú, añejo y café"

# a body bigger than the minimum that is compressed
ITEMS = [{"index": index, "name": "item"} for index in range (1 << 7)]

STREAM_PIECES = [b"first", b"second"]

ALLOWED_ORIGIN = b"http://allowed.com"

REDIRECT_LOCATION = "/api/e2e/next?a=1&b=<2>"

# the gone handler waits for its client to leave
GONE_WAIT_SECONDS = 4
GONE_POLL_SECONDS = 0.01

gone_lock = threading.Lock ()
gone_found = {"states": list (), "gone": list ()}

def _gone_wait (http_receive) -> int:
	"""Asks for the state of the client until it leaves or the wait ends."""
	deadline = time.monotonic () + GONE_WAIT_SECONDS

	state = http_receive_get_client_state (http_receive)
	while ((state == HTTP_CLIENT_STATE_CONNECTED) and (time.monotonic () < deadline)):
		time.sleep (GONE_POLL_SECONDS)
		state = http_receive_get_client_state (http_receive)

	return state

def _block (http_receive, request):
	"""Stops the requests that carry the block header, any other one continues."""
	result = HTTP_MIDDLEWARE_RESULT_CONTINUE

	# the custom headers are not read here: the test sends it as the Content-Type
	content_type = http_request_get_header (request, HTTP_HEADER_CONTENT_TYPE)
	if (content_type and (content_type.contents.str == BLOCK_HEADER.encode ("utf-8"))):
		http_send_response (http_receive, HTTP_STATUS_FORBIDDEN, {"error": "blocked"})
		result = HTTP_MIDDLEWARE_RESULT_STOP

	return result

def _routes (http_cerver: c_void_p):
	api = HttpGroup.create (http_cerver, "api/e2e")
	api.before (_block)

	@api.get ("json")
	def json_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, {"text": UNICODE_TEXT})

	@api.get ("text")
	def text_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, UNICODE_TEXT, content_type=HTTP_CONTENT_TYPE_TXT)

	@api.get ("empty")
	def empty_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, None, content_type=HTTP_CONTENT_TYPE_TXT)

	@api.get ("redirect")
	def redirect_handler (http_receive, request):
		redirect (http_receive, HTTP_STATUS_SEE_OTHER, REDIRECT_LOCATION)

	@api.get ("raise")
	def raise_handler (http_receive, request):
		raise RuntimeError ("the handler failed before its response")

	@api.get ("items/:id<objectid>")
	def item_handler (http_receive, request):
		item = http_request_get_param_at_idx (request, 0).contents.str.decode ("utf-8")
		http_send_response (http_receive, HTTP_STATUS_OK, {"id": item})

	@api.post ("body")
	def body_handler (http_receive, request):
		body = http_request_get_body_json (request)
		if (body is None):
			http_send_response (http_receive, HTTP_STATUS_BAD_REQUEST, {"error": "body"})

		else:
			http_send_response (http_receive, HTTP_STATUS_OK, body)

	@api.post ("upload", modifier=HTTP_ROUTE_MODIFIER_MULTI_PART)
	def upload_handler (http_receive, request):
		files = list ()
		if (http_request_multi_parts_iter_start (request)):
			mpart = http_request_multi_parts_iter_get_next (request)
			while (mpart):
				values = http_multi_part_get_file (mpart)
				if (values):
					files.append (values)

				mpart = http_request_multi_parts_iter_get_next (request)

		http_send_response (http_receive, HTTP_STATUS_OK, {"files": files})

	@api.post ("method")
	def method_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, {"method": "POST"})

	# a method that the parser accepts since llhttp, with a body
	@api.route (REQUEST_METHOD_QUERY, "query")
	def query_handler (http_receive, request):
		body = http_request_get_body_json (request)
		http_send_response (http_receive, HTTP_STATUS_OK, {"query": body})

	@api.get ("gone")
	def gone_handler (http_receive, request):
		state = _gone_wait (http_receive)

		with gone_lock:
			gone_found["states"].append (http_client_state_string (state).decode ("utf-8"))
			gone_found["gone"].append (bool (http_receive_is_client_gone (http_receive)))

		http_send_response (http_receive, HTTP_STATUS_OK, {"state": state})

	@api.get ("gone/found")
	def gone_found_handler (http_receive, request):
		with gone_lock:
			found = {"states": list (gone_found["states"]), "gone": list (gone_found["gone"])}

		http_send_response (http_receive, HTTP_STATUS_OK, found)

	_features_routes (http_cerver)

def _features_routes (http_cerver: c_void_p):
	"""The entity tags, the compression, the streams, the request id and the client's address."""
	features = HttpGroup.create (http_cerver, "api/features")
	http_group_set_cors (features.group, True)

	@features.get ("etag", etag=True)
	def etag_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, {"items": ITEMS})

	@features.get ("compressed", compression=True)
	def compressed_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, {"items": ITEMS})

	@features.get ("stream")
	def stream_handler (http_receive, request):
		response = http_response_get ()
		http_response_set_status (response, HTTP_STATUS_OK)
		http_response_add_content_type_header (response, HTTP_CONTENT_TYPE_TXT)

		if (not http_response_stream_begin (http_receive, response)):
			for piece in STREAM_PIECES:
				http_response_stream_write (http_receive, piece, len (piece))

		# the stream is ended by cerver
		http_response_return (response)

	@features.get ("client")
	def client_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, {
			"id": http_request_get_id (request).decode ("utf-8"),
			"ip": http_request_get_client_ip (request).decode ("utf-8")
		})

def main (port: int) -> int:
	files_create_dir (UPLOADS_PATH, UPLOADS_MODE)

	cerver = cerver_create_web (SERVER_NAME, port, SERVER_CONNECTION_QUEUE)
	cerver_set_handler_type (cerver, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_thpool_n_threads (cerver, SERVER_THREADS)
	cerver_set_reusable_address_flags (cerver, True)

	http_cerver = http_cerver_get (cerver)
	http_cerver_set_method_not_allowed (http_cerver, True)

	# a route that does not match is a 404, not the catch all of cerver
	http_cerver_set_not_found_handler (http_cerver)
	http_cerver_set_uploads_path (http_cerver, UPLOADS_PATH)
	http_cerver_set_default_uploads_filename_generator (http_cerver)
	http_cerver_set_uploads_delete_when_done (http_cerver, True)

	# the tests connect from 127.0.0.1, like a proxy in a private network
	http_cerver_set_request_id (http_cerver, True)
	http_cerver_set_trusted_proxies (http_cerver, HTTP_TRUSTED_PROXIES_PRIVATE)
	http_cerver_add_origin_to_whitelist (http_cerver, ALLOWED_ORIGIN)

	_routes (http_cerver)

	return cerver_run (cerver)

if __name__ == "__main__":
	sys.exit (main (int (sys.argv[1])))
