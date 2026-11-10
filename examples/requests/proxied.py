"""A service behind a reverse proxy: the address of the client from X-Forwarded-For of the
trusted proxies, and an id for every request (X-Request-Id), in the response and in the logs.

	python3 examples/requests/proxied.py
	curl http://localhost:8080/api/client -H "X-Forwarded-For: 203.0.113.7" -H "X-Request-Id: abc-1"
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_TRUSTED_PROXIES_LIST
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_cerver_set_trusted_proxies, http_cerver_add_trusted_proxy
from cerver.http import http_cerver_set_request_id
from cerver.http import http_request_get_client_ip_string, http_request_get_id_string
from cerver.http import http_response_json_send
from cerver.utils import cerver_log_success

SERVICE_NAME = "proxied"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

# the networks of the proxies, like the one of a load balancer in front of the service
TRUSTED_PROXIES = ("127.0.0.0/8", "::1", "10.0.0.0/8")

def client (http_receive, request):
	"""GET /api/client"""
	address = http_request_get_client_ip_string (request)
	request_id = http_request_get_id_string (request)

	cerver_log_success (f"{request_id} - request from {address}")
	http_response_json_send (http_receive, HTTP_STATUS_OK, {"client": address, "request": request_id})

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	http_cerver_set_trusted_proxies (http_cerver, HTTP_TRUSTED_PROXIES_LIST)
	for network in TRUSTED_PROXIES:
		http_cerver_add_trusted_proxy (http_cerver, network.encode ("utf-8"))

	http_cerver_set_request_id (http_cerver, True)

	api = http_group (http_cerver, "api")
	api.get ("/client") (client)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
