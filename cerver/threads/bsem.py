from ctypes import c_int, c_void_p

from ..lib import lib

bsem_new = lib.bsem_new
bsem_new.restype = c_void_p

bsem_delete = lib.bsem_delete
bsem_delete.argtypes = [c_void_p]

# inits semaphore to 1 or 0
bsem_init = lib.bsem_init
bsem_init.argtypes = [c_void_p, c_int]

# resets semaphore to 0
bsem_reset = lib.bsem_reset
bsem_reset.argtypes = [c_void_p]

# posts to at least one thread
bsem_post = lib.bsem_post
bsem_post.argtypes = [c_void_p]

# posts to all threads
bsem_post_all = lib.bsem_post_all
bsem_post_all.argtypes = [c_void_p]

# waits on semaphore until semaphore has value 0
bsem_wait = lib.bsem_wait
bsem_wait.argtypes = [c_void_p]
