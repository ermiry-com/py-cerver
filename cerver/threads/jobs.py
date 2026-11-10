"""Jobs, job handlers and the job queue: rings by priority with stats."""

from ctypes import CFUNCTYPE, POINTER, Structure, byref
from ctypes import c_int, c_uint, c_uint32, c_uint64, c_size_t, c_bool, c_void_p, py_object
from typing import TypeAlias

from ..lib import lib_function

from ..network.sockets import TimespecPointer

from .thpool import THPOOL_HISTOGRAM_BUCKETS

__all__ = [
	"JOB_QUEUE_POOL_INIT",
	"JOB_QUEUE_DEFAULT_PRIORITIES", "JOB_QUEUE_MAX_PRIORITIES",
	"JOB_QUEUE_PRIORITY_HIGH", "JOB_QUEUE_PRIORITY_NORMAL", "JOB_QUEUE_PRIORITY_LOW",
	"JOB_QUEUE_DEFAULT_RING_CAPACITY", "JOB_QUEUE_DEFAULT_STARVATION_LIMIT",
	"JOB_QUEUE_STARVATION_DISABLED", "JOB_QUEUE_WAIT_FOREVER",
	"JobMethod", "JobDataDelete", "JobQueueHandler", "JobQueueInterrupted",
	"Job", "JobPointer",
	"JobQueueType", "JOB_QUEUE_TYPE_NONE", "JOB_QUEUE_TYPE_JOBS", "JOB_QUEUE_TYPE_HANDLERS",
	"JobQueueStats", "JobQueueStatsPointer",
	"job_new", "job_delete", "job_comparator", "job_create", "job_get", "job_reset", "job_return",
	"job_handler_new", "job_handler_delete", "job_handler_create", "job_handler_get",
	"job_handler_reset", "job_handler_signal", "job_handler_return", "job_handler_wait",
	"job_queue_new", "job_queue_delete", "job_queue_create", "job_queue_create_with_priorities",
	"job_queue_set_handler", "job_queue_set_starvation_limit", "job_queue_default_priority",
	"job_queue_size", "job_queue_oldest_wait",
	"job_queue_push", "job_queue_push_priority", "job_queue_push_job", "job_queue_push_job_priority",
	"job_queue_push_job_with_id", "job_queue_push_handler",
	"job_queue_pull", "job_queue_pull_timeout", "job_queue_pull_interruptible",
	"job_queue_request", "job_queue_request_timeout",
	"job_queue_record_run", "job_queue_get_stats", "job_queue_stats_print",
	"job_queue_start", "job_queue_wait", "job_queue_signal", "job_queue_stop", "job_queue_clear",
	"job_queue_stats"
]

JOB_QUEUE_POOL_INIT = 16

# the priorities of a queue, 0 is the highest one
JOB_QUEUE_DEFAULT_PRIORITIES = 3
JOB_QUEUE_MAX_PRIORITIES = 16

JOB_QUEUE_PRIORITY_HIGH = 0
JOB_QUEUE_PRIORITY_NORMAL = 1
JOB_QUEUE_PRIORITY_LOW = 2

# the jobs that each priority has room for, it grows by doubling
JOB_QUEUE_DEFAULT_RING_CAPACITY = 16

# after these jobs were taken ahead of a waiting lower priority, the next one is taken from it
JOB_QUEUE_DEFAULT_STARVATION_LIMIT = 8
JOB_QUEUE_STARVATION_DISABLED = 0

# a wait without a deadline
JOB_QUEUE_WAIT_FOREVER = 0xFFFFFFFF

# void (*) (void *args), the work of a job
JobMethod: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore
JobDataDelete: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

# the handler of a JOB_QUEUE_TYPE_HANDLERS queue, it gets the data of each pushed handler
JobQueueHandler: TypeAlias = CFUNCTYPE (None, py_object) # type: ignore

# bool (*) (const void *args), true stops job_queue_pull_interruptible ()
JobQueueInterrupted: TypeAlias = CFUNCTYPE (c_bool, c_void_p) # type: ignore

class Job (Structure):
	"""A job of a queue, ``Job``.

	Attributes:
		id: The id of the job, for job_queue_request ().
		work: The address of its work.
		args: The argument of the work.
	"""

	_fields_ = [
		("id", c_uint64),
		("work", c_void_p),
		("args", c_void_p)
	]

JobPointer: TypeAlias = POINTER (Job) # type: ignore

JobQueueType: TypeAlias = c_int # type: ignore

JOB_QUEUE_TYPE_NONE = 0
JOB_QUEUE_TYPE_JOBS = 1
JOB_QUEUE_TYPE_HANDLERS = 2

