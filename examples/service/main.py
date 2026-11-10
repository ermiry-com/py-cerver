"""A complete service: its configuration, its errors, the handler of its routes, its controllers
and a periodic job, run until SIGINT or SIGTERM (the signal of docker stop).

	python3 examples/service/main.py
	curl -X POST http://localhost:8080/api/notes -d '{"title": "first", "tags": ["a"]}'
	curl "http://localhost:8080/api/notes?tag=a"
	curl -X POST http://localhost:8080/api/notes -d '{"tags": "not a list"}'     # 400 with the errors
	curl http://localhost:8080/version
"""

import sys

from cerver import cerver_init, cerver_end, cerver_run, cerver_create_web
from cerver import cerver_set_alias, cerver_set_receive_buffer_size, cerver_set_thpool_n_threads
from cerver import cerver_set_handler_type, cerver_set_reusable_address_flags
from cerver import cerver_update_interval_configure
from cerver import CERVER_HANDLER_TYPE_THREADS
from cerver import cerver_version_print_full, pycerver_version_print_full
from cerver.http import HTTP_TRUSTED_PROXIES_LIST
from cerver.http import http_cerver_get, http_cerver_set_request_id
from cerver.http import http_cerver_set_trusted_proxies, http_cerver_add_trusted_proxy
from cerver.utils import cerver_log_debug

import config
import controllers
from errors import errors_init, errors_end
from routes import routes_register

def cleanup (cerver, args) -> None:
	"""Runs every CLEANUP_INTERVAL seconds in a thread of the cerver."""
	removed = controllers.notes_cleanup ()
	if (removed):
		cerver_log_debug (f"Removed {removed} expired notes")

def service_create () -> int:
	"""Creates and configures the cerver of the service."""
	service = cerver_create_web (f"{config.SERVICE_NAME}-service".encode ("utf-8"), config.PORT, config.CONNECTION_QUEUE)

	cerver_set_alias (service, config.SERVICE_NAME.encode ("utf-8"))
	cerver_set_receive_buffer_size (service, config.RECEIVE_BUFFER_SIZE)
	cerver_set_thpool_n_threads (service, config.THREADS)
	cerver_set_handler_type (service, CERVER_HANDLER_TYPE_THREADS)
	cerver_set_reusable_address_flags (service, True)

	cerver_update_interval_configure (service, cleanup, config.CLEANUP_INTERVAL)

	http_cerver = http_cerver_get (service)
	http_cerver_set_request_id (http_cerver, True)
	http_cerver_set_trusted_proxies (http_cerver, HTTP_TRUSTED_PROXIES_LIST)
	http_cerver_add_trusted_proxy (http_cerver, config.TRUSTED_PROXY.encode ("utf-8"))

	routes_register (http_cerver, config.MAX_BODY_SIZE)

	return service

def main () -> int:
	cerver_init ()

	cerver_version_print_full ()
	pycerver_version_print_full ()

	errors_init ()

	service = service_create ()

	# cerver_run () returns after the signal, the drain of the requests and the teardown
	result = cerver_run (service)

	errors_end ()
	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
