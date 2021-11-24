from ctypes import CFUNCTYPE, c_void_p, c_size_t

from ..lib import lib

ThreadWork = CFUNCTYPE (None, c_void_p)

thread_create_detached = lib.thread_create_detached
thread_create_detached.argtypes = [ThreadWork, c_void_p]
thread_create_detached.restype = c_size_t

thread_mutex_new = lib.thread_mutex_new
thread_mutex_new.restype = c_void_p

thread_mutex_delete = lib.thread_mutex_delete
thread_mutex_delete.argtypes = [c_void_p]

thread_mutex_lock = lib.thread_mutex_lock
thread_mutex_lock.argtypes = [c_void_p]

thread_mutex_unlock = lib.thread_mutex_unlock
thread_mutex_unlock.argtypes = [c_void_p]

thread_cond_new = lib.thread_cond_new
thread_cond_new.restype = c_void_p

thread_cond_delete = lib.thread_cond_delete
thread_cond_delete.argtypes = [c_void_p]
