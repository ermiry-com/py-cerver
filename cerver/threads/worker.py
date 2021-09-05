from ctypes import CFUNCTYPE, c_void_p, py_object, c_int, c_uint, c_char_p

from ..lib import lib

from .threads import thread_mutex_new, thread_mutex_delete
from .threads import thread_mutex_lock, thread_mutex_unlock

WorkerState = c_int

WorkerMethod = CFUNCTYPE (None, py_object)
WorkerDataDelete = CFUNCTYPE (None, c_void_p)

WORKER_STATE_NONE = 0
WORKER_STATE_AVAILABLE = 1
WORKER_STATE_WORKING = 2
WORKER_STATE_STOPPED = 3
WORKER_STATE_ENDED = 4

worker_state_to_string = lib.worker_state_to_string
worker_state_to_string.argtypes = [WorkerState]
worker_state_to_string.restype = c_char_p

worker_delete = lib.worker_delete
worker_delete.argtypes = [c_void_p]

worker_create = lib.worker_create
worker_create.restype = c_void_p

worker_create_with_id = lib.worker_create_with_id
worker_create_with_id.argtypes = [c_uint]
worker_create_with_id.restype = c_void_p

worker_set_name = lib.worker_set_name
worker_set_name.argtypes = [c_void_p, c_char_p]

worker_get_state = lib.worker_get_state
worker_get_state.argtypes = [c_void_p]
worker_get_state.restype = WorkerState

worker_set_work = lib.worker_set_work
worker_set_work.argtypes = [c_void_p, WorkerMethod]

worker_set_delete_data = lib.worker_set_delete_data
worker_set_delete_data.argtypes = [c_void_p, WorkerMethod]

worker_set_reference = lib.worker_set_reference
worker_set_reference.argtypes = [c_void_p, py_object]

worker_set_remove_reference = lib.worker_set_remove_reference
worker_set_remove_reference.argtypes = [c_void_p, WorkerMethod]

worker_start_with_state = lib.worker_start_with_state
worker_start_with_state.argtypes = [c_void_p, WorkerState]
worker_start_with_state.restype = c_uint

worker_start = lib.worker_start
worker_start.argtypes = [c_void_p]
worker_start.restype = c_uint

worker_resume = lib.worker_resume
worker_resume.argtypes = [c_void_p]
worker_resume.restype = c_uint

worker_stop = lib.worker_stop
worker_stop.argtypes = [c_void_p]
worker_stop.restype = c_uint

worker_end = lib.worker_end
worker_end.argtypes = [c_void_p]
worker_end.restype = c_uint

worker_push_job = lib.worker_push_job
worker_push_job.argtypes = [c_void_p, py_object]
worker_push_job.restype = c_uint

worker_push_job_with_work = lib.worker_push_job_with_work
worker_push_job_with_work.argtypes = [c_void_p, WorkerMethod, py_object]
worker_push_job_with_work.restype = c_uint

@CFUNCTYPE (None, py_object)
def worker_remove_reference (worker):
	worker.queue.pop (0)

class Worker ():
	def __init__ (self, name, work):
		self.worker = worker_create ()
		worker_set_reference (self.worker, self)
		worker_set_name (self.worker, name.encode ('utf-8'))
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
