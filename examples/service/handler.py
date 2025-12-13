"""The handler of every route: it builds the job of the request, runs its controller and sends
its result or its error, so a controller never touches the request or the response.
"""

import functools
import traceback
from typing import Callable

from cerver.http import HTTP_STATUS_OK
from cerver.http import http_request_get_method, http_request_method_str
from cerver.http import http_request_get_url_string, http_request_get_query_params
from cerver.http import http_request_get_body_json, http_request_get_id_string
from cerver.http import http_request_get_client_ip_string, http_get_params_dict
from cerver.http import http_response_json_send
from cerver.utils import cerver_log_error

from errors import SERVICE_ERROR_NONE, SERVICE_ERROR_INTERNAL, error_send

def job_create (request) -> dict:
	"""The values of a request that a controller uses."""
	return {
		"method": http_request_method_str (http_request_get_method (request)).decode ("utf-8"),
		"path": http_request_get_url_string (request),
		"params": http_get_params_dict (request),
		"query": http_request_get_query_params (request),
		"body": http_request_get_body_json (request) or {},
		"request": http_request_get_id_string (request),
		"client": http_request_get_client_ip_string (request)
	}

def route_handler (controller: Callable [[dict], tuple], status: int = HTTP_STATUS_OK) -> Callable:
	"""Returns a handler of cerver that runs a controller that returns (error, errors, result)."""
	@functools.wraps (controller)
	def handler (http_receive, request):
		job = job_create (request)

		try:
			error, errors, result = controller (job)

		except Exception:
			cerver_log_error (f"{job['method']} {job['path']} failed:\n{traceback.format_exc ()}")
			error, errors, result = SERVICE_ERROR_INTERNAL, None, None

		if (error == SERVICE_ERROR_NONE):
			http_response_json_send (http_receive, status, result)

		else:
			error_send (http_receive, error, errors)

	return handler
