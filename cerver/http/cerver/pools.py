"""The named pools of threads of an HTTP cerver, and its health and ready routes."""

from ctypes import c_void_p, c_uint, c_bool, c_char_p
from typing import TypeAlias

from ...lib import lib_function, lib_c_string

from ...core.policies import CerverOverloadPolicy

__all__ = [
	"HTTP_CERVER_POOLS_SIZE", "HTTP_POOL_DEFAULT_NAME",
	"HttpPool",
	"http_cerver_pool_create", "http_cerver_pool_get_with_name", "http_pool_get_name",
	"http_pool_set_queue_size", "http_pool_set_overload_policy", "http_pool_set_wait_timeout",
	"http_cerver_set_health_route", "http_cerver_set_ready_route", "http_cerver_is_ready",
	"http_cerver_pool"
]

# the pools of threads that an HTTP cerver has at most, with the default one
HTTP_CERVER_POOLS_SIZE = 1 << 4

# the pool of the requests that did not choose one: the thpool of the cerver
HTTP_POOL_DEFAULT_NAME = b"default"

HttpPool: TypeAlias = c_void_p # type: ignore

http_cerver_pool_create = lib_function (
	"http_cerver_pool_create", [c_void_p, c_char_p, c_uint], c_void_p,
	"""Creates a pool of threads in an HTTP cerver, before the cerver starts; its threads start with the cerver.

	The requests of the endpoints that chose the pool (http_group_set_pool (), http_endpoint_set_pool (),
	http_route_set_pool ()) are handled by its threads, so the handlers that take long do not keep the threads
	that the fast ones need. Only a cerver with CERVER_HANDLER_TYPE_EVENTS starts its named pools: with
	another handler type a warning is logged and every request is handled like before.

	Args:
		http_cerver: The HttpCerver.
		name: The name that the endpoints use to choose it, as bytes: a token of up to 31 bytes that no
			other pool of the cerver has ("default" is the one of the thpool of the cerver).
		n_threads: The threads of the pool, more than 0.

	Returns:
		The HttpPool, None for a name that is not valid or that another pool has, no threads, a cerver that
		already started or one that has HTTP_CERVER_POOLS_SIZE pools.
	"""
)

http_cerver_pool_get_with_name = lib_function (
	"http_cerver_pool_get_with_name", [c_void_p, c_char_p], c_void_p,
	"""Returns the pool of an HTTP cerver with a name.

	Args:
		http_cerver: The HttpCerver.
		name: The name as bytes, HTTP_POOL_DEFAULT_NAME for the default pool.

	Returns:
		The HttpPool, None when no pool has the name.
	"""
)

http_pool_get_name = lib_function (
	"http_pool_get_name", [c_void_p], c_char_p,
	"""Returns the name of a pool.

	Args:
		pool: The HttpPool.

	Returns:
		The name as bytes, None for a NULL pool.
	"""
)

http_pool_set_queue_size = lib_function (
	"http_pool_set_queue_size", [c_void_p, c_uint], None,
	"""Sets the jobs that can wait in the queue of a pool for one of its threads.

	The default pool takes its size from the cerver (cerver_set_thpool_queue_size ()).

	Args:
		pool: The HttpPool.
		queue_size: The size, rounded up to a power of 2; 0 uses the default of the thpool.
	"""
)

http_pool_set_overload_policy = lib_function (
	"http_pool_set_overload_policy", [c_void_p, CerverOverloadPolicy], None,
	"""Sets what a pool does with a request when its queue is full.

	CERVER_OVERLOAD_POLICY_WAIT keeps the request in its event loop until a place is free or its wait ends
	(http_pool_set_wait_timeout ()), then it is answered with 503; CERVER_OVERLOAD_POLICY_REJECT answers it
	with 503 at once. Without this call a pool uses the policy of its cerver.

	Args:
		pool: The HttpPool.
		policy: A CERVER_OVERLOAD_POLICY_* value.
	"""
)

http_pool_set_wait_timeout = lib_function (
	"http_pool_set_wait_timeout", [c_void_p, c_uint], None,
	"""Sets the seconds that a request waits for a place in a pool that is full, then it is answered with 503.

	Without this call a pool uses the wait of its cerver (cerver_set_overload_wait_timeout ()).

	Args:
		pool: The HttpPool.
		seconds: The seconds, with 0 a request does not wait.
	"""
)

http_cerver_set_health_route = lib_function (
	"http_cerver_set_health_route", [c_void_p, c_char_p], None,
	"""Sets the path of the health route of an HTTP cerver: a GET or a HEAD of it is answered with 200 while
	the cerver runs.

	With CERVER_HANDLER_TYPE_EVENTS it is answered by the event loop, also when every thread is busy; with
	another handler type it waits for a thread like any request. It has no authentication and it is not
	counted in the stats of the routes.

	Args:
		http_cerver: The HttpCerver.
		path: The complete path as bytes, like b"/api/health"; None removes the route.
	"""
)

http_cerver_set_ready_route = lib_function (
	"http_cerver_set_ready_route", [c_void_p, c_char_p], None,
	"""Sets the path of the ready route of an HTTP cerver: 200 when the cerver can take a request, and 503
	with Retry-After when one of its pools has no place for a request or has requests that wait for one,
	or when the cerver is stopping.

	Args:
		http_cerver: The HttpCerver.
		path: The complete path as bytes, like b"/api/ready"; None removes the route.
	"""
)

http_cerver_is_ready = lib_function (
	"http_cerver_is_ready", [c_void_p], c_bool,
	"""Returns whether an HTTP cerver can take a request: what its ready route answers.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		False for a cerver that is stopping, or one with a pool that has no place for a request or that has
		requests that wait for one.
	"""
)

def http_cerver_pool (
	http_cerver: int, name: str | bytes, n_threads: int,
	queue_size: int | None = None, overload_policy: int | None = None, wait_timeout: int | None = None
) -> int | None:
	"""Creates a pool of threads in an HTTP cerver with its settings.

	Args:
		http_cerver: The HttpCerver.
		name: The name of the pool.
		n_threads: The threads of the pool.
		queue_size: The jobs that can wait in its queue, None for the default of the thpool.
		overload_policy: A CERVER_OVERLOAD_POLICY_* value, None for the policy of the cerver.
		wait_timeout: The seconds that a request waits for a place, None for the wait of the cerver.

	Returns:
		The HttpPool, None when it could not be created.
	"""
	pool = http_cerver_pool_create (http_cerver, lib_c_string (name), n_threads)
	if (pool):
		if (queue_size is not None):
			http_pool_set_queue_size (pool, queue_size)

		if (overload_policy is not None):
			http_pool_set_overload_policy (pool, overload_policy)

		if (wait_timeout is not None):
			http_pool_set_wait_timeout (pool, wait_timeout)

	return pool
