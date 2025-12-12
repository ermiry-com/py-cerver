"""A web service configured from environment variables: the address, the threads, the limits,
the timeouts and the policies when it is full or when it is drained.

	PORT=8080 BIND_ADDRESS=::1 THREADS=8 python3 examples/basics/configuration.py
	curl http://[::1]:8080/api/status
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run, cerver_create_web
from cerver import cerver_set_alias, cerver_set_bind_address, cerver_set_ipv6_only
from cerver import cerver_set_handler_type, cerver_set_thpool_n_threads, cerver_set_thpool_queue_size
from cerver import cerver_set_receive_buffer_size, cerver_set_reusable_address_flags
from cerver import cerver_set_overload_policy, cerver_set_drain_policy, cerver_set_drain_timeout
from cerver import cerver_set_send_timeout
from cerver import CERVER_HANDLER_TYPE_THREADS, CERVER_OVERLOAD_POLICY_REJECT, CERVER_DRAIN_POLICY_RUN
from cerver.http import HTTP_STATUS_OK, REQUEST_METHOD_GET
from cerver.http import http_cerver_get, http_group, http_response_json_send
from cerver.http import http_cerver_set_max_body_size, http_cerver_set_max_url_size
from cerver.http import http_cerver_set_max_headers, http_cerver_set_max_file_size
from cerver.http import http_cerver_set_headers_timeout, http_cerver_set_request_timeout
from cerver.http import http_cerver_all_stats_print, http_receive_get_cerver

SERVICE_NAME = b"configuration-service"

PORT = int (os.environ.get ("PORT", 8080))
BIND_ADDRESS = os.environ.get ("BIND_ADDRESS", "0.0.0.0")
THREADS = int (os.environ.get ("THREADS", 4))
QUEUE_SIZE = int (os.environ.get ("QUEUE_SIZE", 64))
CONNECTION_QUEUE = int (os.environ.get ("CONNECTION_QUEUE", 64))
RECEIVE_BUFFER_SIZE = int (os.environ.get ("RECEIVE_BUFFER_SIZE", 4096))

MAX_BODY_SIZE = 1 << 22
MAX_URL_SIZE = 1 << 12
MAX_HEADERS = 64
MAX_FILE_SIZE = 1 << 24

HEADERS_TIMEOUT = 8
REQUEST_TIMEOUT = 32
SEND_TIMEOUT = 16
DRAIN_TIMEOUT = 16

def status (http_receive, request):
	"""GET /api/status, it also prints the stats of the cerver"""
	http_cerver_all_stats_print (http_receive_get_cerver (http_receive))
	http_response_json_send (http_receive, HTTP_STATUS_OK, {"status": "ok", "threads": THREADS})

def configure (service: int) -> None:
	"""Sets every value of the cerver and of its HttpCerver."""
	cerver_set_alias (service, b"configuration")
	if (cerver_set_bind_address (service, BIND_ADDRESS.encode ("utf-8"))):
		raise ValueError (f"Invalid bind address {BIND_ADDRESS}")

	# an IPv6 cerver also accepts IPv4 connections unless it is IPv6 only
	cerver_set_ipv6_only (service, False)

	cerver_set_handler_type (service, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_thpool_n_threads (service, THREADS)
	cerver_set_thpool_queue_size (service, QUEUE_SIZE)
	cerver_set_receive_buffer_size (service, RECEIVE_BUFFER_SIZE)
	cerver_set_reusable_address_flags (service, True)

	# a full cerver answers 503 right away, a drained one finishes the queued requests
	cerver_set_overload_policy (service, CERVER_OVERLOAD_POLICY_REJECT)
	cerver_set_drain_policy (service, CERVER_DRAIN_POLICY_RUN)
	cerver_set_drain_timeout (service, DRAIN_TIMEOUT)
	cerver_set_send_timeout (service, SEND_TIMEOUT)

	http_cerver = http_cerver_get (service)
	http_cerver_set_max_body_size (http_cerver, MAX_BODY_SIZE)
	http_cerver_set_max_url_size (http_cerver, MAX_URL_SIZE)
	http_cerver_set_max_headers (http_cerver, MAX_HEADERS)
	http_cerver_set_max_file_size (http_cerver, MAX_FILE_SIZE)
	http_cerver_set_headers_timeout (http_cerver, HEADERS_TIMEOUT)
	http_cerver_set_request_timeout (http_cerver, REQUEST_TIMEOUT)

	http_group (http_cerver, "api/status", REQUEST_METHOD_GET, status)

def main () -> int:
	cerver_init ()

	service = cerver_create_web (SERVICE_NAME, PORT, CONNECTION_QUEUE)
	configure (service)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
