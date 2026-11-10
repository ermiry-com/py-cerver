"""Middlewares: one for every endpoint of the cerver, one of a group that can stop a request,
one of a single endpoint, and the CORS headers of the origins of a whitelist.

	python3 examples/middleware/chain.py
	curl -i http://localhost:8080/api/orders -H "Origin: https://app.example.com"
	curl -i http://localhost:8080/api/orders -H "X-Maintenance: on"    # 503 from the middleware
"""

import os
import sys
import time

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_SERVICE_UNAVAILABLE
from cerver.http import HTTP_MIDDLEWARE_RESULT_CONTINUE, HTTP_MIDDLEWARE_RESULT_STOP
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_cerver_add_before, http_cerver_add_after, http_cerver_add_origin_to_whitelist
from cerver.http import http_before_middleware, http_after_middleware
from cerver.http import http_request_get_custom_header_string, http_request_get_url_string
from cerver.http import http_response_json_send, http_response_json_error_send
from cerver.utils import cerver_log_debug

SERVICE_NAME = "middleware"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

ALLOWED_ORIGINS = ("https://app.example.com",)

MAINTENANCE_HEADER = "X-Maintenance"

started = {}

def timer_start (http_receive, request) -> int:
	"""Before every endpoint: the time when the request started."""
	started[request] = time.monotonic ()
	return HTTP_MIDDLEWARE_RESULT_CONTINUE

def timer_end (http_receive, request) -> None:
	"""After every endpoint: logs how long the request took."""
	elapsed = time.monotonic () - started.pop (request, time.monotonic ())
	cerver_log_debug (f"{http_request_get_url_string (request)} took {elapsed:.6f} s")

def maintenance (http_receive, request) -> int:
	"""Before the endpoints of the group: a request in maintenance is answered here."""
	result = HTTP_MIDDLEWARE_RESULT_CONTINUE

	if (http_request_get_custom_header_string (request, MAINTENANCE_HEADER)):
		http_response_json_error_send (http_receive, HTTP_STATUS_SERVICE_UNAVAILABLE, b"In maintenance!")
		result = HTTP_MIDDLEWARE_RESULT_STOP

	return result

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	http_cerver_add_before (http_cerver, http_before_middleware (timer_start))
	http_cerver_add_after (http_cerver, http_after_middleware (timer_end))

	for origin in ALLOWED_ORIGINS:
		http_cerver_add_origin_to_whitelist (http_cerver, origin.encode ("utf-8"))

	orders = http_group (http_cerver, "api/orders")
	orders.before (maintenance)

	@orders.get ("/", cors=True)
	def orders_list (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"orders": []})

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
