"""The responses of a service: Python values as JSON, the builders of cerver, text, a response
with custom headers, and the errors that are created once and sent by every handler.

	python3 examples/responses/messages.py
	curl http://localhost:8080/api/values
	curl http://localhost:8080/api/message
	curl http://localhost:8080/api/text
	curl -i http://localhost:8080/api/custom
	curl http://localhost:8080/api/missing/1
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_NOT_FOUND, HTTP_STATUS_BAD_REQUEST
from cerver.http import HTTP_STATUS_INTERNAL_SERVER_ERROR, HTTP_CONTENT_TYPE_TXT, HTTP_HEADER_CACHE_CONTROL
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_response_json_send, http_response_json_msg_send, http_send_response
from cerver.http import http_response_create, http_response_add_header, http_response_add_json_headers
from cerver.http import http_response_compile, http_response_send, http_response_delete
from cerver.http import HttpPrebuiltResponses

SERVICE_NAME = "messages"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

ERROR_NOT_FOUND = "not_found"
ERROR_BAD_REQUEST = "bad_request"
ERROR_INTERNAL = "internal"

CUSTOM_BODY = b"{\"custom\": true}"

errors = HttpPrebuiltResponses ()

def register (http_cerver: int) -> None:
	api = http_group (http_cerver, "api")

	@api.get ("/values")
	def values (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"numbers": [1, 2, 3], "nested": {"ok": True}})

	@api.get ("/message")
	def message (http_receive, request):
		http_response_json_msg_send (http_receive, HTTP_STATUS_OK, b"Hello!")

	@api.get ("/text")
	def text (http_receive, request):
		http_send_response (http_receive, HTTP_STATUS_OK, "Plain text, ñ included", content_type=HTTP_CONTENT_TYPE_TXT)

	@api.get ("/custom")
	def custom (http_receive, request):
		response = http_response_create (HTTP_STATUS_OK, CUSTOM_BODY, len (CUSTOM_BODY))
		http_response_add_json_headers (response, len (CUSTOM_BODY))
		http_response_add_header (response, HTTP_HEADER_CACHE_CONTROL, b"no-store")
		http_response_compile (response)
		http_response_send (response, http_receive)
		http_response_delete (response)

	@api.get ("/missing/:id")
	def missing (http_receive, request):
		errors.send (ERROR_NOT_FOUND, http_receive)

def main () -> int:
	cerver_init ()

	errors.add (ERROR_NOT_FOUND, HTTP_STATUS_NOT_FOUND, {"error": "Not found!"})
	errors.add (ERROR_BAD_REQUEST, HTTP_STATUS_BAD_REQUEST, {"error": "Bad request!"})
	errors.add (ERROR_INTERNAL, HTTP_STATUS_INTERNAL_SERVER_ERROR, {"error": "Internal error!"})

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	register (http_cerver_get (service))

	result = cerver_run (service)

	# the responses are released after the cerver stopped
	errors.delete ()

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
