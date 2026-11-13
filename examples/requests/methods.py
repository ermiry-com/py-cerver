"""The methods of the parser (llhttp): QUERY, a safe search with a body, WebDAV methods registered like
any other one, the Allow of a 405, and the lenient flags of the parser, all of them disabled by
default (each one can open the cerver to request smuggling attacks).

	python3 examples/requests/methods.py
	curl -X QUERY http://localhost:8080/api/items -d '{"name": "chair"}'
	curl -X PROPFIND http://localhost:8080/api/files/report.txt
	curl -X MKCOL http://localhost:8080/api/files/archive
	curl -X DELETE http://localhost:8080/api/items                  # 405 with Allow
	curl http://localhost:8080/api/lenient
	LENIENT=version,keep_alive python3 examples/requests/methods.py   # a warning for each flag
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_CREATED, HTTP_STATUS_MULTI_STATUS
from cerver.http import REQUEST_METHOD_GET, REQUEST_METHOD_QUERY, REQUEST_METHOD_PROPFIND, REQUEST_METHOD_MKCOL
from cerver.http import HTTP_PARSER_LENIENT_ALL, HTTP_PARSER_LENIENT_NONE
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_cerver_set_method_not_allowed, http_cerver_set_parser_lenient
from cerver.http import http_parser_lenient_string, http_parser_lenient_description
from cerver.http import http_request_get_body_json, http_request_get_named_param_string
from cerver.http import http_request_method_str
from cerver.http import http_response_json_send

SERVICE_NAME = "methods"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

LENIENT = os.environ.get ("LENIENT", "")
LENIENT_SEPARATOR = ","

ITEMS = [{"name": "chair", "color": "red"}, {"name": "table", "color": "blue"}]

# every lenient flag of the parser, by its name (b"version" -> HTTP_PARSER_LENIENT_VERSION)
LENIENT_FLAGS = {
	http_parser_lenient_string (1 << bit).decode (): 1 << bit
	for bit in range (HTTP_PARSER_LENIENT_ALL.bit_length ())
}

def lenient_flags (names: str) -> int:
	"""Combines the flags of a list of names separated by commas."""
	flags = HTTP_PARSER_LENIENT_NONE
	for name in filter (None, names.split (LENIENT_SEPARATOR)):
		if (name not in LENIENT_FLAGS):
			raise ValueError (f"Unknown lenient flag {name}, the flags are {sorted (LENIENT_FLAGS)}")

		flags |= LENIENT_FLAGS[name]

	return flags

def register (http_cerver: int) -> None:
	items = http_group (http_cerver, "api/items")

	@items.route (REQUEST_METHOD_QUERY, "/")
	def items_query (http_receive, request):
		"""QUERY /api/items, the filters go in the body and the request is safe like a GET"""
		filters = http_request_get_body_json (request) or {}
		found = [item for item in ITEMS if all (item.get (key) == value for key, value in filters.items ())]
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"items": found})

	@items.get ("/")
	def items_get (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"items": ITEMS})

	files = http_group (http_cerver, "api/files")

	@files.route (REQUEST_METHOD_PROPFIND, "/:name")
	def file_properties (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_MULTI_STATUS, {
			"name": http_request_get_named_param_string (request, "name"),
			"method": http_request_method_str (REQUEST_METHOD_PROPFIND).decode ()
		})

	@files.route (REQUEST_METHOD_MKCOL, "/:name")
	def collection_create (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_CREATED, {"collection": http_request_get_named_param_string (request, "name")})

	def lenient (http_receive, request):
		"""GET /api/lenient, the flags that the parser accepts"""
		http_response_json_send (http_receive, HTTP_STATUS_OK, {
			name: {"enabled": bool (lenient_flags (LENIENT) & flag), "accepts": http_parser_lenient_description (flag).decode ()}
			for name, flag in LENIENT_FLAGS.items ()
		})

	http_group (http_cerver, "api/lenient", REQUEST_METHOD_GET, lenient)

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	http_cerver_set_method_not_allowed (http_cerver, True)
	http_cerver_set_parser_lenient (http_cerver, lenient_flags (LENIENT))

	register (http_cerver)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
