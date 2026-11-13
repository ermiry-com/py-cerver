"""A web server of the e2e tier with a public and a private static path, and a route with a big body.

The private path is authenticated with a Python handler, and every send of a response shares the
deadline of http_cerver_set_send_timeout_milliseconds ().

Usage: statics.py <port> [send timeout in milliseconds, 0 keeps the one of the cerver]
"""

import os
import sys

from cerver import CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_create_web, cerver_run, cerver_set_handler_type
from cerver import cerver_set_reusable_address_flags, cerver_set_thpool_n_threads
from cerver.callbacks import callback_wrap
from cerver.http import HTTP_CONTENT_TYPE_TXT, HTTP_HEADER_AUTHORIZATION
from cerver.http import HTTP_ROUTE_AUTH_TYPE_CUSTOM, HTTP_STATUS_OK
from cerver.http import HttpAuthenticationHandler
from cerver.http import http_cerver_get, http_cerver_set_not_found_handler, http_cerver_static_path_add
from cerver.http import http_cerver_set_send_timeout_milliseconds
from cerver.http import http_request_get_header_string, http_send_response
from cerver.http import http_static_path_set_auth, http_static_path_set_authentication_handler
from cerver.http.decorators import HttpGroup

STATICS_NAME = b"pycerver-statics"
STATICS_THREADS = 2
STATICS_CONNECTION_QUEUE = 16

STATICS_ROOT = "/tmp/pycerver-statics"
PUBLIC_PATH = os.path.join (STATICS_ROOT, "public")
PRIVATE_PATH = os.path.join (STATICS_ROOT, "private")

# the files of the static paths, by their url
PUBLIC_FILES = {"index.html": "<h1>public</h1>"}
PRIVATE_FILES = {"report.txt": "the private report"}

AUTHORIZATION = "Bearer statics-token"

AUTHENTICATED = 0
NOT_AUTHENTICATED = 1

# far bigger than the socket buffers of the loopback, a client that does not read never gets it all
BIG_BODY_SIZE = 1 << 26

def _files (path: str, files: dict) -> None:
	os.makedirs (path, exist_ok=True)
	for name, content in files.items ():
		with open (os.path.join (path, name), "w", encoding="utf-8") as file:
			file.write (content)

def _authenticate (http_receive, request) -> int:
	authorization = http_request_get_header_string (request, HTTP_HEADER_AUTHORIZATION)

	return AUTHENTICATED if (authorization == AUTHORIZATION) else NOT_AUTHENTICATED

def _routes (http_cerver) -> None:
	api = HttpGroup.create (http_cerver, "api/statics")

	@api.get ("big")
	def big_handler (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, bytes (BIG_BODY_SIZE), content_type=HTTP_CONTENT_TYPE_TXT)

def main (port: int, send_timeout: int) -> int:
	_files (PUBLIC_PATH, PUBLIC_FILES)
	_files (PRIVATE_PATH, PRIVATE_FILES)

	cerver = cerver_create_web (STATICS_NAME, port, STATICS_CONNECTION_QUEUE)
	cerver_set_handler_type (cerver, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_thpool_n_threads (cerver, STATICS_THREADS)
	cerver_set_reusable_address_flags (cerver, True)

	http_cerver = http_cerver_get (cerver)
	http_cerver_set_not_found_handler (http_cerver)

	if (send_timeout):
		http_cerver_set_send_timeout_milliseconds (http_cerver, send_timeout)

	http_cerver_static_path_add (http_cerver, PUBLIC_PATH.encode ("utf-8"))

	private_path = http_cerver_static_path_add (http_cerver, PRIVATE_PATH.encode ("utf-8"))
	http_static_path_set_auth (private_path, HTTP_ROUTE_AUTH_TYPE_CUSTOM)
	http_static_path_set_authentication_handler (private_path, callback_wrap (_authenticate, HttpAuthenticationHandler))

	_routes (http_cerver)

	return cerver_run (cerver)

if __name__ == "__main__":
	sys.exit (main (int (sys.argv[1]), int (sys.argv[2]) if (len (sys.argv) > 2) else 0))