class JobQueueStats (Structure):
	"""The stats of a queue, ``JobQueueStats``.

	Attributes:
		total_jobs: Jobs that entered the queue.
		pulled_jobs: Jobs that were taken from the queue.
		completed_jobs: Jobs whose work finished (job_queue_record_run ()).
		requested_jobs: Jobs given to job_queue_request () by their id.
		timed_out_waits: Waits that ended at their deadline without a job.
		promoted_jobs: Jobs taken ahead of a higher priority, so they were not starved.
		max_queued: The most jobs in the queue at the same time.
		priority_jobs: The jobs that entered each priority.
		wait_total_microseconds: The time that the jobs waited.
		run_total_microseconds: The time that the jobs ran.
		wait_histogram: The jobs that waited up to 2^i ms.
		run_histogram: The jobs that ran up to 2^i ms.
	"""

	_fields_ = [
		("total_jobs", c_uint64),
		("pulled_jobs", c_uint64),
		("completed_jobs", c_uint64),
		("requested_jobs", c_uint64),
		("timed_out_waits", c_uint64),
		("promoted_jobs", c_uint64),
		("max_queued", c_uint64),
		("priority_jobs", c_uint64 * JOB_QUEUE_MAX_PRIORITIES),
		("wait_total_microseconds", c_uint64),
		("run_total_microseconds", c_uint64),
		("wait_histogram", c_uint64 * THPOOL_HISTOGRAM_BUCKETS),
		("run_histogram", c_uint64 * THPOOL_HISTOGRAM_BUCKETS)
	]

JobQueueStatsPointer: TypeAlias = POINTER (JobQueueStats) # type: ignore

# jobs
job_new = lib_function (
	"job_new", [], JobPointer,
	"""Allocates an empty job.

	Returns:
		The Job, released with job_delete ().
	"""
)

job_delete = lib_function (
	"job_delete", [c_void_p], None,
	"""Releases a job.

	Args:
		job_ptr: The Job.
	"""
)

job_comparator = lib_function (
	"job_comparator", [c_void_p, c_void_p], c_int,
	"""Compares two jobs by their ids.

	Args:
		a: A Job.
		b: A Job.

	Returns:
		Less than, equal to or greater than 0.
	"""
)

job_create = lib_function (
	"job_create", [c_void_p, c_void_p], JobPointer,
	"""Allocates a job, job_get () takes one from the pool of a queue instead.

	Args:
		work: A JobMethod kept by the caller.
		args: The argument of the work.

	Returns:
		The Job, released with job_delete ().
	"""
)

job_get = lib_function (
	"job_get", [c_void_p], JobPointer,
	"""Takes a job from the pool of a queue, it allocates one only if the pool is empty.

	Args:
		job_queue: The queue.

	Returns:
		The Job, given back with job_return ().
	"""
)

job_reset = lib_function (
	"job_reset", [JobPointer], None,
	"""Clears the values of a job.

	Args:
		job: The Job.
	"""
)

job_return = lib_function (
	"job_return", [c_void_p, JobPointer], None,
	"""Gives a job back to the pool of a queue.

	Args:
		job_queue: The queue.
		job: The Job.
	"""
)

# handlers
job_handler_new = lib_function (
	"job_handler_new", [], c_void_p,
	"""Allocates an empty job handler.

	Returns:
		The JobHandler, released with job_handler_delete ().
	"""
)

job_handler_delete = lib_function (
	"job_handler_delete", [c_void_p], None,
	"""Releases a job handler.

	Args:
		job_handler_ptr: The JobHandler.
	"""
)

job_handler_create = lib_function (
	"job_handler_create", [], c_void_p,
	"""Creates a job handler with its synchronization values.

	Returns:
		The JobHandler, released with job_handler_delete ().
	"""
)

job_handler_get = lib_function (
	"job_handler_get", [c_void_p], c_void_p,
	"""Takes a job handler from the pool of a queue.

	Args:
		job_queue: The queue.

	Returns:
		The JobHandler, given back with job_handler_return ().
	"""
)

job_handler_reset = lib_function (
	"job_handler_reset", [c_void_p], None,
	"""Clears the values of a job handler.

	Args:
		job_handler: The JobHandler.
	"""
)

job_handler_signal = lib_function (
	"job_handler_signal", [c_void_p], None,
	"""Wakes up the thread that waits in job_handler_wait () for the job handler.

	Args:
		handler: The JobHandler.
	"""
)

job_handler_return = lib_function (
	"job_handler_return", [c_void_p, c_void_p], None,
	"""Gives a job handler back to the pool of a queue.

	Args:
		job_queue: The queue.
		job_handler: The JobHandler.
	"""
)

