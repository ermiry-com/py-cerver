"""The routes of the groups API in the tree that cerver compiles.

A real web cerver is created and its tree compiled, never started: the groups and their
decorators, the subgroups, the typed params, the middleware and the registration errors
are read from the compiled tree.
"""

import pytest

from cerver import cerver_create_web
from cerver import cerver_teardown
from cerver.http import HTTP_ROUTE_MODIFIER_MULTI_PART
from cerver.http import REQUEST_METHOD_GET
from cerver.http import http_cerver_get
from cerver.http import http_cerver_routes_compile
from cerver.http import http_cerver_routes_error
from cerver.http import http_cerver_routes_errors_count
from cerver.http import http_cerver_routes_json
from cerver.http import http_endpoint_get_path
from cerver.http import http_route_modifier_to_string
from cerver.http.decorators import HttpGroup

pytestmark = [pytest.mark.integration]

CERVER_NAME = b"pycerver-tree-test"
CERVER_PORT = 5996
CERVER_CONNECTION_QUEUE = 4

TREE_ERRORS_NONE = 0

MODIFIER_MULTI_PART = http_route_modifier_to_string (HTTP_ROUTE_MODIFIER_MULTI_PART).decode ("utf-8")

def _handler (http_receive, request):
	return None

def _middleware (http_receive, request):
	return 0

@pytest.fixture
def http_cerver ():
	cerver = cerver_create_web (CERVER_NAME, CERVER_PORT, CERVER_CONNECTION_QUEUE)

	yield http_cerver_get (cerver)

	cerver_teardown (cerver)

def _tree (http_cerver) -> dict:
	return {
		(endpoint["method"], endpoint["path"]): endpoint
		for endpoint in http_cerver_routes_json (http_cerver)["endpoints"]
	}

def _register (http_cerver) -> HttpGroup:
	api = HttpGroup.create (http_cerver, "api/items", REQUEST_METHOD_GET, _handler)
	api.before (_middleware)
	api.after (_handler)

	api.get (":id<objectid>") (_handler)
	api.delete (":id<objectid>") (_handler)
	api.post ("upload", modifier=HTTP_ROUTE_MODIFIER_MULTI_PART) (_handler)
	api.put ("numbers/:value<int>", before=(_middleware,)) (_handler)

	archived = api.subgroup ("archived", REQUEST_METHOD_GET, _handler)
	archived.patch (":id<uuid>") (_handler)

	return api

EXPECTED_ENDPOINTS = {
	("GET", "/api/items"),
	("GET", "/api/items/:id<objectid>"),
	("DELETE", "/api/items/:id<objectid>"),
	("POST", "/api/items/upload"),
	("PUT", "/api/items/numbers/:value<int>"),
	("GET", "/api/items/archived"),
	("PATCH", "/api/items/archived/:id<uuid>")
}

class TestTree:

	def test_routes_json_before_compiling_is_empty (self, http_cerver):
		_register (http_cerver)

		assert http_cerver_routes_json (http_cerver) == dict ()

	def test_tree_compiles (self, http_cerver):
		_register (http_cerver)

		assert http_cerver_routes_compile (http_cerver) == TREE_ERRORS_NONE, http_cerver_routes_error (http_cerver)
		assert http_cerver_routes_errors_count (http_cerver) == TREE_ERRORS_NONE

	def test_endpoints (self, http_cerver):
		_register (http_cerver)
		http_cerver_routes_compile (http_cerver)

		tree = _tree (http_cerver)

		assert set (tree) == EXPECTED_ENDPOINTS
		assert not any (endpoint["compatibility"] for endpoint in tree.values ())

	def test_modifier (self, http_cerver):
		_register (http_cerver)
		http_cerver_routes_compile (http_cerver)

		assert _tree (http_cerver)[("POST", "/api/items/upload")]["modifier"] == MODIFIER_MULTI_PART

	def test_endpoint_path (self, http_cerver):
		api = HttpGroup.create (http_cerver, "api/paths")
		endpoint = api.add (REQUEST_METHOD_GET, "a/:b", _handler)

		assert http_endpoint_get_path (endpoint).contents.str == b"/api/paths/a/:b"

class TestTreeErrors:

	def test_duplicated_endpoint (self, http_cerver):
		api = HttpGroup.create (http_cerver, "api/items")
		api.get ("same") (_handler)
		api.get ("same") (_handler)

		assert http_cerver_routes_compile (http_cerver) != TREE_ERRORS_NONE
		assert http_cerver_routes_error (http_cerver)

	def test_unknown_validator (self, http_cerver):
		api = HttpGroup.create (http_cerver, "api/items")
		api.get (":id<unknown>") (_handler)

		assert http_cerver_routes_compile (http_cerver) != TREE_ERRORS_NONE
