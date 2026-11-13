"""Files: directories, paths, images, the files cerver and the sending of files to a connection."""

from ctypes import CFUNCTYPE, POINTER, Structure
from ctypes import c_int, c_uint, c_uint8, c_uint64, c_char, c_char_p, c_bool, c_void_p
from ctypes import c_size_t, c_ssize_t, byref, create_string_buffer, string_at
from typing import TypeAlias

from ..lib import lib_function, lib_take_c_string, lib_c_string, lib_text, libc_free

from ..types.string import StringPointer

__all__ = [
	"DIRNAME_DEFAULT_SIZE", "FILENAME_DEFAULT_SIZE", "FILES_MOVE_SIZE", "FILE_CERVER_MAX_PATHS",
	"FILES_DEFAULT_DIRECTORY_MODE",
	"FileUploadHandler", "FileUploadCallback",
	"file_cerver_add_path", "file_cerver_set_uploads_path",
	"file_cerver_set_file_upload_handler", "file_cerver_set_file_upload_cb",
	"file_cerver_search_file", "file_cerver_send_file", "file_cerver_stats_print",
	"files_sanitize_filename", "files_sanitize_complete_filename",
	"files_create_dir", "files_create_recursive_dir", "file_move_to",
	"files_copy", "files_copy_recursive", "files_remove_recursive",
	"files_get_file_extension_c_string", "files_get_file_extension_reference",
	"file_exists", "file_read_c_string", "file_n_read_c_string",
	"files_get_file_extension", "files_sanitize", "files_sanitize_complete",
	"file_read", "file_n_read",
	"ImageType",
	"IMAGE_TYPE_NONE", "IMAGE_TYPE_PNG", "IMAGE_TYPE_JPEG", "IMAGE_TYPE_GIF", "IMAGE_TYPE_BMP",
	"files_image_type_to_string", "files_image_type_extension",
	"files_image_get_type_from_file", "files_image_get_type", "files_image_get_type_by_extension",
	"files_image_is_jpeg", "files_image_extension_is_jpeg",
	"files_image_is_png", "files_image_extension_is_png",
	"FileHeader", "FileHeaderPointer",
	"file_header_is_valid", "file_header_get",
	"file_send", "file_send_by_fd"
]

DIRNAME_DEFAULT_SIZE = 1024
FILENAME_DEFAULT_SIZE = 1024
FILES_MOVE_SIZE = 2048

FILE_CERVER_MAX_PATHS = 32

# rwxr-xr-x
FILES_DEFAULT_DIRECTORY_MODE = 0o755

# u8 (*) (Cerver *, Client *, Connection *, FileHeader *, const char *file_data, size_t, char **saved_filename)
FileUploadHandler: TypeAlias = CFUNCTYPE ( # type: ignore
	c_uint8, c_void_p, c_void_p, c_void_p, c_void_p, c_void_p, c_size_t, c_void_p
)

# void (*) (Cerver *, Client *, Connection *, const char *saved_filename)
FileUploadCallback: TypeAlias = CFUNCTYPE (None, c_void_p, c_void_p, c_void_p, c_char_p) # type: ignore

