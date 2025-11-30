"""A worker manager: workers that share a queue, added while jobs wait and removed when idle."""

import threading

from ctypes import POINTER, Structure, byref
from ctypes import c_int, c_uint, c_uint32, c_uint64, c_char_p, c_void_p
from typing import Any, Callable, TypeAlias

from ..callbacks import callback_wrap
from ..lib import lib_function, lib_c_string

from .jobs import JobMethod, JobQueueStats, JOB_QUEUE_PRIORITY_NORMAL

__all__ = [
	"WORKER_MANAGER_NAME_SIZE", "WORKER_MANAGER_MAX_WORKERS",
	"WORKER_MANAGER_DEFAULT_MIN_WORKERS", "WORKER_MANAGER_DEFAULT_MAX_WORKERS",
	"WORKER_MANAGER_DEFAULT_SCALE_UP_WAIT", "WORKER_MANAGER_DEFAULT_IDLE_TIMEOUT",
	"WORKER_MANAGER_DEFAULT_CHECK_INTERVAL",
	"WorkerManagerStats", "WorkerManagerStatsPointer",
	"worker_manager_create", "worker_manager_delete",
	"worker_manager_set_limits", "worker_manager_set_scaling", "worker_manager_set_work",
	"worker_manager_start", "worker_manager_stop", "worker_manager_resume", "worker_manager_end",
	"worker_manager_push_job", "worker_manager_push_job_priority",
	"worker_manager_get_n_workers", "worker_manager_get_states", "worker_manager_get_stats",
	"WorkerManager"
]

WORKER_MANAGER_NAME_SIZE = 64

# the most workers that a manager can have
WORKER_MANAGER_MAX_WORKERS = 256

WORKER_MANAGER_DEFAULT_MIN_WORKERS = 1
WORKER_MANAGER_DEFAULT_MAX_WORKERS = 8

# a job that waits this long (ms) without a free worker makes the manager add one
WORKER_MANAGER_DEFAULT_SCALE_UP_WAIT = 64

# a worker without a job for this long (ms) is removed, down to the minimum
WORKER_MANAGER_DEFAULT_IDLE_TIMEOUT = 4096

# how often (ms) the manager checks its workers when nothing wakes it up
WORKER_MANAGER_DEFAULT_CHECK_INTERVAL = 128

class WorkerManagerStats (Structure):
	"""The stats of a worker manager, ``WorkerManagerStats``.

	Attributes:
		workers: The workers that the manager has now.
		available: Workers without a job.
		working: Workers running a job.
		stopped: Workers that were stopped.
		created_workers: Workers that were added, the first ones too.
		removed_workers: Idle workers that were removed.
		max_workers: The most workers that it had at the same time.
		queue: The JobQueueStats of the queue of the workers.
	"""

	_fields_ = [
		("workers", c_uint),
		("available", c_uint),
		("working", c_uint),
		("stopped", c_uint),
		("created_workers", c_uint64),
		("removed_workers", c_uint64),
		("max_workers", c_uint),
		("queue", JobQueueStats)
	]

WorkerManagerStatsPointer: TypeAlias = POINTER (WorkerManagerStats) # type: ignore

worker_manager_create = lib_function (
	"worker_manager_create", [c_char_p], c_void_p,
	"""Creates a worker manager with a queue of JOB_QUEUE_DEFAULT_PRIORITIES priorities.

	Args:
		name: The name, as bytes.

	Returns:
		The WorkerManager, released with worker_manager_delete ().
	"""
)

worker_manager_delete = lib_function (
	"worker_manager_delete", [c_void_p], None,
	"""Ends the manager if it is running and deletes it with its workers and its queue.

	Args:
		manager: The manager, it must not be used after this call.
	"""
)

worker_manager_set_limits = lib_function (
	"worker_manager_set_limits", [c_void_p, c_uint, c_uint], c_uint,
	"""Sets the least and the most workers, before the start.

	Args:
		manager: The manager.
		min_workers: 1 to WORKER_MANAGER_MAX_WORKERS.
		max_workers: min_workers to WORKER_MANAGER_MAX_WORKERS.

	Returns:
		0 on success, 1 if the limits are not valid.
	"""
)

