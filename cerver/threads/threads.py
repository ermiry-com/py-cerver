"""The threads, mutexes and conditions of cerver."""

from ctypes import CFUNCTYPE
from ctypes import c_ulong, c_void_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"ThreadWork", "ThreadId",
	"thread_create_detached",
	"thread_mutex_new", "thread_mutex_delete", "thread_mutex_lock", "thread_mutex_unlock",
	"thread_cond_new", "thread_cond_delete"
]

# void *(*) (void *), the work of a thread
ThreadWork: TypeAlias = CFUNCTYPE (c_void_p, c_void_p) # type: ignore

# pthread_t in linux
ThreadId: TypeAlias = c_ulong # type: ignore

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
