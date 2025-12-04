"""The redirects."""

import html

from ..content import HTTP_CONTENT_TYPE_HTML
from ..headers import HTTP_HEADER_LOCATION

from .core import http_response_create, http_response_add_header
from .core import http_response_add_content_type_header, http_response_add_content_length_header
from .core import http_response_compile, http_response_send, http_response_delete

__all__ = [
	"REDIRECT_LINE_BREAKS",
	"redirect"
]

REDIRECT_LINE_BREAKS = ("\r", "\n")

TEXT_ENCODING = "utf-8"

def redirect (http_receive: int, status: int, location: str) -> int:
	"""Sends a redirect to a location.

	The header carries the location as it is, only the HTML body escapes it.

	Args:
		http_receive: The HttpReceive of the request.
		status: A 3xx HTTP_STATUS_* value, like HTTP_STATUS_SEE_OTHER.
		location: The url of the redirect.

	Returns:
		0 on success, 1 on error.

	Raises:
		ValueError: If the location has a line break, that would add headers.
	"""
	if (any (line_break in location for line_break in REDIRECT_LINE_BREAKS)):
		raise ValueError ("The location of a redirect can not have line breaks")

	result = 1

	display_location = html.escape (location)

	body = (
		'<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
		"<title>Redirecting...</title>\n"
		"<h1>Redirecting...</h1>\n"
		"<p>You should be redirected automatically to target URL: "
		f'<a href="{display_location}">{display_location}</a>. If'
		" not click the link."
	).encode (TEXT_ENCODING)

	response = http_response_create (status, body, len (body))
	if (response):
		http_response_add_content_type_header (response, HTTP_CONTENT_TYPE_HTML)
		http_response_add_content_length_header (response, len (body))
		http_response_add_header (response, HTTP_HEADER_LOCATION, location.encode (TEXT_ENCODING))

		if (not http_response_compile (response)):
			result = http_response_send (response, http_receive)

		http_response_delete (response)

	return result