worker_manager_set_scaling = lib_function (
	"worker_manager_set_scaling", [c_void_p, c_uint32, c_uint32], None,
	"""Sets when the manager adds a worker and when it removes one.

	Args:
		manager: The manager.
		scale_up_wait: A job that waits these ms without a free worker adds one.
		idle_timeout: A worker without a job for these ms is removed.
	"""
)

worker_manager_set_work = lib_function (
	"worker_manager_set_work", [c_void_p, c_void_p], None,
	"""Sets the work of the jobs that are pushed without one.

	Args:
		manager: The manager.
		work: A JobMethod kept by the caller.
	"""
)

worker_manager_start = lib_function (
	"worker_manager_start", [c_void_p], c_uint,
	"""Starts the minimum workers and the thread that scales them.

	Args:
		manager: The manager.

	Returns:
		0 on success, 1 on error.
	"""
)

worker_manager_stop = lib_function (
	"worker_manager_stop", [c_void_p], c_uint,
	"""Stops every worker after its job, the jobs stay in the queue.

	Args:
		manager: The manager.

	Returns:
		0 on success, 1 if it was not running.
	"""
)

worker_manager_resume = lib_function (
	"worker_manager_resume", [c_void_p], c_uint,
	"""Lets the stopped workers take jobs again.

	Args:
		manager: The manager.

	Returns:
		0 on success, 1 if it was not stopped.
	"""
)

worker_manager_end = lib_function (
	"worker_manager_end", [c_void_p], c_uint,
	"""Ends the scaling thread and every worker after its job.

	Args:
		manager: The manager.

	Returns:
		0 on success, 1 if it was not running.
	"""
)

worker_manager_push_job = lib_function (
	"worker_manager_push_job", [c_void_p, c_void_p, c_void_p], c_uint,
	"""Pushes a job with the default priority.

	Args:
		manager: The manager.
		work: A JobMethod kept by the caller, None for the work of the manager.
		args: The argument of the work.

	Returns:
		0 on success, 1 on error.
	"""
)

worker_manager_push_job_priority = lib_function (
	"worker_manager_push_job_priority", [c_void_p, c_void_p, c_void_p, c_uint], c_uint,
	"""Pushes a job with a priority.

	Args:
		manager: The manager.
		work: A JobMethod kept by the caller, None for the work of the manager.
		args: The argument of the work.
		priority: 0 is the highest one.

	Returns:
		0 on success, 1 on error.
	"""
)

worker_manager_get_n_workers = lib_function (
	"worker_manager_get_n_workers", [c_void_p], c_uint,
	"""Returns how many workers the manager has now.

	Args:
		manager: The manager.

	Returns:
		The number of workers.
	"""
)

worker_manager_get_states = lib_function (
	"worker_manager_get_states", [c_void_p, POINTER (c_int), c_uint], c_uint,
	"""Copies the state of each worker.

	Args:
		manager: The manager.
		states: An array of c_int that gets the WORKER_STATE_* values.
		max_states: The size of the array.

	Returns:
		How many states were copied.
	"""
)

worker_manager_get_stats = lib_function (
	"worker_manager_get_stats", [c_void_p, WorkerManagerStatsPointer], None,
	"""Copies the stats of the manager and of its queue.

	Args:
		manager: The manager.
		stats: The WorkerManagerStats that gets them.
	"""
)

