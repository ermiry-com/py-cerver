"""The routes tree: groups, subgroups, typed params, a catch all param, the answers of the
requests without a route, and the compiled tree as JSON.

	python3 examples/routing/groups.py
	curl http://localhost:8080/api/items
	curl http://localhost:8080/api/items/507f1f77bcf86cd799439011
	curl http://localhost:8080/api/items/not-an-id                 # 404, the param is not an objectid
	curl -X DELETE http://localhost:8080/api/items/archived/12     # 405 with Allow
	curl http://localhost:8080/api/files/a/b/c.txt
	curl http://localhost:8080/api/routes
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_CREATED, HTTP_STATUS_NOT_FOUND
from cerver.http import REQUEST_METHOD_GET, HTTP_TRAILING_SLASH_REDIRECT
from cerver.http import http_cerver_configuration, http_cerver_get, http_group, http_handler
from cerver.http import http_cerver_set_method_not_allowed, http_cerver_set_not_found_route
from cerver.http import http_cerver_set_trailing_slash, http_cerver_routes_json
from cerver.http import http_receive_get_cerver
from cerver.http import http_request_get_named_param_string, http_request_get_url_string
from cerver.http import http_response_json_send, http_response_json_error_send

SERVICE_NAME = "routing"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

ITEMS = {"507f1f77bcf86cd799439011": {"name": "first item"}}

def items_list (http_receive, request):
	"""GET /api/items, the endpoint of the group itself"""
	http_response_json_send (http_receive, HTTP_STATUS_OK, {"items": list (ITEMS)})

def not_found (http_receive, request):
	"""Every request that no route matched"""
	http_response_json_send (http_receive, HTTP_STATUS_NOT_FOUND, {
		"error": "Not found!", "path": http_request_get_url_string (request)
	})

def register (http_cerver: int) -> None:
	"""Registers every group of the service."""
	items = http_group (http_cerver, "api/items", REQUEST_METHOD_GET, items_list)

	@items.get ("/:id<objectid>")
	def item_get (http_receive, request):
		item = ITEMS.get (http_request_get_named_param_string (request, "id"))
		if (item):
			http_response_json_send (http_receive, HTTP_STATUS_OK, item)

		else:
			http_response_json_error_send (http_receive, HTTP_STATUS_NOT_FOUND, b"Item not found!")

	@items.post ("/")
	def item_create (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_CREATED, {"msg": "created"})

	archived = items.subgroup ("archived")

	@archived.get ("/:number<int>")
	def archived_get (http_receive, request):
		number = int (http_request_get_named_param_string (request, "number"))
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"archived": number})

	files = http_group (http_cerver, "api/files")

	@files.get ("/*path")
	def file_get (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"path": http_request_get_named_param_string (request, "path")})

	routes = http_group (http_cerver, "api/routes")

	@routes.get ("/")
	def routes_get (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, http_cerver_routes_json (http_receive_get_cerver (http_receive)))

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	http_cerver_set_method_not_allowed (http_cerver, True)
	http_cerver_set_trailing_slash (http_cerver, HTTP_TRAILING_SLASH_REDIRECT)
	http_cerver_set_not_found_route (http_cerver, http_handler (not_found))

	register (http_cerver)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
