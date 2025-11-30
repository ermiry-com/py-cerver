"""Workers: a thread that takes its jobs from a queue, alone or shared with other workers."""

import threading

from ctypes import CFUNCTYPE, c_void_p, py_object
from ctypes import c_int, c_uint, c_uint64, c_char_p
from typing import Any, Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function, lib_c_string

__all__ = [
	"WORKER_NAME_SIZE",
	"WorkerState",
	"WORKER_STATE_NONE", "WORKER_STATE_AVAILABLE", "WORKER_STATE_WORKING",
	"WORKER_STATE_STOPPED", "WORKER_STATE_ENDED",
	"WorkerMethod", "WorkerDataDelete", "WorkerRemoveReference",
	"worker_state_to_string",
	"worker_delete", "worker_create", "worker_create_with_id", "worker_create_with_queue",
	"worker_set_name", "worker_get_state", "worker_get_idle_milliseconds",
	"worker_set_work", "worker_set_delete_data",
	"worker_set_reference", "worker_set_remove_reference",
	"worker_start_with_state", "worker_start", "worker_resume", "worker_stop", "worker_end",
	"worker_push_job", "worker_push_job_with_work",
	"Worker"
]

WORKER_NAME_SIZE = 64

WorkerState: TypeAlias = c_int # type: ignore

WORKER_STATE_NONE = 0
WORKER_STATE_AVAILABLE = 1
WORKER_STATE_WORKING = 2
WORKER_STATE_STOPPED = 3
WORKER_STATE_ENDED = 4

# void (*) (void *args), it gets the Python object of each job
WorkerMethod: TypeAlias = CFUNCTYPE (None, py_object) # type: ignore
WorkerDataDelete: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

# void (*) (const void *args), it gets the reference of the worker after each job
WorkerRemoveReference: TypeAlias = CFUNCTYPE (None, py_object) # type: ignore

worker_state_to_string = lib_function (
	"worker_state_to_string", [WorkerState], c_char_p,
	"""Returns the name of a worker state.

	Args:
		state: A WORKER_STATE_* value.

	Returns:
		The name, as bytes.
	"""
)

worker_delete = lib_function (
	"worker_delete", [c_void_p], None,
	"""Ends a worker if it is running and deletes it.

	Args:
		worker_ptr: The worker, it must not be used after this call.
	"""
)

worker_create = lib_function (
	"worker_create", [], c_void_p,
	"""Creates a worker with its own queue.

	Returns:
		The worker, released with worker_delete ().
	"""
)

worker_create_with_id = lib_function (
	"worker_create_with_id", [c_uint], c_void_p,
	"""Creates a worker with an id and its own queue.

	Args:
		id: The id.

	Returns:
		The worker, released with worker_delete ().
	"""
)

worker_create_with_queue = lib_function (
	"worker_create_with_queue", [c_uint, c_void_p], c_void_p,
	"""Creates a worker that takes its jobs from a queue that it shares with other workers.

	Args:
		id: The id.
		job_queue: The JobQueue, it is not deleted with the worker.

	Returns:
		The worker, released with worker_delete ().
	"""
)

worker_set_name = lib_function (
	"worker_set_name", [c_void_p, c_char_p], None,
	"""Sets the name of the worker, used in the name of its thread.

	Args:
		worker: The worker.
		name: The name, as bytes, up to WORKER_NAME_SIZE bytes.
	"""
)

worker_get_state = lib_function (
	"worker_get_state", [c_void_p], WorkerState,
	"""Returns the state of the worker.

	Args:
		worker: The worker.

	Returns:
		A WORKER_STATE_* value.
	"""
)

worker_get_idle_milliseconds = lib_function (
	"worker_get_idle_milliseconds", [c_void_p], c_uint64,
	"""Returns the milliseconds that an available worker has been without a job.

	Args:
		worker: The worker.

	Returns:
		The milliseconds, 0 if it is not available.
	"""
)

worker_set_work = lib_function (
	"worker_set_work", [c_void_p, c_void_p], None,
	"""Sets the work that runs with the jobs that are pushed without one.

	Args:
		worker: The worker.
		work: A WorkerMethod kept by the caller.
	"""
)

worker_set_delete_data = lib_function (
	"worker_set_delete_data", [c_void_p, c_void_p], None,
	"""Sets how the data of the jobs that are still queued is released when the worker ends.

	Args:
		worker: The worker.
		delete_data: A WorkerDataDelete kept by the caller, or None.
	"""
)

worker_set_reference = lib_function (
	"worker_set_reference", [c_void_p, py_object], None,
	"""Sets the reference that the remove reference method gets after each job.

	Args:
		worker: The worker.
		reference: A Python object, kept alive by the caller.
	"""
)

worker_set_remove_reference = lib_function (
	"worker_set_remove_reference", [c_void_p, c_void_p], None,
	"""Sets the method that runs with the reference of the worker after each job.

	Args:
		worker: The worker.
		remove_reference: A WorkerRemoveReference kept by the caller.
	"""
)

