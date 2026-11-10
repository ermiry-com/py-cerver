"""The threads, mutexes and conditions of cerver."""

from ctypes import CFUNCTYPE, POINTER
from ctypes import c_uint, c_ulong, c_void_p, c_char_p
from typing import TypeAlias

from ..lib import lib_function, lib_c_string

__all__ = [
	"THREAD_OK", "THREAD_NAME_BUFFER_SIZE",
	"ThreadWork", "ThreadId",
	"thread_create_joinable", "thread_create_detachable", "thread_create_detached",
	"thread_set_name_variadic", "thread_set_name",
	"thread_mutex_new", "thread_mutex_delete", "thread_mutex_lock", "thread_mutex_unlock",
	"thread_cond_new", "thread_cond_delete"
]

THREAD_OK = 0
THREAD_NAME_BUFFER_SIZE = 64

# the format that sets a name as it is
THREAD_NAME_FORMAT = b"%s"

# void *(*) (void *), the work of a thread
ThreadWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

# pthread_t in linux
ThreadId: TypeAlias = c_ulong # type: ignore

thread_create_joinable = lib_function (
	"thread_create_joinable", [POINTER (ThreadId), c_void_p, c_void_p], c_uint,
	"""Creates a joinable thread, that must be joined with pthread_join ().

	Every thread that cerver creates blocks SIGINT and SIGTERM, so the signals of the
	process are delivered to the main thread.

	Args:
		thread: A pointer to a ThreadId that gets the thread.
		work: A ThreadWork kept by the caller.
		args: The argument of the work.

	Returns:
		0 on success, 1 on error.
	"""
)

thread_create_detachable = lib_function (
	"thread_create_detachable", [POINTER (ThreadId), c_void_p, c_void_p], c_uint,
	"""Creates a detached thread, that goes away on its own when its work returns.

	Args:
		thread: A pointer to a ThreadId that gets the thread.
		work: A ThreadWork kept by the caller.
		args: The argument of the work.

	Returns:
		0 on success, 1 on error.
	"""
)

thread_create_detached = lib_function (
	"thread_create_detached", [c_void_p, c_void_p], ThreadId,
	"""Creates a detached thread.

	Args:
		work: A ThreadWork kept by the caller.
		args: The argument of the work.

	Returns:
		The thread.
	"""
)

thread_set_name_variadic = lib_function (
	"thread_set_name", None, c_uint,
	"""Sets the name of the calling thread with a printf format (variadic).

	Args:
		name: The format, as bytes, followed by its arguments.

	Returns:
		0 on success, 1 on error.
	"""
)

def thread_set_name (name: str | bytes) -> int:
	"""Sets the name of the calling thread.

	Args:
		name: The name, up to THREAD_NAME_BUFFER_SIZE bytes.

	Returns:
		0 on success, 1 on error.
	"""
	return thread_set_name_variadic (c_char_p (THREAD_NAME_FORMAT), c_char_p (lib_c_string (name)))

thread_mutex_new = lib_function (
	"thread_mutex_new", [], c_void_p,
	"""Allocates and initializes a mutex.

	Returns:
		The mutex, released with thread_mutex_delete ().
	"""
)

thread_mutex_delete = lib_function (
	"thread_mutex_delete", [c_void_p], None,
	"""Destroys and releases a mutex.

	Args:
		mutex: The mutex.
	"""
)

thread_mutex_lock = lib_function (
	"thread_mutex_lock", [c_void_p], None,
	"""Locks a mutex.

	Args:
		mutex: The mutex.
	"""
)

thread_mutex_unlock = lib_function (
	"thread_mutex_unlock", [c_void_p], None,
	"""Unlocks a mutex.

	Args:
		mutex: The mutex.
	"""
)

thread_cond_new = lib_function (
	"thread_cond_new", [], c_void_p,
	"""Allocates and initializes a condition.

	Returns:
		The condition, released with thread_cond_delete ().
	"""
)

thread_cond_delete = lib_function (
	"thread_cond_delete", [c_void_p], None,
	"""Destroys and releases a condition.

	Args:
		cond: The condition.
	"""
)
