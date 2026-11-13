"""The clients that leave: a long handler that asks for its client between its steps and stops when it
is gone, the stage that a request reached, and the timeouts in milliseconds, the send one shared by
all the sends of a response so a client that stops reading costs that time in total.

	python3 examples/requests/abandoned.py
	curl http://localhost:8080/api/reports/monthly                     # waits for the report
	curl --max-time 1 http://localhost:8080/api/reports/monthly        # leaves, the handler stops
	curl http://localhost:8080/api/stage
"""

import os
import sys
import time

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_cerver_set_headers_timeout_milliseconds, http_cerver_set_request_timeout_milliseconds
from cerver.http import http_cerver_set_idle_timeout_milliseconds, http_cerver_set_send_timeout_milliseconds
from cerver.http import http_cerver_set_half_close_is_gone
from cerver.http import http_receive_is_client_gone, http_receive_get_client_state, http_receive_get_stage
from cerver.http import http_client_state_string, http_stage_string
from cerver.http import http_request_get_named_param_string
from cerver.http import http_response_json_send
from cerver.utils import cerver_log_warning

SERVICE_NAME = "abandoned"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

HEADERS_TIMEOUT = 2048
REQUEST_TIMEOUT = 8192
IDLE_TIMEOUT = 4096
SEND_TIMEOUT = 2048

# the report takes STEPS steps of STEP_SECONDS each one
STEPS = int (os.environ.get ("STEPS", 8))
STEP_SECONDS = float (os.environ.get ("STEP_SECONDS", 0.25))

def register (http_cerver: int) -> None:
	api = http_group (http_cerver, "api")

	@api.get ("/reports/:name")
	def report (http_receive, request):
		"""A long work that is useless when its client is gone, cerver counts the request as aborted."""
		name = http_request_get_named_param_string (request, "name")

		done = 0
		while ((done < STEPS) and (not http_receive_is_client_gone (http_receive))):
			time.sleep (STEP_SECONDS)
			done += 1

		if (done < STEPS):
			state = http_client_state_string (http_receive_get_client_state (http_receive)).decode ()
			cerver_log_warning (f"The client of the report {name} is gone ({state}) after {done} steps")

		else:
			http_response_json_send (http_receive, HTTP_STATUS_OK, {"report": name, "steps": done})

	@api.get ("/stage")
	def stage (http_receive, request):
		"""The handler runs in the handler stage, the next one is the response."""
		http_response_json_send (http_receive, HTTP_STATUS_OK, {
			"stage": http_stage_string (http_receive_get_stage (http_receive)).decode (),
			"client": http_client_state_string (http_receive_get_client_state (http_receive)).decode ()
		})

def configure (http_cerver: int) -> None:
	http_cerver_set_headers_timeout_milliseconds (http_cerver, HEADERS_TIMEOUT)
	http_cerver_set_request_timeout_milliseconds (http_cerver, REQUEST_TIMEOUT)
	http_cerver_set_idle_timeout_milliseconds (http_cerver, IDLE_TIMEOUT)
	http_cerver_set_send_timeout_milliseconds (http_cerver, SEND_TIMEOUT)

	# a client that only closed its side of the connection is gone too
	http_cerver_set_half_close_is_gone (http_cerver, True)

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	configure (http_cerver)
	register (http_cerver)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