worker_start_with_state = lib_function (
	"worker_start_with_state", [c_void_p, WorkerState], c_uint,
	"""Starts the thread of the worker in a state.

	Args:
		worker: The worker.
		worker_state: WORKER_STATE_AVAILABLE or WORKER_STATE_STOPPED.

	Returns:
		0 on success, 1 on error.
	"""
)

worker_start = lib_function (
	"worker_start", [c_void_p], c_uint,
	"""Starts the thread of the worker, available to take jobs.

	Args:
		worker: The worker.

	Returns:
		0 on success, 1 on error.
	"""
)

worker_resume = lib_function (
	"worker_resume", [c_void_p], c_uint,
	"""Lets a stopped worker take jobs again.

	Args:
		worker: The worker.

	Returns:
		0 on success, 1 if it was not stopped.
	"""
)

worker_stop = lib_function (
	"worker_stop", [c_void_p], c_uint,
	"""Waits until the worker ends its current job and stops it.

	Args:
		worker: The worker.

	Returns:
		0 on success, 1 if it was not running.
	"""
)

worker_end = lib_function (
	"worker_end", [c_void_p], c_uint,
	"""Waits until the worker ends its current job and joins its thread.

	Args:
		worker: The worker.

	Returns:
		0 on success, 1 if it was not running.
	"""
)

worker_push_job = lib_function (
	"worker_push_job", [c_void_p, py_object], c_uint,
	"""Pushes a job for the work of the worker.

	Args:
		worker: The worker.
		args: The Python object that the work gets, kept alive by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

worker_push_job_with_work = lib_function (
	"worker_push_job_with_work", [c_void_p, c_void_p, py_object], c_uint,
	"""Pushes a job with its own work.

	Args:
		worker: The worker.
		work: A WorkerMethod kept by the caller.
		args: The Python object that the work gets, kept alive by the caller.

	Returns:
		0 on success, 1 on error.
	"""
)

class Worker:
	"""A worker with a Python work, that keeps every object of a job until it ran.

	Example:
		worker = Worker ("images", process_image)
		worker.start ()
		worker.push ({"path": path})
		...
		worker.delete ()

	Attributes:
		worker: The C worker.
	"""

	def __init__ (self, name: str, work: Callable [[Any], None]):
		"""Creates the worker.

		Args:
			name: The name of the worker.
			work: A Python function (or a WorkerMethod) that gets the object of each job.

		Raises:
			RuntimeError: If cerver could not create the worker.
		"""
		self.worker = worker_create ()
		if (not self.worker):
			raise RuntimeError ("Failed to create the worker")

		self.queue = []
		self.lock = threading.Lock ()

		self.work = callback_wrap (work, WorkerMethod)
		self.remove_reference = callback_wrap (self.job_done, WorkerRemoveReference)

		worker_set_reference (self.worker, self)
		worker_set_name (self.worker, lib_c_string (name))
		worker_set_work (self.worker, self.work)
		worker_set_remove_reference (self.worker, self.remove_reference)

	@staticmethod
	def job_done (worker: "Worker") -> None:
		"""Releases the object of the job that ran, called from the thread of the worker."""
		with worker.lock:
			if (worker.queue):
				worker.queue.pop (0)

	def start_with_state (self, worker_state: int) -> int:
		"""Starts the thread of the worker in a state.

		Args:
			worker_state: WORKER_STATE_AVAILABLE or WORKER_STATE_STOPPED.

		Returns:
			0 on success, 1 on error.
		"""
		return worker_start_with_state (self.worker, worker_state)

	def start (self) -> int:
		"""Starts the thread of the worker.

		Returns:
			0 on success, 1 on error.
		"""
		return worker_start (self.worker)

	def resume (self) -> int:
		"""Lets a stopped worker take jobs again.

		Returns:
			0 on success, 1 if it was not stopped.
		"""
		return worker_resume (self.worker)

	def stop (self) -> int:
		"""Stops the worker after its current job.

		Returns:
			0 on success, 1 if it was not running.
		"""
		return worker_stop (self.worker)

	def state (self) -> int:
		"""Returns the state of the worker.

		Returns:
			A WORKER_STATE_* value.
		"""
		return worker_get_state (self.worker)

	def push (self, data: Any) -> int:
		"""Pushes a job with an object for the work.

		Args:
			data: Any Python object, it is kept until the job ran.

		Returns:
			0 on success, 1 on error.
		"""
		with self.lock:
			self.queue.append (data)

			result = worker_push_job (self.worker, data)
			if (result):
				self.queue.pop ()

		return result

	def end (self) -> int:
		"""Ends the worker after its current job and joins its thread.

		Returns:
			0 on success, 1 if it was not running.
		"""
		return worker_end (self.worker)

	def delete (self) -> None:
		"""Ends the worker and releases it, it must not be used after this call."""
		if (self.worker):
			worker_delete (self.worker)
			self.worker = None

			with self.lock:
				self.queue.clear ()