job_handler_wait = lib_function (
	"job_handler_wait", [c_void_p, py_object, c_void_p], None,
	"""Pushes a handler with the data to a JOB_QUEUE_TYPE_HANDLERS queue and waits until it was handled.

	Args:
		job_queue: The queue, with its JobQueueHandler.
		data: The Python object that the JobQueueHandler gets.
		data_delete: A JobDataDelete kept by the caller, or None.
	"""
)

# queue
job_queue_new = lib_function (
	"job_queue_new", [], c_void_p,
	"""Allocates an empty job queue.

	Returns:
		The JobQueue, released with job_queue_delete ().
	"""
)

job_queue_delete = lib_function (
	"job_queue_delete", [c_void_p], None,
	"""Stops a job queue, destroys its jobs and releases it.

	Args:
		job_queue_ptr: The JobQueue.
	"""
)

job_queue_create = lib_function (
	"job_queue_create", [JobQueueType], c_void_p,
	"""Creates a job queue with JOB_QUEUE_DEFAULT_PRIORITIES priorities.

	Args:
		type: JOB_QUEUE_TYPE_JOBS or JOB_QUEUE_TYPE_HANDLERS.

	Returns:
		The JobQueue, released with job_queue_delete ().
	"""
)

job_queue_create_with_priorities = lib_function (
	"job_queue_create_with_priorities", [JobQueueType, c_uint], c_void_p,
	"""Creates a job queue with a number of priorities.

	Args:
		type: JOB_QUEUE_TYPE_JOBS or JOB_QUEUE_TYPE_HANDLERS.
		n_priorities: 1 to JOB_QUEUE_MAX_PRIORITIES.

	Returns:
		The JobQueue, released with job_queue_delete ().
	"""
)

job_queue_set_handler = lib_function (
	"job_queue_set_handler", [c_void_p, c_void_p], None,
	"""Sets the method that the thread of the queue runs with each job.

	Args:
		queue: The queue.
		handler: A JobQueueHandler kept by the caller.
	"""
)

job_queue_set_starvation_limit = lib_function (
	"job_queue_set_starvation_limit", [c_void_p, c_uint], None,
	"""Sets how many jobs can be taken ahead of a waiting job of a lower priority before it is taken.

	Args:
		job_queue: The queue.
		limit: The number of jobs, JOB_QUEUE_STARVATION_DISABLED always takes the highest priority.
	"""
)

job_queue_default_priority = lib_function (
	"job_queue_default_priority", [c_void_p], c_uint,
	"""Returns the priority that job_queue_push () uses, the one in the middle.

	Args:
		job_queue: The queue.

	Returns:
		The priority.
	"""
)

job_queue_size = lib_function (
	"job_queue_size", [c_void_p], c_size_t,
	"""Returns how many jobs are in the queue.

	Args:
		job_queue: The queue.

	Returns:
		The number of jobs.
	"""
)

job_queue_oldest_wait = lib_function (
	"job_queue_oldest_wait", [c_void_p], c_uint64,
	"""Returns the milliseconds that the oldest job in the queue has waited.

	Args:
		job_queue: The queue.

	Returns:
		The milliseconds, 0 if it is empty.
	"""
)

