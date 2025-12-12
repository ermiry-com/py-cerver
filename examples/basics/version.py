"""The versions of pycerver and of cerver, printed and served.

	python3 examples/basics/version.py
	curl http://localhost:8080/version
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run, version
from cerver import cerver_version_print_full, pycerver_version_print_full
from cerver.http import HTTP_STATUS_OK, REQUEST_METHOD_GET
from cerver.http import http_cerver_configuration, http_cerver_get, http_group, http_response_json_send

SERVICE_NAME = "version"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

def version_handler (http_receive, request):
	"""GET /version"""
	http_response_json_send (http_receive, HTTP_STATUS_OK, version)

def main () -> int:
	cerver_init ()

	cerver_version_print_full ()
	pycerver_version_print_full ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_group (http_cerver_get (service), "version", REQUEST_METHOD_GET, version_handler)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
