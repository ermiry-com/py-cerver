"""The responses with a file, a video or a text."""

from ctypes import c_void_p, c_char_p, c_size_t, c_uint8

from ...lib import lib_function, lib_c_string

from ..status import HttpStatus

__all__ = [
	"HTTP_RESPONSE_FILE_CHUNK_SIZE", "HTTP_RESPONSE_VIDEO_CHUNK_SIZE",
	"http_response_send_file", "http_response_send_file_generate_variadic",
	"http_response_send_file_generate",
	"http_response_render_text",
	"http_response_handle_video", "http_response_handle_video_generate_variadic",
	"http_response_handle_video_generate"
]

HTTP_RESPONSE_FILE_CHUNK_SIZE = 2097152
HTTP_RESPONSE_VIDEO_CHUNK_SIZE = 2097152

# the format that gives a filename as it is
FILENAME_FORMAT = b"%s"

http_response_send_file = lib_function (
	"http_response_send_file", [c_void_p, HttpStatus, c_char_p], c_uint8,
	"""Sends a file with its content type, with sendfile ().

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		filename: The path, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_send_file_generate_variadic = lib_function (
	"http_response_send_file_generate", None, c_uint8,
	"""Works like http_response_send_file () with a printf format for the path (variadic).

	Args:
		http_receive: The HttpReceive, as c_void_p.
		status: An HTTP_STATUS_* value, as c_int.
		format: The format, as bytes, followed by its arguments.

	Returns:
		0 on success, 1 on error.
	"""
)

def http_response_send_file_generate (http_receive: int, status: int, filename: str | bytes) -> int:
	"""Sends a file with its content type.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		filename: The path.

	Returns:
		0 on success, 1 on error.
	"""
	return http_response_send_file_generate_variadic (
		c_void_p (http_receive), HttpStatus (status),
		c_char_p (FILENAME_FORMAT), c_char_p (lib_c_string (filename))
	)

http_response_render_text = lib_function (
	"http_response_render_text", [c_void_p, HttpStatus, c_char_p, c_size_t], c_uint8,
	"""Sends a text with the text/html content type.

	Args:
		http_receive: The HttpReceive of the request.
		status: An HTTP_STATUS_* value.
		text: The text, as bytes.
		text_len: Its length in bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_handle_video = lib_function (
	"http_response_handle_video", [c_void_p, c_char_p], c_uint8,
	"""Sends the part of a video that the Range of the request asks for.

	Args:
		http_receive: The HttpReceive of the request.
		filename: The path of the video, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

http_response_handle_video_generate_variadic = lib_function (
	"http_response_handle_video_generate", None, c_uint8,
	"""Works like http_response_handle_video () with a printf format for the path (variadic).

	Args:
		http_receive: The HttpReceive, as c_void_p.
		format: The format, as bytes, followed by its arguments.

	Returns:
		0 on success, 1 on error.
	"""
)

def http_response_handle_video_generate (http_receive: int, filename: str | bytes) -> int:
	"""Sends the part of a video that the Range of the request asks for.

	Args:
		http_receive: The HttpReceive of the request.
		filename: The path of the video.

	Returns:
		0 on success, 1 on error.
	"""
	return http_response_handle_video_generate_variadic (
		c_void_p (http_receive), c_char_p (FILENAME_FORMAT), c_char_p (lib_c_string (filename))
	)
