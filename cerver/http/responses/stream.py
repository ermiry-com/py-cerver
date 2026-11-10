"""The streamed responses: the status and the headers, then the body in pieces."""

from ctypes import c_void_p, c_size_t, c_uint8, c_bool

from ...lib import lib_function

__all__ = [
	"http_response_stream_begin", "http_response_stream_write",
	"http_response_stream_end", "http_response_stream_is_active"
]

http_response_stream_begin = lib_function (
	"http_response_stream_begin", [c_void_p, c_void_p], c_uint8,
	"""Sends the status and the headers of a response without Content-Length.

	The body is chunked to an HTTP/1.1 client, and it ends when the connection closes for an
	HTTP/1.0 one. Cerver ends a stream that its handler did not end.

	Args:
		http_receive: The HttpReceive of the request.
		response: The HttpResponse with the status and the headers.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_stream_write = lib_function (
	"http_response_stream_write", [c_void_p, c_void_p, c_size_t], c_uint8,
	"""Sends a piece of the body of a stream.

	Args:
		http_receive: The HttpReceive of the request.
		data: The bytes of the piece.
		length: Their length.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_stream_end = lib_function (
	"http_response_stream_end", [c_void_p], c_uint8,
	"""Ends a stream.

	Args:
		http_receive: The HttpReceive of the request.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_stream_is_active = lib_function (
	"http_response_stream_is_active", [c_void_p], c_bool,
	"""Returns if a stream was begun and not ended.

	Args:
		http_receive: The HttpReceive of the request.

	Returns:
		True while it is active.
	"""
)
