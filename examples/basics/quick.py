"""The smallest web service: a group with two endpoints, run until SIGINT or SIGTERM.

	python3 examples/basics/quick.py
	curl http://localhost:8080/api/hello
	curl http://localhost:8080/api/hello/world
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, REQUEST_METHOD_GET
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_request_get_named_param_string, http_response_json_send

SERVICE_NAME = "quick"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

def hello (http_receive, request):
	"""GET /api/hello"""
	http_response_json_send (http_receive, HTTP_STATUS_OK, {"msg": "Hello from pycerver!"})

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	api = http_group (http_cerver, "api/hello", REQUEST_METHOD_GET, hello)

	@api.get ("/:name")
	def hello_name (http_receive, request):
		"""GET /api/hello/:name"""
		name = http_request_get_named_param_string (request, "name")
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"msg": f"Hello {name}!"})

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