class WorkerManager:
	"""Workers that run Python jobs from a shared queue, scaled between a minimum and a maximum.

	Each job is a Python object given to the work of the manager, and it is kept until it ran.

	Example:
		manager = WorkerManager ("reports", build_report, min_workers=1, max_workers=4)
		manager.start ()
		manager.push ({"id": report_id})
		...
		manager.delete ()

	Attributes:
		manager: The C worker manager.
	"""

	def __init__ (
		self, name: str, work: Callable [[Any], None],
		min_workers: int = WORKER_MANAGER_DEFAULT_MIN_WORKERS,
		max_workers: int = WORKER_MANAGER_DEFAULT_MAX_WORKERS,
		scale_up_wait: int = WORKER_MANAGER_DEFAULT_SCALE_UP_WAIT,
		idle_timeout: int = WORKER_MANAGER_DEFAULT_IDLE_TIMEOUT
	):
		"""Creates the manager.

		Args:
			name: The name of the manager.
			work: Called with the object of each job, from the threads of the workers.
			min_workers: The least workers.
			max_workers: The most workers.
			scale_up_wait: A job that waits these ms without a free worker adds one.
			idle_timeout: A worker without a job for these ms is removed.

		Raises:
			RuntimeError: If cerver could not create the manager.
			ValueError: If the limits are not valid.
		"""
		self.manager = worker_manager_create (lib_c_string (name))
		if (not self.manager):
			raise RuntimeError ("Failed to create the worker manager")

		if (worker_manager_set_limits (self.manager, min_workers, max_workers)):
			worker_manager_delete (self.manager)
			self.manager = None
			raise ValueError (f"Invalid worker limits {min_workers} - {max_workers}")

		worker_manager_set_scaling (self.manager, scale_up_wait, idle_timeout)

		# the objects of the jobs by their id, released after their job ran
		self.jobs = {}
		self.lock = threading.Lock ()
		self.next_id = 0

		self.method = work
		self.work = callback_wrap (self.job_run, JobMethod)

	def job_run (self, job_id: int) -> None:
		"""Runs the work with the object of a job, from the thread of a worker."""
		with self.lock:
			data = self.jobs.pop (job_id, None)

		self.method (data)

	def push (self, data: Any, priority: int = JOB_QUEUE_PRIORITY_NORMAL) -> int:
		"""Pushes a job with an object for the work.

		Args:
			data: Any Python object, it is kept until the job ran.
			priority: 0 is the highest one.

		Returns:
			0 on success, 1 on error.
		"""
		with self.lock:
			self.next_id += 1
			job_id = self.next_id
			self.jobs[job_id] = data

		result = worker_manager_push_job_priority (self.manager, self.work, job_id, priority)
		if (result):
			with self.lock:
				self.jobs.pop (job_id, None)

		return result

	def start (self) -> int:
		"""Starts the minimum workers and the thread that scales them.

		Returns:
			0 on success, 1 on error.
		"""
		return worker_manager_start (self.manager)

	def stop (self) -> int:
		"""Stops every worker after its job, the jobs stay in the queue.

		Returns:
			0 on success, 1 if it was not running.
		"""
		return worker_manager_stop (self.manager)

	def resume (self) -> int:
		"""Lets the stopped workers take jobs again.

		Returns:
			0 on success, 1 if it was not stopped.
		"""
		return worker_manager_resume (self.manager)

	def end (self) -> int:
		"""Ends the scaling thread and every worker after its job.

		Returns:
			0 on success, 1 if it was not running.
		"""
		return worker_manager_end (self.manager)

	def workers (self) -> int:
		"""Returns how many workers the manager has now."""
		return worker_manager_get_n_workers (self.manager)

	def states (self) -> list:
		"""Returns the WORKER_STATE_* value of each worker."""
		states = (c_int * WORKER_MANAGER_MAX_WORKERS) ()
		count = worker_manager_get_states (self.manager, states, WORKER_MANAGER_MAX_WORKERS)
		return list (states[:count])

	def stats (self) -> dict:
		"""Returns the stats of the manager and of its queue."""
		stats = WorkerManagerStats ()
		worker_manager_get_stats (self.manager, byref (stats))

		return {
			"workers": stats.workers,
			"available": stats.available,
			"working": stats.working,
			"stopped": stats.stopped,
			"created_workers": stats.created_workers,
			"removed_workers": stats.removed_workers,
			"max_workers": stats.max_workers,
			"queued_jobs": stats.queue.total_jobs - stats.queue.pulled_jobs,
			"completed_jobs": stats.queue.completed_jobs
		}

	def delete (self) -> None:
		"""Ends the manager and releases it, it must not be used after this call."""
		if (self.manager):
			worker_manager_delete (self.manager)
			self.manager = None

			with self.lock:
				self.jobs.clear ()
