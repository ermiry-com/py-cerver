"""The files of a client: the ones it requests to a cerver, the ones it sends and the ones it receives."""

from ctypes import CFUNCTYPE, c_char_p, c_void_p, c_uint8, c_size_t
from typing import TypeAlias

from ..lib import lib_function

from ..types.string import StringPointer

__all__ = [
	"CLIENT_FILES_MAX_PATHS",
	"ClientFileUploadHandler", "ClientFileUploadCallback",
	"client_file_stats_print",
	"client_files_add_path", "client_files_set_uploads_path",
	"client_files_set_file_upload_handler", "client_files_set_file_upload_cb",
	"client_files_search_file", "client_file_get", "client_file_send"
]

CLIENT_FILES_MAX_PATHS = 32

# u8 (*) (Client *, Connection *, FileHeader *, const char *file_data, size_t, char **saved_filename)
ClientFileUploadHandler: TypeAlias = CFUNCTYPE ( # type: ignore
	c_uint8, c_void_p, c_void_p, c_void_p, c_void_p, c_size_t, c_void_p
)

# void (*) (Client *, Connection *, const char *saved_filename)
ClientFileUploadCallback: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p, c_char_p) # type: ignore

client_file_stats_print = lib_function (
	"client_file_stats_print", [c_void_p], None,
	"""Prints the file stats of a client.

	Args:
		client: The client.
	"""
)

client_files_add_path = lib_function (
	"client_files_add_path", [c_void_p, c_char_p], c_uint8,
	"""Adds a path where the files that are requested to the client are searched.

	Args:
		client: The client.
		path: The path, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

client_files_set_uploads_path = lib_function (
	"client_files_set_uploads_path", [c_void_p, c_char_p], None,
	"""Sets the path where the files that the client receives are saved.

	Args:
		client: The client.
		uploads_path: The path, as bytes.
	"""
)

client_files_set_file_upload_handler = lib_function (
	"client_files_set_file_upload_handler", [c_void_p, c_void_p], None,
	"""Sets a method that receives the files that the client gets.

	Args:
		client: The client.
		file_upload_handler: A ClientFileUploadHandler kept by the caller that returns 0 on success.
	"""
)

client_files_set_file_upload_cb = lib_function (
	"client_files_set_file_upload_cb", [c_void_p, c_void_p], None,
	"""Sets a method that runs after the client received a file.

	Args:
		client: The client.
		file_upload_cb: A ClientFileUploadCallback kept by the caller.
	"""
)

client_files_search_file = lib_function (
	"client_files_search_file", [c_void_p, c_char_p], StringPointer,
	"""Searches a file in the paths of the client.

	Args:
		client: The client.
		filename: The name of the file, as bytes.

	Returns:
		The path as a new StringPointer (released with str_delete ()), NULL if it was not found.
	"""
)

client_file_get = lib_function (
	"client_file_get", [c_void_p, c_void_p, c_char_p], c_uint8,
	"""Requests a file to the cerver, it is saved in the uploads path of the client.

	Args:
		client: The client.
		connection: The connection.
		filename: The name of the file, as bytes.

	Returns:
		0 when the request was sent, 1 on error.
	"""
)

client_file_send = lib_function (
	"client_file_send", [c_void_p, c_void_p, c_char_p], c_uint8,
	"""Sends a file to the cerver.

	Args:
		client: The client.
		connection: The connection.
		filename: The path, as bytes.

	Returns:
		0 when it was sent, 1 on error.
	"""
)
