"""The values of a request: its query, its JSON body, its headers, and the typed validators
that answer 400 with every error at once.

	python3 examples/requests/values.py
	curl "http://localhost:8080/api/search?text=chair&page=2&sort=name&tags=a,b"
	curl "http://localhost:8080/api/search?page=0&sort=other"                      # 400 with the errors
	curl -X POST http://localhost:8080/api/orders -d '{"product": "chair", "quantity": 2, "date": "2026-11-09"}'
	curl http://localhost:8080/api/headers -H "User-Agent: example"
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_CREATED, HTTP_STATUS_BAD_REQUEST, HTTP_HEADER_USER_AGENT
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_request_get_query_params, http_request_get_body_json
from cerver.http import http_request_get_header_string, http_request_get_custom_header_string
from cerver.http import http_request_get_client_ip_string
from cerver.http import validate_query_string, validate_query_int, validate_query_choice, validate_query_list
from cerver.http import validate_body_string, validate_body_int, validate_body_date, validate_body_bool
from cerver.http import http_response_json_send

SERVICE_NAME = "values"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

SORTS = ("name", "date")

PAGE_MINIMUM = 1
PAGE_DEFAULT = 1
QUANTITY_MINIMUM = 1
QUANTITY_MAXIMUM = 100
PRODUCT_MAXIMUM = 64

def answer (http_receive, errors: dict, status: int, body: dict) -> None:
	"""Answers the errors of the request with 400, or the body."""
	if (errors):
		http_response_json_send (http_receive, HTTP_STATUS_BAD_REQUEST, {"errors": errors})

	else:
		http_response_json_send (http_receive, status, body)

def register (http_cerver: int) -> None:
	api = http_group (http_cerver, "api")

	@api.get ("/search")
	def search (http_receive, request):
		errors = {}
		query = http_request_get_query_params (request)

		values = {
			"text": validate_query_string (query, "text", errors, required=False),
			"page": validate_query_int (query, "page", errors, required=False, default=PAGE_DEFAULT, minimum=PAGE_MINIMUM),
			"sort": validate_query_choice (query, "sort", errors, SORTS, required=False, default=SORTS[0]),
			"tags": validate_query_list (query, "tags", errors, required=False, default=[])
		}

		answer (http_receive, errors, HTTP_STATUS_OK, values)

	@api.post ("/orders")
	def order_create (http_receive, request):
		errors = {}
		body = http_request_get_body_json (request) or {}

		order = {
			"product": validate_body_string (body, "product", errors, max_len=PRODUCT_MAXIMUM),
			"quantity": validate_body_int (body, "quantity", errors, minimum=QUANTITY_MINIMUM, maximum=QUANTITY_MAXIMUM),
			"date": validate_body_date (body, "date", errors),
			"gift": validate_body_bool (body, "gift", errors, required=False, default=False)
		}

		if (not errors):
			order["date"] = order["date"].isoformat ()

		answer (http_receive, errors, HTTP_STATUS_CREATED, order)

	@api.get ("/headers")
	def headers (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {
			"user_agent": http_request_get_header_string (request, HTTP_HEADER_USER_AGENT),
			"custom": http_request_get_custom_header_string (request, "X-Custom"),
			"client": http_request_get_client_ip_string (request)
		})

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	register (http_cerver_get (service))

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
