"""Unit tests for http/decorators.py - the callbacks that cerver keeps.

A ctypes callback must live as long as the cerver that calls it, so every one that goes
through the package is kept, also the ones that already were callbacks.

Bugs these tests fixed:
- a function that already was a HttpHandler was returned without keeping it, so a handler
  created in a scope that ended was freed while the cerver still held its address
- HttpGroup.create () created the group of cerver before it checked its root, so a root
  without its handler left an orphan group in the cerver
"""

import gc
import pytest
from unittest.mock import patch

from cerver.http import HttpAfterMiddleware
from cerver.http import HttpBeforeMiddleware
from cerver.http import HttpHandler
from cerver.http import REQUEST_METHOD_GET
from cerver.http import decorators
from cerver.http.decorators import HttpGroup
from cerver.http.decorators import http_after_middleware
from cerver.http.decorators import http_before_middleware
from cerver.http.decorators import http_callbacks
from cerver.http.decorators import http_group_root_check
from cerver.http.decorators import http_handler

pytestmark = [pytest.mark.unit]

def _handler (http_receive, request):
	return None

def _middleware (http_receive, request):
	return 0

class TestCallbacks:

	def test_function_is_wrapped_and_kept (self):
		handler = http_handler (_handler)

		assert isinstance (handler, HttpHandler)
		assert http_callbacks[id (handler)] is handler

	def test_existing_handler_is_kept (self):
		def scoped ():
			return HttpHandler (_handler)

		handler = http_handler (scoped ())
		handler_id = id (handler)
		del handler
		gc.collect ()

		assert isinstance (http_callbacks[handler_id], HttpHandler)

	def test_a_callback_is_kept_once (self):
		handler = http_handler (_handler)
		size = len (http_callbacks)

		assert http_handler (handler) is handler
		assert len (http_callbacks) == size

	def test_middlewares (self):
		assert isinstance (http_before_middleware (_middleware), HttpBeforeMiddleware)
		assert isinstance (http_after_middleware (_handler), HttpAfterMiddleware)

class TestGroupRoot:

	def test_root_with_method_and_handler (self):
		http_group_root_check (REQUEST_METHOD_GET, _handler)
		http_group_root_check (None, None)

	@pytest.mark.parametrize ("method, handler", [(REQUEST_METHOD_GET, None), (None, _handler)])
	def test_root_without_one_of_them (self, method, handler):
		with pytest.raises (ValueError):
			http_group_root_check (method, handler)

	def test_create_checks_the_root_before_the_group (self):
		with patch.object (decorators, "http_cerver_group_create") as group_create:
			with pytest.raises (ValueError):
				HttpGroup.create (None, "api", REQUEST_METHOD_GET)

		group_create.assert_not_called ()

	def test_group_that_cerver_did_not_create_raises (self):
		with pytest.raises (ValueError):
			HttpGroup.create (None, "api")
