"""The thread pool of cerver, with a bounded queue and its stats."""

from ctypes import CFUNCTYPE, POINTER, Structure, byref
from ctypes import c_int, c_uint, c_uint64, c_long, c_bool, c_char_p, c_void_p
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"THPOOL_NAME_SIZE", "THPOOL_DEFAULT_QUEUE_SIZE_FACTOR", "THPOOL_DRAIN_TIMEOUT_NONE",
	"THPOOL_HISTOGRAM_MAX_EXPONENT", "THPOOL_HISTOGRAM_BUCKETS",
	"THPOOL_MICROSECONDS_PER_MILLISECOND", "THPOOL_MICROSECONDS_PER_SECOND",
	"THPOOL_NANOSECONDS_PER_MICROSECOND",
	"ThpoolWork", "ThpoolStats", "ThpoolStatsPointer",
	"thpool_create", "thpool_set_queue_size", "thpool_init", "thpool_set_name",
	"thpool_get_num_threads_alive", "thpool_get_num_threads_working",
	"thpool_get_queued", "thpool_get_queue_size",
	"thpool_get_stats", "thpool_histogram_bucket", "thpool_stats_print",
	"thpool_is_empty", "thpool_is_full",
	"thpool_add_work", "thpool_add_work_with_reject", "thpool_add_work_wait",
	"thpool_wait_space", "thpool_wait", "thpool_drain", "thpool_destroy",
	"thpool_stats"
]

THPOOL_NAME_SIZE = 64

# the default queue size is the number of threads times this factor, rounded up to a power of 2
THPOOL_DEFAULT_QUEUE_SIZE_FACTOR = 2

# a drain timeout of 0 waits until every job has finished
THPOOL_DRAIN_TIMEOUT_NONE = 0

# the waits and the runs are counted in buckets of up to 2^0 ... 2^18 ms and a last one
THPOOL_HISTOGRAM_MAX_EXPONENT = 18
THPOOL_HISTOGRAM_BUCKETS = THPOOL_HISTOGRAM_MAX_EXPONENT + 2

THPOOL_MICROSECONDS_PER_MILLISECOND = 1000
THPOOL_MICROSECONDS_PER_SECOND = 1000000
THPOOL_NANOSECONDS_PER_MICROSECOND = 1000

# void (*) (void *args), the work and the reject of a job
ThpoolWork: TypeAlias = CFUNCTYPE (None, c_void_p) # type: ignore

class ThpoolStats (Structure):
	"""The values that a thpool counts since it was created, ``ThpoolStats``.

	Attributes:
		total_jobs: Jobs that entered the queue.
		completed_jobs: Jobs that finished their work.
		rejected_jobs: Jobs that could not enter the queue.
		dropped_jobs: Queued jobs that were rejected by a drain or the destroy.
		waited_jobs: Times that a caller had to wait for space in the queue.
		max_queued: The most jobs that waited in the queue at once.
		wait_total_microseconds: The time that the jobs waited.
		run_total_microseconds: The time that the jobs ran.
		wait_histogram: The jobs that waited up to 2^i ms, the last bucket for the longer ones.
		run_histogram: The jobs that ran up to 2^i ms, the last bucket for the longer ones.
	"""

	_fields_ = [
		("total_jobs", c_uint64),
		("completed_jobs", c_uint64),
		("rejected_jobs", c_uint64),
		("dropped_jobs", c_uint64),
		("waited_jobs", c_uint64),
		("max_queued", c_uint),
		("wait_total_microseconds", c_uint64),
		("run_total_microseconds", c_uint64),
		("wait_histogram", c_uint64 * THPOOL_HISTOGRAM_BUCKETS),
		("run_histogram", c_uint64 * THPOOL_HISTOGRAM_BUCKETS)
	]

ThpoolStatsPointer: TypeAlias = POINTER (ThpoolStats) # type: ignore

thpool_create = lib_function (
	"thpool_create", [c_uint], c_void_p,
	"""Creates a thpool, its queue is the threads times THPOOL_DEFAULT_QUEUE_SIZE_FACTOR.

	Args:
		n_threads: The number of threads.

	Returns:
		The Thpool, released with thpool_destroy ().
	"""
)

thpool_set_queue_size = lib_function (
	"thpool_set_queue_size", [c_void_p, c_uint], c_uint,
	"""Sets how many jobs can wait in the queue, before thpool_init ().

	Args:
		thpool: The thpool.
		queue_size: The size, rounded up to a power of 2.

	Returns:
		0 on success, 1 on error.
	"""
)

thpool_init = lib_function (
	"thpool_init", [c_void_p], c_uint,
	"""Starts the threads of the thpool and waits until every one is running.

	Args:
		thpool: The thpool.

	Returns:
		0 on success, 1 on error (no thread is left running).
	"""
)

thpool_set_name = lib_function (
	"thpool_set_name", [c_void_p, c_char_p], None,
	"""Sets the name of the thpool, used in the names of its threads.

	Args:
		thpool: The thpool.
		name: The name, as bytes.
	"""
)

thpool_get_num_threads_alive = lib_function (
	"thpool_get_num_threads_alive", [c_void_p], c_uint,
	"""Returns the threads of the thpool that are running.

	Args:
		thpool: The thpool.

	Returns:
		The number of threads.
	"""
)

