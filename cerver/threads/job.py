from ctypes import Structure, c_void_p, c_int, POINTER, CFUNCTYPE

from ..lib import lib

JobMethod = CFUNCTYPE (None, c_void_p)

class Job (Structure):
	_fields_ = [
		("method", JobMethod),
		("args", c_void_p),
	]

job_new = lib.job_new
job_new.restype = POINTER (Job)

job_delete = lib.job_delete
job_delete.argtypes = [c_void_p]

job_create = lib.job_create
job_create.argtypes = [JobMethod, c_void_p]
job_create.restype = POINTER (Job)

# JobQueue
job_queue_new = lib.job_queue_new
job_queue_new.restype = c_void_p

job_queue_delete = lib.job_queue_delete
job_queue_delete.argtypes = [c_void_p]

job_queue_create = lib.job_queue_create
job_queue_create.restype = c_void_p

job_queue_push = lib.job_queue_push
job_queue_push.argtypes = [c_void_p, c_void_p]
job_queue_push.restype = c_int

job_queue_pull = lib.job_queue_pull
job_queue_pull.argtypes = [c_void_p]
job_queue_pull.restype = POINTER (Job)

job_queue_clear = lib.job_queue_clear
job_queue_clear.argtypes = [c_void_p]
