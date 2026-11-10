"""Static files: a directory served when no endpoint matches, and a file sent by a handler.

	python3 examples/basics/static.py
	curl http://localhost:8080/index.html
	curl http://localhost:8080/home
"""

import os
import sys
from pathlib import Path

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, REQUEST_METHOD_GET
from cerver.http import http_cerver_configuration, http_cerver_get, http_cerver_static_path_add
from cerver.http import http_group, http_response_send_file

SERVICE_NAME = "static"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

PUBLIC = Path (__file__).resolve ().parent / "public"

def home (http_receive, request):
	"""GET /home, sends index.html with its content type"""
	http_response_send_file (http_receive, HTTP_STATUS_OK, str (PUBLIC / "index.html").encode ("utf-8"))

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	http_cerver_static_path_add (http_cerver, str (PUBLIC).encode ("utf-8"))
	http_group (http_cerver, "home", REQUEST_METHOD_GET, home)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