thpool_get_num_threads_working = lib_function (
	"thpool_get_num_threads_working", [c_void_p], c_uint,
	"""Returns the threads of the thpool that are running a job.

	Args:
		thpool: The thpool.

	Returns:
		The number of threads.
	"""
)

thpool_get_queued = lib_function (
	"thpool_get_queued", [c_void_p], c_uint,
	"""Returns how many jobs wait in the queue.

	Args:
		thpool: The thpool.

	Returns:
		The number of jobs.
	"""
)

thpool_get_queue_size = lib_function (
	"thpool_get_queue_size", [c_void_p], c_uint,
	"""Returns how many jobs can wait in the queue.

	Args:
		thpool: The thpool.

	Returns:
		The size of the queue.
	"""
)

thpool_get_stats = lib_function (
	"thpool_get_stats", [c_void_p, ThpoolStatsPointer], None,
	"""Copies the current stats of the thpool, use thpool_stats () for a dict.

	Args:
		thpool: The thpool.
		stats: The ThpoolStats that gets them.
	"""
)

thpool_histogram_bucket = lib_function (
	"thpool_histogram_bucket", [c_uint64], c_uint,
	"""Returns the bucket of the histograms for an elapsed time.

	Args:
		microseconds: The time.

	Returns:
		The index of the bucket.
	"""
)

thpool_stats_print = lib_function (
	"thpool_stats_print", [ThpoolStatsPointer], None,
	"""Prints the stats of a thpool with the log.

	Args:
		stats: The ThpoolStats.
	"""
)

thpool_is_empty = lib_function (
	"thpool_is_empty", [c_void_p], c_bool,
	"""Returns if no thread of the thpool is running a job.

	Args:
		thpool: The thpool.

	Returns:
		True when every thread is idle.
	"""
)

thpool_is_full = lib_function (
	"thpool_is_full", [c_void_p], c_bool,
	"""Returns if a new job can not be queued right now.

	Args:
		thpool: The thpool.

	Returns:
		True when the queue is full or the thpool is not accepting jobs.
	"""
)

thpool_add_work = lib_function (
	"thpool_add_work", [c_void_p, c_void_p, c_void_p], c_int,
	"""Queues a job without blocking.

	Args:
		thpool: The thpool.
		work: A ThpoolWork kept by the caller.
		args: The argument of the work.

	Returns:
		0 on success, 1 if the queue is full or the thpool is not accepting jobs.
	"""
)

thpool_add_work_with_reject = lib_function (
	"thpool_add_work_with_reject", [c_void_p, c_void_p, c_void_p, c_void_p], c_int,
	"""Queues a job without blocking, its reject runs instead of its work if it is dropped.

	Args:
		thpool: The thpool.
		work: A ThpoolWork kept by the caller.
		reject: A ThpoolWork kept by the caller, or None.
		args: The argument of the work.

	Returns:
		0 on success, 1 if the queue is full or the thpool is not accepting jobs.
	"""
)

thpool_add_work_wait = lib_function (
	"thpool_add_work_wait", [c_void_p, c_void_p, c_void_p, c_void_p], c_int,
	"""Queues a job, blocking while the queue is full.

	Args:
		thpool: The thpool.
		work: A ThpoolWork kept by the caller.
		reject: A ThpoolWork kept by the caller, or None.
		args: The argument of the work.

	Returns:
		0 on success, 1 if the thpool stopped accepting jobs.
	"""
)

thpool_wait_space = lib_function (
	"thpool_wait_space", [c_void_p, c_int], c_int,
	"""Waits until a new job can be queued.

	Args:
		thpool: The thpool.
		timeout: The milliseconds to wait.

	Returns:
		0 when there is space, 1 on timeout or when it is not accepting jobs, -1 when a signal interrupted it.
	"""
)

thpool_wait = lib_function (
	"thpool_wait", [c_void_p], None,
	"""Waits until every job has finished.

	Args:
		thpool: The thpool.
	"""
)

thpool_drain = lib_function (
	"thpool_drain", [c_void_p, c_bool, c_long], c_uint,
	"""Stops accepting jobs and waits for the current ones.

	Args:
		thpool: The thpool.
		run_queued: False rejects the queued jobs right away, True still runs them until the timeout.
		timeout: The seconds, THPOOL_DRAIN_TIMEOUT_NONE waits for every job.

	Returns:
		0 if every job finished, 1 if some threads are still working.
	"""
)

thpool_destroy = lib_function (
	"thpool_destroy", [c_void_p], None,
	"""Stops the threads after their current job, rejects the queued jobs and deletes the thpool.

	Args:
		thpool: The thpool, it must not be used after this call.
	"""
)

def thpool_stats (thpool: int) -> dict:
	"""Returns the current stats of a thpool.

	Args:
		thpool: The thpool.

	Returns:
		The values of ThpoolStats, with the histograms as lists.
	"""
	stats = ThpoolStats ()
	thpool_get_stats (thpool, byref (stats))

	return {
		"total_jobs": stats.total_jobs,
		"completed_jobs": stats.completed_jobs,
		"rejected_jobs": stats.rejected_jobs,
		"dropped_jobs": stats.dropped_jobs,
		"waited_jobs": stats.waited_jobs,
		"max_queued": stats.max_queued,
		"wait_total_microseconds": stats.wait_total_microseconds,
		"run_total_microseconds": stats.run_total_microseconds,
		"wait_histogram": list (stats.wait_histogram),
		"run_histogram": list (stats.run_histogram)
	}
