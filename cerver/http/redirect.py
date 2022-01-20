from ctypes import c_void_p
import html

from .content import HTTP_CONTENT_TYPE_HTML
from .headers import HTTP_HEADER_LOCATION
from .response import http_response_create
from .response import http_response_add_header
from .response import http_response_add_content_type_header
from .response import http_response_add_content_length_header
from .response import http_response_compile
from .response import http_response_print
from .response import http_response_send
from .response import http_response_delete
from .status import http_status, HTTP_STATUS_SEE_OTHER

def redirect (http_receive: c_void_p, status: http_status, location: str):
	display_location = html.escape (location)
	actual_location = display_location.encode ("utf-8")

	body = ('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">\n'
	"<title>Redirecting...</title>\n"
	"<h1>Redirecting...</h1>\n"
	"<p>You should be redirected automatically to target URL: "
	f'<a href="{display_location}">{display_location}</a>. If'
	" not click the link.")

	actual_body = body.encode ("utf-8")
	body_len = len (actual_body)

	response = http_response_create (status, actual_body, body_len)
	if (response):
		http_response_add_content_type_header (response, HTTP_CONTENT_TYPE_HTML)
		http_response_add_content_length_header (response, body_len)

		http_response_add_header (response, HTTP_HEADER_LOCATION, actual_location)

		http_response_compile (response)

		# http_response_print (response)

		http_response_send (response, http_receive)
		http_response_delete (response)
