"""The transfers of a service: a file, a streamed body, a redirect, and the bodies with an
entity tag (304 when the client has it) and with gzip when the client accepts it.

	python3 examples/responses/transfers.py
	curl http://localhost:8080/api/file
	curl -N http://localhost:8080/api/stream
	curl -i http://localhost:8080/api/old
	curl -i http://localhost:8080/api/catalog                       # ETag
	curl -i http://localhost:8080/api/catalog -H 'If-None-Match: "<etag>"'
	curl -i --compressed http://localhost:8080/api/catalog
"""

import os
import sys
import time
from pathlib import Path

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_MOVED_PERMANENTLY, HTTP_CONTENT_TYPE_TXT
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_response_send_file, http_response_json_send, redirect
from cerver.http import http_response_get, http_response_return, http_response_set_status
from cerver.http import http_response_add_content_type_header
from cerver.http import http_response_stream_begin, http_response_stream_write, http_response_stream_end

SERVICE_NAME = "transfers"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

THIS_FILE = Path (__file__).resolve ()

STREAM_PIECES = 4
STREAM_SECONDS = 0.1

# a body that is worth compressing
CATALOG = [{"index": index, "name": f"product {index}"} for index in range (1 << 8)]

def register (http_cerver: int) -> None:
	api = http_group (http_cerver, "api")

	@api.get ("/file")
	def file (http_receive, request):
		http_response_send_file (http_receive, HTTP_STATUS_OK, str (THIS_FILE).encode ("utf-8"))

	@api.get ("/stream")
	def stream (http_receive, request):
		response = http_response_get ()
		http_response_set_status (response, HTTP_STATUS_OK)
		http_response_add_content_type_header (response, HTTP_CONTENT_TYPE_TXT)

		http_response_stream_begin (http_receive, response)
		for piece in range (STREAM_PIECES):
			data = f"piece {piece}\n".encode ("utf-8")
			http_response_stream_write (http_receive, data, len (data))
			time.sleep (STREAM_SECONDS)

		http_response_stream_end (http_receive)
		http_response_return (response)

	@api.get ("/old")
	def old (http_receive, request):
		redirect (http_receive, HTTP_STATUS_MOVED_PERMANENTLY, "/api/catalog")

	@api.get ("/catalog", etag=True, compression=True)
	def catalog (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, CATALOG)

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	register (http_cerver_get (service))

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
