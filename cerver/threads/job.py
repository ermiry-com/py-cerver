from ctypes import POINTER, CFUNCTYPE, Structure
from ctypes import c_void_p, py_object, c_int, c_uint, c_uint64

from ..lib import lib

JobMethod = CFUNCTYPE (None, c_void_p)
JobDataDelete = CFUNCTYPE (None, c_void_p)

class Job (Structure):
	_fields_ = [
		("method", JobMethod),
		("args", c_void_p),
	]

job_new = lib.job_new
job_new.restype = POINTER (Job)

job_delete = lib.job_delete
job_delete.argtypes = [c_void_p]

job_comparator = lib.job_comparator
job_comparator.argtypes = [c_void_p, c_void_p]
job_comparator.restype = c_int

job_create = lib.job_create
job_create.argtypes = [JobMethod, c_void_p]
job_create.restype = POINTER (Job)

job_get = lib.job_get
job_get.argtypes = [c_void_p]
job_get.restype = POINTER (Job)

job_reset = lib.job_reset
job_reset.argtypes = [c_void_p]

job_return = lib.job_return
job_return.argtypes = [c_void_p, c_void_p]

# JobHandler
job_handler_new = lib.job_handler_new
job_handler_new.restype = c_void_p

job_handler_delete = lib.job_handler_delete
job_handler_delete.argtypes = [c_void_p]

job_handler_create = lib.job_handler_create
job_handler_create.restype = c_void_p

job_handler_get = lib.job_handler_get
job_handler_get.argtypes = [c_void_p]
job_handler_get.restype = c_void_p

job_handler_reset = lib.job_handler_reset
job_handler_reset.argtypes = [c_void_p]

job_handler_signal = lib.job_handler_signal
job_handler_signal.argtypes = [c_void_p]

job_handler_return = lib.job_handler_return
job_handler_return.argtypes = [c_void_p, c_void_p]

job_handler_wait = lib.job_handler_wait
job_handler_wait.argtypes = [c_void_p, py_object, c_void_p]

# JobQueue
JobQueueType = c_int

JOB_QUEUE_TYPE_NONE = 0
JOB_QUEUE_TYPE_JOBS = 1
JOB_QUEUE_TYPE_HANDLERS = 2

JobQueueHandler = CFUNCTYPE (None, py_object)

job_queue_new = lib.job_queue_new
job_queue_new.restype = c_void_p

job_queue_delete = lib.job_queue_delete
job_queue_delete.argtypes = [c_void_p]

job_queue_create = lib.job_queue_create
job_queue_create.argtypes = [JobQueueType]
job_queue_create.restype = c_void_p

job_queue_set_handler = lib.job_queue_set_handler
job_queue_set_handler.argtypes = [c_void_p, JobQueueHandler]

job_queue_push = lib.job_queue_push
job_queue_push.argtypes = [c_void_p, c_void_p]
job_queue_push.restype = c_uint

job_queue_push_job = lib.job_queue_push_job
job_queue_push_job.argtypes = [c_void_p, JobMethod, c_void_p]
job_queue_push_job.restype = c_uint

job_queue_push_job_with_id = lib.job_queue_push_job_with_id
job_queue_push_job_with_id.argtypes = [c_void_p, c_uint64, JobMethod, c_void_p]
job_queue_push_job_with_id.restype = c_uint

job_queue_push_handler = lib.job_queue_push_handler
job_queue_push_handler.argtypes = [c_void_p, c_void_p, c_void_p, c_void_p, JobDataDelete]
job_queue_push_handler.restype = c_uint

job_queue_pull = lib.job_queue_pull
job_queue_pull.argtypes = [c_void_p]
job_queue_pull.restype = c_void_p

job_queue_request = lib.job_queue_request
job_queue_request.argtypes = [c_void_p, c_uint64]
job_queue_request.restype = c_void_p

job_queue_start = lib.job_queue_start
job_queue_start.argtypes = [c_void_p]
job_queue_start.restype = c_uint

job_queue_wait = lib.job_queue_wait
job_queue_wait.argtypes = [c_void_p]

job_queue_signal = lib.job_queue_signal
job_queue_signal.argtypes = [c_void_p]

job_queue_stop = lib.job_queue_stop
job_queue_stop.argtypes = [c_void_p]
job_queue_stop.restype = c_uint

job_queue_clear = lib.job_queue_clear
job_queue_clear.argtypes = [c_void_p]
