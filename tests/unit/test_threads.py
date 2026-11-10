"""Unit tests for the threads of cerver: the thpool with its stats, the job queue with its
priorities, the workers and the worker manager, with Python works.

Bugs these tests fixed:
- the Job of the package did not have its id, so its work and its args were read from the wrong bytes
- Worker.__del__ called into cerver while the interpreter was ending, now it is Worker.delete ()
"""

import ctypes
import threading
import pytest

from cerver.threads import ThpoolWork, thpool_create, thpool_init, thpool_add_work, thpool_wait
from cerver.threads import thpool_destroy, thpool_stats, thpool_get_queue_size, thpool_set_queue_size
from cerver.threads import thpool_histogram_bucket, THPOOL_HISTOGRAM_BUCKETS
from cerver.threads import JobMethod, Job, job_create, job_delete
from cerver.threads import job_queue_create_with_priorities, job_queue_delete, job_queue_push_job_priority
from cerver.threads import job_queue_pull, job_queue_pull_timeout, job_queue_size, job_queue_stats
from cerver.threads import job_queue_default_priority, JOB_QUEUE_TYPE_JOBS, JOB_QUEUE_PRIORITY_HIGH
from cerver.threads import JOB_QUEUE_PRIORITY_LOW, JOB_QUEUE_STARVATION_DISABLED
from cerver.threads import job_queue_set_starvation_limit
from cerver.threads import Worker, WORKER_STATE_AVAILABLE, WORKER_STATE_STOPPED, worker_state_to_string
from cerver.threads import WorkerManager

pytestmark = [pytest.mark.unit]

THREADS = 2
JOBS = 8
QUEUE_SIZE = 16

WAIT_SECONDS = 8
SHORT_TIMEOUT_MILLISECONDS = 16

class TestThpool:

	def test_python_work_runs_and_is_counted (self):
		done = []
		lock = threading.Lock ()

		def work (args):
			with lock:
				done.append (args)

		callback = ThpoolWork (work)

		thpool = thpool_create (THREADS)
		assert thpool_set_queue_size (thpool, QUEUE_SIZE) == 0
		assert thpool_init (thpool) == 0

		try:
			for index in range (JOBS):
				assert thpool_add_work (thpool, callback, index + 1) == 0

			thpool_wait (thpool)

			stats = thpool_stats (thpool)
			assert sorted (done) == list (range (1, JOBS + 1))
			assert (stats["total_jobs"], stats["completed_jobs"]) == (JOBS, JOBS)
			assert len (stats["wait_histogram"]) == THPOOL_HISTOGRAM_BUCKETS
			assert thpool_get_queue_size (thpool) == QUEUE_SIZE

		finally:
			thpool_destroy (thpool)

	def test_histogram_bucket (self):
		assert thpool_histogram_bucket (0) == 0
		assert thpool_histogram_bucket (1 << 40) == THPOOL_HISTOGRAM_BUCKETS - 1

class TestJobQueue:

	def test_job_layout (self):
		callback = JobMethod (lambda args: None)
		job = job_create (callback, 7)
		try:
			assert job.contents.args == 7
			assert job.contents.work == ctypes.cast (callback, ctypes.c_void_p).value

		finally:
			job_delete (job)

	def test_priorities (self):
		callback = JobMethod (lambda args: None)
		queue = job_queue_create_with_priorities (JOB_QUEUE_TYPE_JOBS, 3)
		job_queue_set_starvation_limit (queue, JOB_QUEUE_STARVATION_DISABLED)

		try:
			assert job_queue_default_priority (queue) == 1
			assert job_queue_push_job_priority (queue, callback, 1, JOB_QUEUE_PRIORITY_LOW) == 0
			assert job_queue_push_job_priority (queue, callback, 2, JOB_QUEUE_PRIORITY_HIGH) == 0
			assert job_queue_size (queue) == 2

			first = ctypes.cast (job_queue_pull (queue), ctypes.POINTER (Job))
			second = ctypes.cast (job_queue_pull (queue), ctypes.POINTER (Job))
			assert (first.contents.args, second.contents.args) == (2, 1)

			stats = job_queue_stats (queue)
			assert (stats["total_jobs"], stats["pulled_jobs"]) == (2, 2)
			assert stats["priority_jobs"][:3] == [1, 0, 1]

			job_delete (first)
			job_delete (second)

		finally:
			job_queue_delete (queue)

	def test_pull_timeout_of_an_empty_queue (self):
		queue = job_queue_create_with_priorities (JOB_QUEUE_TYPE_JOBS, 1)
		try:
			assert job_queue_pull_timeout (queue, SHORT_TIMEOUT_MILLISECONDS) is None
			assert job_queue_stats (queue)["timed_out_waits"] == 1

		finally:
			job_queue_delete (queue)

class TestWorker:

	def test_jobs_run_and_the_worker_stops (self):
		done = threading.Event ()
		values = []

		def work (data):
			values.append (data["value"])
			done.set ()

		worker = Worker ("unit-worker", work)
		try:
			assert worker.start () == 0
			assert worker.state () == WORKER_STATE_AVAILABLE
			assert worker.push ({"value": 5}) == 0
			assert done.wait (WAIT_SECONDS)
			assert values == [5]

			assert worker.stop () == 0
			assert worker.state () == WORKER_STATE_STOPPED
			assert worker_state_to_string (WORKER_STATE_STOPPED) == b"Stopped"
			assert worker.resume () == 0

		finally:
			worker.delete ()

		assert worker.worker is None

class TestWorkerManager:

	def test_jobs_run_with_their_objects (self):
		done = threading.Event ()
		values = []
		lock = threading.Lock ()

		def work (data):
			with lock:
				values.append (data)
				if (len (values) == JOBS):
					done.set ()

		manager = WorkerManager ("unit-manager", work, min_workers=1, max_workers=4)
		try:
			assert manager.start () == 0
			for index in range (JOBS):
				assert manager.push ({"index": index}) == 0

			assert done.wait (WAIT_SECONDS)
			assert sorted (value["index"] for value in values) == list (range (JOBS))

			stats = manager.stats ()
			assert 1 <= stats["workers"] <= 4
			assert len (manager.states ()) == manager.workers ()

		finally:
			manager.delete ()

	def test_invalid_limits (self):
		with pytest.raises (ValueError):
			WorkerManager ("unit-invalid", lambda data: None, min_workers=4, max_workers=1)
