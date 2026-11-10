"""The errors of the service: the responses are created once and sent by every handler."""

from cerver.http import HTTP_STATUS_BAD_REQUEST, HTTP_STATUS_NOT_FOUND, HTTP_STATUS_INTERNAL_SERVER_ERROR
from cerver.http import HttpPrebuiltResponses, http_response_json_send

SERVICE_ERROR_NONE = 0
SERVICE_ERROR_BAD_REQUEST = 1
SERVICE_ERROR_NOT_FOUND = 2
SERVICE_ERROR_INTERNAL = 3

responses = HttpPrebuiltResponses ()

def errors_init () -> None:
	"""Creates the responses of the errors, before the service starts."""
	responses.add (SERVICE_ERROR_BAD_REQUEST, HTTP_STATUS_BAD_REQUEST, {"error": "Bad request!"})
	responses.add (SERVICE_ERROR_NOT_FOUND, HTTP_STATUS_NOT_FOUND, {"error": "Not found!"})
	responses.add (SERVICE_ERROR_INTERNAL, HTTP_STATUS_INTERNAL_SERVER_ERROR, {"error": "Internal error!"})

def errors_end () -> None:
	"""Releases the responses, after the service stopped."""
	responses.delete ()

def error_send (http_receive, error: int, errors: dict | None = None) -> None:
	"""Sends an error, with the errors of the fields when there are some."""
	if (errors):
		http_response_json_send (http_receive, HTTP_STATUS_BAD_REQUEST, {"errors": errors})

	else:
		responses.send (error, http_receive)
