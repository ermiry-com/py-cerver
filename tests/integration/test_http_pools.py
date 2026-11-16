"""The pools of threads of a real HTTP cerver that is created and never started, and its health and
ready routes (cerver 2.1b-17): what is created, what is refused, and the routes that choose a pool.
"""

import pytest

from cerver import cerver_create_web, cerver_teardown
from cerver import CERVER_OVERLOAD_POLICY_REJECT, CERVER_OVERLOAD_POLICY_WAIT
from cerver.http import http_cerver_get
from cerver.http import HTTP_CERVER_POOLS_SIZE, HTTP_POOL_DEFAULT_NAME, HTTP_POOL_NAME_SIZE
from cerver.http import http_cerver_pool, http_cerver_pool_create, http_cerver_pool_get_with_name
from cerver.http import http_pool_get_name, http_pool_set_queue_size
from cerver.http import http_pool_set_overload_policy, http_pool_set_wait_timeout
from cerver.http import http_cerver_set_health_route, http_cerver_set_ready_route, http_cerver_is_ready
from cerver.http import http_cerver_routes_compile, http_cerver_routes_error, http_cerver_routes_errors_count
from cerver.http import http_create_route, http_route_set_pool, REQUEST_METHOD_GET
from cerver.http import http_group_set_pool, http_endpoint_set_pool
from cerver.http import http_handler, HttpGroup

pytestmark = [pytest.mark.integration]

CERVER_NAME = b"pycerver-pools-test"
CERVER_PORT = 5996
CERVER_CONNECTION_QUEUE = 4

POOL_NAME = b"slow"
POOL_THREADS = 2
POOL_QUEUE_SIZE = 8
POOL_WAIT_TIMEOUT = 4

MISSING_POOL = b"missing"
LONG_POOL = b"a-name-that-is-longer-than-a-pool-can-have"

COMPILED = 0
NOT_COMPILED = 1

def _handler (http_receive, request):
	return None

@pytest.fixture
def cerver ():
	cerver = cerver_create_web (CERVER_NAME, CERVER_PORT, CERVER_CONNECTION_QUEUE)

	yield cerver

	cerver_teardown (cerver)

class TestPools:

	def test_a_cerver_has_its_default_pool (self, cerver):
		http_cerver = http_cerver_get (cerver)

		default_pool = http_cerver_pool_get_with_name (http_cerver, HTTP_POOL_DEFAULT_NAME)

		assert default_pool
		assert http_pool_get_name (default_pool) == HTTP_POOL_DEFAULT_NAME
		assert http_pool_get_name (None) is None

	def test_a_pool_is_created_with_a_name_of_its_own (self, cerver):
		http_cerver = http_cerver_get (cerver)

		pool = http_cerver_pool_create (http_cerver, POOL_NAME, POOL_THREADS)

		assert pool
		assert http_pool_get_name (pool) == POOL_NAME
		assert http_cerver_pool_get_with_name (http_cerver, POOL_NAME) == pool
		assert http_cerver_pool_get_with_name (http_cerver, MISSING_POOL) is None

		# a name has one pool, also the one of the default pool
		assert http_cerver_pool_create (http_cerver, POOL_NAME, POOL_THREADS) is None
		assert http_cerver_pool_create (http_cerver, HTTP_POOL_DEFAULT_NAME, POOL_THREADS) is None

	@pytest.mark.parametrize ("name", [b"", b"two words", LONG_POOL, None])
	def test_a_name_that_is_not_a_token_is_refused (self, cerver, name):
		assert http_cerver_pool_create (http_cerver_get (cerver), name, POOL_THREADS) is None

	def test_a_pool_needs_threads_and_a_cerver (self, cerver):
		assert http_cerver_pool_create (http_cerver_get (cerver), POOL_NAME, 0) is None
		assert http_cerver_pool_create (None, POOL_NAME, POOL_THREADS) is None

	def test_the_name_of_a_pool_fits_in_its_size (self):
		assert len (LONG_POOL) >= HTTP_POOL_NAME_SIZE
		assert len (HTTP_POOL_DEFAULT_NAME) < HTTP_POOL_NAME_SIZE

	def test_a_cerver_has_a_limit_of_pools (self, cerver):
		http_cerver = http_cerver_get (cerver)

		for index in range (1, HTTP_CERVER_POOLS_SIZE):
			assert http_cerver_pool_create (http_cerver, f"pool-{index}".encode (), POOL_THREADS)

		assert http_cerver_pool_create (http_cerver, POOL_NAME, POOL_THREADS) is None

	def test_the_settings_of_a_pool (self, cerver):
		http_cerver = http_cerver_get (cerver)

		pool = http_cerver_pool (
			http_cerver, "slow", POOL_THREADS,
			queue_size=POOL_QUEUE_SIZE, overload_policy=CERVER_OVERLOAD_POLICY_REJECT,
			wait_timeout=POOL_WAIT_TIMEOUT
		)

		assert pool
		assert http_pool_get_name (pool) == POOL_NAME

		http_pool_set_overload_policy (pool, CERVER_OVERLOAD_POLICY_WAIT)
		http_pool_set_queue_size (pool, 0)
		http_pool_set_wait_timeout (pool, 0)

		# nothing is done without a pool
		http_pool_set_queue_size (None, POOL_QUEUE_SIZE)
		http_pool_set_overload_policy (None, CERVER_OVERLOAD_POLICY_REJECT)
		http_pool_set_wait_timeout (None, POOL_WAIT_TIMEOUT)

		# a pool that could not be created has no settings
		assert http_cerver_pool (http_cerver, "slow", POOL_THREADS, queue_size=POOL_QUEUE_SIZE) is None

