"""Workers: a thread that takes its jobs from a queue, alone or shared with other workers."""

from ctypes import CFUNCTYPE, c_void_p, py_object
from ctypes import c_int, c_uint, c_uint64, c_char_p
from typing import TypeAlias

from ..lib import lib_function

from .threads import thread_mutex_new, thread_mutex_delete
from .threads import thread_mutex_lock, thread_mutex_unlock

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

@CFUNCTYPE (None, py_object)
def worker_remove_reference (worker):
	worker.queue.pop (0)

class Worker ():
	def __init__ (self, name, work):
		self.worker = worker_create ()
		worker_set_reference (self.worker, self)
		worker_set_name (self.worker, name.encode ("utf-8"))
		worker_set_work (self.worker, work)
		worker_set_remove_reference (self.worker, worker_remove_reference)

		self.queue = []

		self.mutex = thread_mutex_new ()

	def __del__ (self):
		# correctly end internal queue
		self.end ()
		worker_delete (self.worker)

		# remove all saved references
		self.queue.clear ()

		thread_mutex_delete (self.mutex)

	def start_with_state (self, worker_state):
		return worker_start_with_state (self.worker, worker_state)

	def start (self):
		return worker_start (self.worker)

	def resume (self):
		return worker_resume (self.worker)

	def stop (self):
		return worker_stop (self.worker)

	def push (self, data):
		result = None

		thread_mutex_lock (self.mutex)

		# safely insert object reference into local queue
		self.queue.append (data)

		# process data using internal queue
		result = worker_push_job (self.worker, data)

		thread_mutex_unlock (self.mutex)

		return result

	def end (self):
		return worker_end (self.worker)