job_queue_push = lib_function (
	"job_queue_push", [c_void_p, c_void_p], c_uint,
	"""Adds a job to the queue with the default priority.

	Args:
		job_queue: The queue.
		job_ptr: The Job, or the JobHandler of a handlers queue.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_push_priority = lib_function (
	"job_queue_push_priority", [c_void_p, c_void_p, c_uint], c_uint,
	"""Adds a job to the queue with a priority.

	Args:
		job_queue: The queue.
		job_ptr: The Job.
		priority: 0 is the highest one, one that does not exist is the lowest one.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_push_job = lib_function (
	"job_queue_push_job", [c_void_p, c_void_p, c_void_p], c_uint,
	"""Creates a job and adds it to the queue with the default priority.

	Args:
		job_queue: The queue.
		work: A JobMethod kept by the caller.
		args: The argument of the work.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_push_job_priority = lib_function (
	"job_queue_push_job_priority", [c_void_p, c_void_p, c_void_p, c_uint], c_uint,
	"""Creates a job and adds it to the queue with a priority.

	Args:
		job_queue: The queue.
		work: A JobMethod kept by the caller.
		args: The argument of the work.
		priority: 0 is the highest one.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_push_job_with_id = lib_function (
	"job_queue_push_job_with_id", [c_void_p, c_uint64, c_void_p, c_void_p], c_uint,
	"""Adds a job with an id, a thread that waits for it in job_queue_request () gets it directly.

	Args:
		job_queue: The queue.
		job_id: The id.
		work: A JobMethod kept by the caller.
		args: The argument of the work.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_push_handler = lib_function (
	"job_queue_push_handler", [c_void_p, c_void_p, c_void_p, c_void_p, c_void_p], c_uint,
	"""Creates a job handler and adds it to a JOB_QUEUE_TYPE_HANDLERS queue.

	Args:
		job_queue: The queue.
		cerver: The cerver of the handler.
		connection: The connection of the handler.
		data: The data of the handler.
		data_delete: A JobDataDelete kept by the caller, or None.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_pull = lib_function (
	"job_queue_pull", [c_void_p], c_void_p,
	"""Takes the next job without waiting.

	Args:
		job_queue: The queue.

	Returns:
		The job, None if the queue is empty.
	"""
)

job_queue_pull_timeout = lib_function (
	"job_queue_pull_timeout", [c_void_p, c_uint32], c_void_p,
	"""Waits for the next job.

	Args:
		job_queue: The queue.
		timeout: The milliseconds, or JOB_QUEUE_WAIT_FOREVER.

	Returns:
		The job, None if the deadline passed or job_queue_signal () was called.
	"""
)

job_queue_pull_interruptible = lib_function (
	"job_queue_pull_interruptible", [c_void_p, c_void_p, c_void_p], c_void_p,
	"""Waits for the next job until interrupted (args) is true.

	The thread that changes what interrupted () reads must call job_queue_signal () after it.

	Args:
		job_queue: The queue.
		interrupted: A JobQueueInterrupted kept by the caller, called with the lock of the queue.
		args: Its argument.

	Returns:
		The job, None when it was interrupted or signaled.
	"""
)

job_queue_request = lib_function (
	"job_queue_request", [c_void_p, c_uint64], c_void_p,
	"""Waits for the job with an id.

	Args:
		job_queue: The queue.
		job_id: The id.

	Returns:
		The job.
	"""
)

job_queue_request_timeout = lib_function (
	"job_queue_request_timeout", [c_void_p, c_uint64, c_uint32], c_void_p,
	"""Waits for the job with an id up to a timeout.

	Args:
		job_queue: The queue.
		job_id: The id.
		timeout: The milliseconds.

	Returns:
		The job, None if it did not arrive before the deadline.
	"""
)

job_queue_record_run = lib_function (
	"job_queue_record_run", [c_void_p, TimespecPointer], None,
	"""Records that a job that was pulled finished its work.

	Args:
		job_queue: The queue.
		start: The Timespec (CLOCK_MONOTONIC) when the job started.
	"""
)

job_queue_get_stats = lib_function (
	"job_queue_get_stats", [c_void_p, JobQueueStatsPointer], None,
	"""Copies the stats of the queue, use job_queue_stats () for a dict.

	Args:
		job_queue: The queue.
		stats: The JobQueueStats that gets them.
	"""
)

job_queue_stats_print = lib_function (
	"job_queue_stats_print", [c_void_p], None,
	"""Prints the stats of the queue with the log.

	Args:
		job_queue: The queue.
	"""
)

job_queue_start = lib_function (
	"job_queue_start", [c_void_p], c_uint,
	"""Starts the thread that runs the handler of the queue with each job.

	Args:
		job_queue: The queue.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_wait = lib_function (
	"job_queue_wait", [c_void_p], None,
	"""Waits until there is a job in the queue or the queue is signaled.

	Args:
		job_queue: The queue.
	"""
)

job_queue_signal = lib_function (
	"job_queue_signal", [c_void_p], None,
	"""Wakes up every thread that waits in the queue.

	Args:
		job_queue: The queue.
	"""
)

job_queue_stop = lib_function (
	"job_queue_stop", [c_void_p], c_uint,
	"""Stops the thread of the queue.

	Args:
		job_queue: The queue.

	Returns:
		0 on success, 1 on error.
	"""
)

job_queue_clear = lib_function (
	"job_queue_clear", [c_void_p], None,
	"""Destroys every job of the queue.

	Args:
		job_queue: The queue.
	"""
)

def job_queue_stats (job_queue: int) -> dict:
	"""Returns the stats of a queue.

	Args:
		job_queue: The queue.

	Returns:
		The values of JobQueueStats, with the arrays as lists.
	"""
	stats = JobQueueStats ()
	job_queue_get_stats (job_queue, byref (stats))

	return {
		"total_jobs": stats.total_jobs,
		"pulled_jobs": stats.pulled_jobs,
		"completed_jobs": stats.completed_jobs,
		"requested_jobs": stats.requested_jobs,
		"timed_out_waits": stats.timed_out_waits,
		"promoted_jobs": stats.promoted_jobs,
		"max_queued": stats.max_queued,
		"priority_jobs": list (stats.priority_jobs),
		"wait_total_microseconds": stats.wait_total_microseconds,
		"run_total_microseconds": stats.run_total_microseconds,
		"wait_histogram": list (stats.wait_histogram),
		"run_histogram": list (stats.run_histogram)
	}