class TestRoutes:

	def test_the_routes_choose_a_pool_of_the_cerver (self, cerver):
		http_cerver = http_cerver_get (cerver)

		assert http_cerver_pool_create (http_cerver, POOL_NAME, POOL_THREADS)

		api = HttpGroup.create (http_cerver, "api")

		work = HttpGroup.create (http_cerver, "work")
		work.pool ("slow")

		@api.get ("fast")
		def fast_handler (http_receive, request):
			return None

		@api.get ("slow", pool="slow")
		def slow_handler (http_receive, request):
			return None

		@work.get ("job")
		def job_handler (http_receive, request):
			return None

		@work.get ("default", pool=HTTP_POOL_DEFAULT_NAME)
		def default_handler (http_receive, request):
			return None

		route = http_create_route (http_cerver, REQUEST_METHOD_GET, "old", http_handler (_handler))
		http_route_set_pool (route, POOL_NAME)

		assert http_cerver_routes_compile (http_cerver) == COMPILED
		assert http_cerver_routes_errors_count (http_cerver) == 0

	def test_an_endpoint_with_a_pool_that_the_cerver_does_not_have (self, cerver):
		http_cerver = http_cerver_get (cerver)

		api = HttpGroup.create (http_cerver, "api")

		@api.get ("job", pool=MISSING_POOL)
		def job_handler (http_receive, request):
			return None

		assert http_cerver_routes_compile (http_cerver) == NOT_COMPILED
		assert MISSING_POOL in http_cerver_routes_error (http_cerver)

	def test_a_group_with_a_pool_that_the_cerver_does_not_have (self, cerver):
		http_cerver = http_cerver_get (cerver)

		api = HttpGroup.create (http_cerver, "api")
		http_group_set_pool (api.group, MISSING_POOL)

		endpoint = api.add (REQUEST_METHOD_GET, "job", _handler)
		assert endpoint

		assert http_cerver_routes_compile (http_cerver) == NOT_COMPILED
		assert MISSING_POOL in http_cerver_routes_error (http_cerver)

	def test_a_pool_with_a_name_that_is_too_long_is_an_error_when_it_is_set (self, cerver):
		http_cerver = http_cerver_get (cerver)

		api = HttpGroup.create (http_cerver, "api")
		endpoint = api.add (REQUEST_METHOD_GET, "job", _handler)

		assert http_cerver_routes_errors_count (http_cerver) == 0

		http_endpoint_set_pool (endpoint, LONG_POOL)

		assert http_cerver_routes_errors_count (http_cerver) == 1
		assert http_cerver_routes_compile (http_cerver) == NOT_COMPILED

	def test_nothing_is_done_without_a_group_an_endpoint_or_a_route (self):
		http_group_set_pool (None, POOL_NAME)
		http_endpoint_set_pool (None, POOL_NAME)
		http_route_set_pool (None, POOL_NAME)

class TestHealth:

	def test_the_routes_that_the_cerver_answers (self, cerver):
		http_cerver = http_cerver_get (cerver)

		http_cerver_set_health_route (http_cerver, b"/health")
		http_cerver_set_ready_route (http_cerver, b"/ready")

		# a NULL path removes them
		http_cerver_set_health_route (http_cerver, None)
		http_cerver_set_ready_route (http_cerver, None)

		# nothing is done without a cerver
		http_cerver_set_health_route (None, b"/health")
		http_cerver_set_ready_route (None, b"/ready")

	def test_a_cerver_that_has_not_started_is_ready (self, cerver):
		assert http_cerver_is_ready (http_cerver_get (cerver))
		assert not http_cerver_is_ready (None)
