"""A binary semaphore."""

from ctypes import c_int, c_void_p

from ..lib import lib_function

__all__ = [
	"bsem_new", "bsem_delete", "bsem_init", "bsem_reset",
	"bsem_post", "bsem_post_all", "bsem_wait"
]

bsem_new = lib_function (
	"bsem_new", [], c_void_p,
	"""Allocates a binary semaphore.

	Returns:
		The semaphore, released with bsem_delete ().
	"""
)

bsem_delete = lib_function (
	"bsem_delete", [c_void_p], None,
	"""Releases a binary semaphore.

	Args:
		bsem_ptr: The semaphore.
	"""
)

bsem_init = lib_function (
	"bsem_init", [c_void_p, c_int], None,
	"""Initializes a semaphore.

	Args:
		bsem_p: The semaphore.
		value: 0 or 1.
	"""
)

bsem_reset = lib_function (
	"bsem_reset", [c_void_p], None,
	"""Resets a semaphore to 0.

	Args:
		bsem_p: The semaphore.
	"""
)

bsem_post = lib_function (
	"bsem_post", [c_void_p], None,
	"""Posts to at least one waiting thread.

	Args:
		bsem_p: The semaphore.
	"""
)

bsem_post_all = lib_function (
	"bsem_post_all", [c_void_p], None,
	"""Posts to every waiting thread.

	Args:
		bsem_p: The semaphore.
	"""
)

bsem_wait = lib_function (
	"bsem_wait", [c_void_p], None,
	"""Waits until the semaphore is posted.

	Args:
		bsem_p: The semaphore.
	"""
)