# cerver
file_cerver_add_path = lib_function (
	"file_cerver_add_path", [c_void_p, c_char_p], c_uint8,
	"""Adds a path where the files that the clients request are searched.

	Args:
		file_cerver: The FileCerver of a CERVER_TYPE_FILES cerver.
		path: The path, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

file_cerver_set_uploads_path = lib_function (
	"file_cerver_set_uploads_path", [c_void_p, c_char_p], None,
	"""Sets the path where the files that the clients upload are saved.

	Args:
		file_cerver: The FileCerver.
		uploads_path: The path, as bytes.
	"""
)

file_cerver_set_file_upload_handler = lib_function (
	"file_cerver_set_file_upload_handler", [c_void_p, c_void_p], None,
	"""Sets a method that receives the files that the clients upload.

	Args:
		file_cerver: The FileCerver.
		file_upload_handler: A FileUploadHandler kept by the caller that returns 0 on success.
	"""
)

file_cerver_set_file_upload_cb = lib_function (
	"file_cerver_set_file_upload_cb", [c_void_p, c_void_p], None,
	"""Sets a method that runs after a client uploaded a file.

	Args:
		file_cerver: The FileCerver.
		file_upload_cb: A FileUploadCallback kept by the caller.
	"""
)

file_cerver_search_file = lib_function (
	"file_cerver_search_file", [c_void_p, c_char_p], StringPointer,
	"""Searches a file in the paths of the files cerver.

	Args:
		file_cerver: The FileCerver.
		filename: The name of the file, as bytes.

	Returns:
		The path of the file as a StringPointer that the caller releases, NULL if it was not found.
	"""
)

file_cerver_send_file = lib_function (
	"file_cerver_send_file", [c_void_p, c_void_p, c_void_p, c_char_p], c_ssize_t,
	"""Sends a file of the paths of the files cerver to a connection.

	The FileHeader goes first in a packet, then the contents of the file. A file that is
	not found is answered with a CERVER_ERROR_FILE_NOT_FOUND error packet.

	Args:
		cerver: The cerver.
		client: The client.
		connection: The connection.
		filename: The name of the file, as bytes.

	Returns:
		The bytes that were sent, -1 on error.
	"""
)

file_cerver_stats_print = lib_function (
	"file_cerver_stats_print", [c_void_p], None,
	"""Prints the stats of a files cerver.

	Args:
		file_cerver: The FileCerver.
	"""
)

# main
files_sanitize_filename = lib_function (
	"files_sanitize_filename", [c_void_p], None,
	"""Removes from a filename every character that is not a letter, a number, '-', '_' or '.'.

	Use files_sanitize () with a str.

	Args:
		filename: A writable buffer with the filename, it is changed in place.
	"""
)

files_sanitize_complete_filename = lib_function (
	"files_sanitize_complete_filename", [c_void_p], None,
	"""Works like files_sanitize_filename () but keeps the '/' characters.

	Use files_sanitize_complete () with a str.

	Args:
		filename: A writable buffer with the filename, it is changed in place.
	"""
)

files_create_dir = lib_function (
	"files_create_dir", [c_char_p, c_uint], c_uint,
	"""Creates a directory if it does not exist.

	Args:
		dir_path: The path, as bytes.
		mode: Its permissions, like 0o755.

	Returns:
		0 on success, 1 on error.
	"""
)

files_create_recursive_dir = lib_function (
	"files_create_recursive_dir", [c_char_p, c_uint], c_uint,
	"""Creates every directory of a path, a path that already is a directory is a success.

	Args:
		dir_path: The path, as bytes, shorter than DIRNAME_DEFAULT_SIZE.
		mode: Their permissions, like 0o755.

	Returns:
		0 on success, 1 on error.
	"""
)

file_move_to = lib_function (
	"file_move_to", [c_char_p, c_char_p], c_int,
	"""Moves a file or a directory with rename (), or with a copy between file systems.

	Args:
		actual_path: The current path, as bytes.
		saved_path: The new path, as bytes, or a directory that exists to move it inside.

	Returns:
		0 on success, 1 on error.
	"""
)

files_copy = lib_function (
	"files_copy", [c_char_p, c_char_p], c_uint,
	"""Copies a file, a copy that fails is removed.

	Args:
		source: The path of the file, as bytes.
		destination: The path of the copy, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

files_copy_recursive = lib_function (
	"files_copy_recursive", [c_char_p, c_char_p], c_uint,
	"""Copies a file or a directory with everything in it, the directories of the destination can exist.

	Args:
		source: The path, as bytes.
		destination: The path of the copy, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

files_remove_recursive = lib_function (
	"files_remove_recursive", [c_char_p], c_uint,
	"""Removes a file, a symbolic link (without following it) or a directory with everything in it.

	Args:
		path: The path, as bytes.

	Returns:
		0 on success, 1 on error.
	"""
)

files_get_file_extension_c_string = lib_function (
	"files_get_file_extension", [c_char_p], c_void_p,
	"""Returns the extension of a filename in a new C string, use files_get_file_extension ().

	Args:
		filename: The filename, as bytes.

	Returns:
		The address of the extension that the caller frees, None if it has none.
	"""
)

files_get_file_extension_reference = lib_function (
	"files_get_file_extension_reference", [c_char_p, POINTER (c_uint)], c_char_p,
	"""Returns the extension of a filename without a copy.

	Args:
		filename: The filename, as bytes.
		ext_len: A pointer to a c_uint that gets the length of the extension.

	Returns:
		The extension, as bytes, None if it has none.
	"""
)

file_exists = lib_function (
	"file_exists", [c_char_p], c_bool,
	"""Returns if a file exists.

	Args:
		filename: The path, as bytes.

	Returns:
		True if it exists.
	"""
)

file_read_c_string = lib_function (
	"file_read", [c_char_p, POINTER (c_size_t)], c_void_p,
	"""Reads a file into a new buffer, use file_read ().

	Args:
		filename: The path, as bytes.
		file_size: A pointer to a c_size_t that gets the bytes that were read.

	Returns:
		The address of the buffer that the caller frees, None on error.
	"""
)

file_n_read_c_string = lib_function (
	"file_n_read", [c_char_p, c_size_t, POINTER (c_size_t)], c_void_p,
	"""Reads up to n bytes of a file into a new buffer, use file_n_read ().

	Args:
		filename: The path, as bytes.
		n_bytes: The most bytes to read.
		n_read: A pointer to a c_size_t that gets the bytes that were read.

	Returns:
		The address of the buffer that the caller frees, None on error.
	"""
)

def files_get_file_extension (filename: str | bytes) -> str | None:
	"""Returns the extension of a filename.

	Args:
		filename: The filename.

	Returns:
		The extension without the dot, None if it has none.
	"""
	return lib_text (lib_take_c_string (files_get_file_extension_c_string (lib_c_string (filename))))

def files_sanitize_with (function, filename: str | bytes) -> str | None:
	"""Runs a sanitize function of cerver over a copy of the filename."""
	buffer = create_string_buffer (lib_c_string (filename))
	function (buffer)
	return lib_text (buffer.value)

def files_sanitize (filename: str | bytes) -> str | None:
	"""Returns a filename with only letters, numbers, '-', '_' and '.'.

	Args:
		filename: The filename.

	Returns:
		The sanitized filename.
	"""
	return files_sanitize_with (files_sanitize_filename, filename)

def files_sanitize_complete (filename: str | bytes) -> str | None:
	"""Returns a path with only letters, numbers, '-', '_', '.' and '/'.

	Args:
		filename: The path.

	Returns:
		The sanitized path.
	"""
	return files_sanitize_with (files_sanitize_complete_filename, filename)

def file_read_take (pointer: int | None, size: c_size_t) -> bytes | None:
	"""Copies a buffer of cerver with its size and frees it."""
	result = None
	if (pointer):
		result = string_at (pointer, size.value)
		libc_free (pointer)

	return result

def file_read (filename: str | bytes) -> bytes | None:
	"""Reads a file.

	Args:
		filename: The path.

	Returns:
		Its contents, None on error.
	"""
	size = c_size_t (0)
	return file_read_take (file_read_c_string (lib_c_string (filename), byref (size)), size)

def file_n_read (filename: str | bytes, n_bytes: int) -> bytes | None:
	"""Reads up to n bytes of a file.

	Args:
		filename: The path.
		n_bytes: The most bytes to read.

	Returns:
		The bytes that were read, None on error.
	"""
	size = c_size_t (0)
	return file_read_take (file_n_read_c_string (lib_c_string (filename), n_bytes, byref (size)), size)

# images
ImageType: TypeAlias = c_int # type: ignore

IMAGE_TYPE_NONE = 0
IMAGE_TYPE_PNG = 1
IMAGE_TYPE_JPEG = 2
IMAGE_TYPE_GIF = 3
IMAGE_TYPE_BMP = 4

files_image_type_to_string = lib_function (
	"files_image_type_to_string", [ImageType], c_char_p,
	"""Returns the name of an image type.

	Args:
		type: An IMAGE_TYPE_* value.

	Returns:
		The name, as bytes.
	"""
)

files_image_type_extension = lib_function (
	"files_image_type_extension", [ImageType], c_char_p,
	"""Returns the extension of an image type.

	Args:
		type: An IMAGE_TYPE_* value.

	Returns:
		The extension, as bytes.
	"""
)

files_image_get_type_from_file = lib_function (
	"files_image_get_type_from_file", [c_void_p], ImageType,
	"""Returns the type of an image by the magic bytes of an open file.

	Args:
		file: A FILE * of the C library.

	Returns:
		An IMAGE_TYPE_* value.
	"""
)

files_image_get_type = lib_function (
	"files_image_get_type", [c_char_p], ImageType,
	"""Opens a file and returns its type of image by its magic bytes.

	Args:
		filename: The path, as bytes.

	Returns:
		An IMAGE_TYPE_* value, IMAGE_TYPE_NONE if it is not an image.
	"""
)

files_image_get_type_by_extension = lib_function (
	"files_image_get_type_by_extension", [c_char_p], ImageType,
	"""Returns the type of an image by the extension of its filename.

	Args:
		filename: The filename, as bytes.

	Returns:
		An IMAGE_TYPE_* value.
	"""
)

files_image_is_jpeg = lib_function (
	"files_image_is_jpeg", [c_char_p], c_bool,
	"""Returns if a file has the magic bytes of a jpeg.

	Args:
		filename: The path, as bytes.

	Returns:
		True for a jpeg.
	"""
)

files_image_extension_is_jpeg = lib_function (
	"files_image_extension_is_jpeg", [c_char_p], c_bool,
	"""Returns if the extension of a filename is jpg or jpeg.

	Args:
		filename: The filename, as bytes.

	Returns:
		True for a jpeg extension.
	"""
)

files_image_is_png = lib_function (
	"files_image_is_png", [c_char_p], c_bool,
	"""Returns if a file has the magic bytes of a png.

	Args:
		filename: The path, as bytes.

	Returns:
		True for a png.
	"""
)

files_image_extension_is_png = lib_function (
	"files_image_extension_is_png", [c_char_p], c_bool,
	"""Returns if the extension of a filename is png.

	Args:
		filename: The filename, as bytes.

	Returns:
		True for a png extension.
	"""
)

# send
class FileHeader (Structure):
	"""The header that goes before the contents of a file in a connection, ``FileHeader``.

	Attributes:
		filename: The name of the file, NUL terminated.
		len: The size of the file in bytes.
	"""

	_fields_ = [
		("filename", c_char * FILENAME_DEFAULT_SIZE),
		("len", c_uint64)
	]

FileHeaderPointer: TypeAlias = POINTER (FileHeader) # type: ignore

file_header_is_valid = lib_function (
	"file_header_is_valid", [FileHeaderPointer], c_bool,
	"""Returns if a FileHeader can be used: a NUL terminated single name that is not "." or "..".

	Args:
		file_header: The FileHeader.

	Returns:
		True if it is valid.
	"""
)

file_header_get = lib_function (
	"file_header_get", [c_void_p, FileHeaderPointer], c_bool,
	"""Decodes the FileHeader object of a packet and validates it.

	Args:
		packet: The Packet.
		file_header: The FileHeader that gets the values.

	Returns:
		True if the packet has a valid header.
	"""
)

file_send = lib_function (
	"file_send", [c_void_p, c_void_p, c_void_p, c_char_p], c_ssize_t,
	"""Sends a file to a connection: its FileHeader in a packet, then its contents.

	Args:
		cerver: The cerver.
		client: The client.
		connection: The connection.
		filename: The path, as bytes.

	Returns:
		The bytes that were sent, -1 on error.
	"""
)

file_send_by_fd = lib_function (
	"file_send_by_fd", [c_void_p, c_void_p, c_void_p, c_int, c_char_p, c_size_t], c_ssize_t,
	"""Sends an open file to a connection: its FileHeader in a packet, then its contents.

	Args:
		cerver: The cerver.
		client: The client.
		connection: The connection.
		file_fd: The descriptor of the open file.
		actual_filename: The name of the file in the FileHeader, as bytes.
		filelen: The size of the file.

	Returns:
		The bytes that were sent, -1 on error.
	"""
)
