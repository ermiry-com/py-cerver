"""Where an HTTP cerver saves the files of the multipart requests."""

from ctypes import c_void_p, c_char_p, c_bool, c_uint

from ...lib import lib_function, lib_c_string

from ..routes import HttpHandler

__all__ = [
	"HTTP_CERVER_DEFAULT_UPLOADS_DIR_MODE", "HTTP_CERVER_DEFAULT_UPLOADS_FILE_MODE",
	"HTTP_CERVER_DEFAULT_UPLOADS_DELETE",
	"UploadsFilenameGenerator", "UploadsDirnameGenerator",
	"http_cerver_set_uploads_path", "http_cerver_generate_uploads_path_variadic",
	"http_cerver_generate_uploads_path", "http_cerver_set_uploads_file_mode",
	"http_cerver_default_uploads_filename_generator", "http_cerver_set_uploads_filename_generator",
	"http_cerver_set_default_uploads_filename_generator",
	"http_cerver_set_uploads_dir_mode",
	"http_cerver_default_uploads_dirname_generator", "http_cerver_set_uploads_dirname_generator",
	"http_cerver_set_default_uploads_dirname_generator",
	"http_cerver_set_uploads_delete_when_done"
]

HTTP_CERVER_DEFAULT_UPLOADS_DIR_MODE = 0o755
HTTP_CERVER_DEFAULT_UPLOADS_FILE_MODE = 0o644
HTTP_CERVER_DEFAULT_UPLOADS_DELETE = False

# void (*) (const HttpReceive *, const HttpRequest *), called while a request is parsed
UploadsFilenameGenerator = HttpHandler
UploadsDirnameGenerator = HttpHandler

# the format that gives a path as it is
UPLOADS_PATH_FORMAT = b"%s"

http_cerver_set_uploads_path = lib_function (
	"http_cerver_set_uploads_path", [c_void_p, c_char_p], None,
	"""Sets the directory where the files of the multipart requests are saved.

	Args:
		http_cerver: The HttpCerver.
		uploads_path: The directory, as bytes.
	"""
)

http_cerver_generate_uploads_path_variadic = lib_function (
	"http_cerver_generate_uploads_path", None, None,
	"""Sets the uploads directory with a printf format (variadic).

	Args:
		http_cerver: The HttpCerver, as c_void_p.
		format: The format, as bytes, followed by its arguments.
	"""
)

def http_cerver_generate_uploads_path (http_cerver: int, uploads_path: str | bytes) -> None:
	"""Sets the directory where the files of the multipart requests are saved.

	Args:
		http_cerver: The HttpCerver.
		uploads_path: The directory.
	"""
	http_cerver_generate_uploads_path_variadic (
		c_void_p (http_cerver), c_char_p (UPLOADS_PATH_FORMAT), c_char_p (lib_c_string (uploads_path))
	)

http_cerver_set_uploads_file_mode = lib_function (
	"http_cerver_set_uploads_file_mode", [c_void_p, c_uint], None,
	"""Sets the permissions of the uploaded files.

	Args:
		http_cerver: The HttpCerver.
		file_mode: The permissions, HTTP_CERVER_DEFAULT_UPLOADS_FILE_MODE by default.
	"""
)

http_cerver_default_uploads_filename_generator = lib_function (
	"http_cerver_default_uploads_filename_generator", [c_void_p, c_void_p], None,
	"""The default generator of the filenames of the uploads, "<sequence>-<time>-<filename>".

	Args:
		http_receive: The HttpReceive of the request.
		request: The request.
	"""
)

http_cerver_set_uploads_filename_generator = lib_function (
	"http_cerver_set_uploads_filename_generator", [c_void_p, c_void_p], None,
	"""Sets the method that gives a filename to each uploaded file.

	It is called while the request is parsed, it gets the part with
	http_request_get_current_mpart () and sets its name with http_multi_part_set_generated_filename ().

	Args:
		http_cerver: The HttpCerver.
		uploads_filename_generator: An UploadsFilenameGenerator kept by the caller.
	"""
)

http_cerver_set_default_uploads_filename_generator = lib_function (
	"http_cerver_set_default_uploads_filename_generator", [c_void_p], None,
	"""Uses the default generator of the filenames of the uploads.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_set_uploads_dir_mode = lib_function (
	"http_cerver_set_uploads_dir_mode", [c_void_p, c_uint], None,
	"""Sets the permissions of the directories of the uploads.

	Args:
		http_cerver: The HttpCerver.
		dir_mode: The permissions, HTTP_CERVER_DEFAULT_UPLOADS_DIR_MODE by default.
	"""
)

http_cerver_default_uploads_dirname_generator = lib_function (
	"http_cerver_default_uploads_dirname_generator", [c_void_p, c_void_p], None,
	"""The default generator of the directory of the uploads of a request, "<sequence>-<time>".

	Args:
		http_receive: The HttpReceive of the request.
		request: The request.
	"""
)

http_cerver_set_uploads_dirname_generator = lib_function (
	"http_cerver_set_uploads_dirname_generator", [c_void_p, c_void_p], None,
	"""Sets the method that gives a directory to the uploads of each request.

	It sets the directory with http_request_set_dirname ().

	Args:
		http_cerver: The HttpCerver.
		uploads_dirname_generator: An UploadsDirnameGenerator kept by the caller.
	"""
)

http_cerver_set_default_uploads_dirname_generator = lib_function (
	"http_cerver_set_default_uploads_dirname_generator", [c_void_p], None,
	"""Uses the default generator of the directory of the uploads of each request.

	Args:
		http_cerver: The HttpCerver.
	"""
)

http_cerver_set_uploads_delete_when_done = lib_function (
	"http_cerver_set_uploads_delete_when_done", [c_void_p, c_bool], None,
	"""Deletes the uploaded files when their request ends, unless the handler keeps or moves them.

	Args:
		http_cerver: The HttpCerver.
		value: True to delete them.
	"""
)
