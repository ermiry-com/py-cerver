"""The sockets of the connections and the sends with a deadline."""

from ctypes import POINTER, Structure
from ctypes import c_int, c_long, c_bool, c_uint8, c_size_t, c_void_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"SOCKET_MILLISECONDS_PER_SECOND", "SOCKET_NANOSECONDS_PER_MILLISECOND",
	"Timespec", "TimespecPointer",
	"socket_new", "socket_delete", "socket_reference", "socket_create_empty", "socket_create",
	"socket_deadline_create", "socket_deadline_remaining",
	"socket_wait_writable", "socket_send_can_retry",
	"socket_send_vector", "socket_send_buffer", "socket_send_file"
]

SOCKET_MILLISECONDS_PER_SECOND = 1000
SOCKET_NANOSECONDS_PER_MILLISECOND = 1000000

class Timespec (Structure):
	"""A ``struct timespec``.

	Attributes:
		tv_sec: The seconds.
		tv_nsec: The nanoseconds.
	"""

	_fields_ = [
		("tv_sec", c_long),
		("tv_nsec", c_long)
	]

TimespecPointer: TypeAlias = POINTER (Timespec) # type: ignore

socket_new = lib_function (
	"socket_new", [], c_void_p,
	"""Allocates an empty socket.

	Returns:
		The Socket, released with socket_delete ().
	"""
)

socket_delete = lib_function (
	"socket_delete", [c_void_p], None,
	"""Releases a reference to a socket, it is deleted with the last one.

	Args:
		socket_ptr: The Socket.
	"""
)

socket_reference = lib_function (
	"socket_reference", [c_void_p], c_void_p,
	"""Takes a new reference to a socket, that must be released with socket_delete ().

	Args:
		socket: The Socket.

	Returns:
		The same socket.
	"""
)

socket_create_empty = lib_function (
	"socket_create_empty", [], c_void_p,
	"""Creates a socket without a descriptor.

	Returns:
		The Socket, released with socket_delete ().
	"""
)

socket_create = lib_function (
	"socket_create", [c_int], c_void_p,
	"""Creates a socket for a descriptor.

	Args:
		fd: The descriptor.

	Returns:
		The Socket, released with socket_delete ().
	"""
)

socket_deadline_create = lib_function (
	"socket_deadline_create", [TimespecPointer, c_long], None,
	"""Sets the deadline of a send to a timeout from now (CLOCK_MONOTONIC).

	Args:
		deadline: The Timespec that gets the deadline.
		timeout: The timeout in seconds, 0 uses CERVER_DEFAULT_SEND_TIMEOUT.
	"""
)

socket_deadline_remaining = lib_function (
	"socket_deadline_remaining", [TimespecPointer], c_int,
	"""Returns the milliseconds that are left until a deadline.

	Args:
		deadline: The Timespec.

	Returns:
		The milliseconds, 0 if it expired.
	"""
)

socket_wait_writable = lib_function (
	"socket_wait_writable", [c_int, TimespecPointer], c_bool,
	"""Waits until a full non blocking socket can be written again.

	Args:
		sock_fd: The socket.
		deadline: The Timespec of the deadline.

	Returns:
		True if it can be written before the deadline.
	"""
)

socket_send_can_retry = lib_function (
	"socket_send_can_retry", [c_int, c_int, TimespecPointer], c_bool,
	"""Returns if a failed send can be retried.

	An interrupted send is always retried, and a full non blocking socket (EAGAIN) when it
	can be written before the deadline.

	Args:
		sock_fd: The socket.
		error: The errno of the send.
		deadline: The Timespec of the deadline.

	Returns:
		True if it can be retried.
	"""
)

socket_send_vector = lib_function (
	"socket_send_vector",
	[c_void_p, c_void_p, c_int, c_int, c_long, POINTER (c_size_t), POINTER (c_int)],
	c_uint8,
	"""Sends every part of a vector with MSG_NOSIGNAL, like writev ().

	The write mutex of the socket must be held by the caller, and the parts are changed to
	skip what was sent.

	Args:
		socket: The Socket.
		parts: An array of struct iovec.
		n_parts: The number of parts.
		flags: The flags of sendmsg ().
		timeout: The seconds to wait for a full socket, 0 for the default.
		sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		error: A pointer to a c_int that gets the errno of a failure, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

socket_send_buffer = lib_function (
	"socket_send_buffer",
	[c_void_p, c_void_p, c_size_t, c_int, c_long, POINTER (c_size_t), POINTER (c_int)],
	c_uint8,
	"""Works like socket_send_vector () with a single buffer.

	Args:
		socket: The Socket.
		buffer: The bytes to send.
		size: Their size.
		flags: The flags of sendmsg ().
		timeout: The seconds to wait for a full socket, 0 for the default.
		sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		error: A pointer to a c_int that gets the errno of a failure, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

socket_send_file = lib_function (
	"socket_send_file",
	[c_void_p, c_int, c_size_t, c_long, POINTER (c_size_t), POINTER (c_int)],
	c_uint8,
	"""Sends the bytes of a file with sendfile () from its current offset.

	The write mutex of the socket must be held by the caller.

	Args:
		socket: The Socket.
		file_fd: The descriptor of the file.
		size: The bytes to send.
		timeout: The seconds to wait for a full socket, 0 for the default.
		sent: A pointer to a c_size_t that gets the bytes that were sent, or None.
		error: A pointer to a c_int that gets the errno of a failure, or None.

	Returns:
		0 on success, 1 on error.
	"""
)
