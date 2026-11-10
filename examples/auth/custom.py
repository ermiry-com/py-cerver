"""A custom authentication: a handler that accepts or rejects each request before its handler,
like an API key, and the admin routes of the cerver behind the same key with their metrics.

	python3 examples/auth/custom.py
	curl http://localhost:8080/api/reports -H "X-Api-Key: example-key"
	curl -i http://localhost:8080/api/reports                       # 401
	curl http://localhost:8080/cerver/metrics -H "X-Api-Key: example-key"
"""

import hmac
import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.callbacks import callback_wrap
from cerver.http import HTTP_STATUS_OK, HTTP_ROUTE_AUTH_TYPE_CUSTOM, HttpAuthenticationHandler
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_group_set_auth, http_group_set_authentication_handler
from cerver.http import http_cerver_enable_admin_routes, http_cerver_enable_admin_routes_authentication
from cerver.http import http_cerver_admin_routes_set_authentication_handler
from cerver.http import http_request_get_custom_header_string, http_response_json_send

SERVICE_NAME = "custom"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

API_KEY = os.environ.get ("API_KEY", "example-key")
API_KEY_HEADER = "X-Api-Key"

# the results of an authentication handler
AUTHENTICATED = 0
REJECTED = 1

def authenticate (http_receive, request) -> int:
	"""Accepts a request with the key of the service, cerver answers 401 to the other ones."""
	key = http_request_get_custom_header_string (request, API_KEY_HEADER) or ""
	return AUTHENTICATED if (hmac.compare_digest (key, API_KEY)) else REJECTED

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	authentication = callback_wrap (authenticate, HttpAuthenticationHandler)

	reports = http_group (http_cerver, "api/reports")
	http_group_set_auth (reports.group, HTTP_ROUTE_AUTH_TYPE_CUSTOM)
	http_group_set_authentication_handler (reports.group, authentication)

	@reports.get ("/")
	def reports_list (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"reports": []})

	http_cerver_enable_admin_routes (http_cerver, True)
	http_cerver_enable_admin_routes_authentication (http_cerver, HTTP_ROUTE_AUTH_TYPE_CUSTOM)
	http_cerver_admin_routes_set_authentication_handler (http_cerver, authentication)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
