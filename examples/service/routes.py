"""The routes of the service and the version endpoint."""

from cerver import version
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_CREATED, REQUEST_METHOD_GET
from cerver.http import http_group, http_response_json_send

import controllers
from handler import route_handler

def version_handler (http_receive, request):
	"""GET /version"""
	http_response_json_send (http_receive, HTTP_STATUS_OK, version)

def routes_register (http_cerver: int, max_body_size: int) -> None:
	"""Registers the groups of the service."""
	http_group (http_cerver, "version", REQUEST_METHOD_GET, version_handler)

	notes = http_group (
		http_cerver, "api/notes", REQUEST_METHOD_GET, route_handler (controllers.notes_list)
	)

	notes.post ("/", max_body_size=max_body_size) (route_handler (controllers.note_create, HTTP_STATUS_CREATED))
	notes.get ("/:id") (route_handler (controllers.note_get))
	notes.delete ("/:id") (route_handler (controllers.note_delete))
