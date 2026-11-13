"""The configuration of a real HTTP cerver, created and never started: the settings of every
part, the metrics, the HEAD and OPTIONS decorators and the routes of the first API.
"""

import pytest

from cerver import cerver_create_web, cerver_teardown, cerver_set_bind_address, cerver_set_ipv6_only
from cerver import cerver_set_overload_policy, cerver_set_drain_policy, cerver_set_drain_timeout
from cerver import CERVER_OVERLOAD_POLICY_REJECT, CERVER_DRAIN_POLICY_REJECT
from cerver.http import http_cerver_get, http_cerver_configuration
from cerver.http import http_cerver_set_max_body_size, http_cerver_set_headers_timeout
from cerver.http import http_cerver_set_headers_timeout_milliseconds, http_cerver_set_request_timeout_milliseconds
from cerver.http import http_cerver_set_idle_timeout_milliseconds, http_cerver_set_half_close_is_gone
from cerver.http import http_cerver_set_send_timeout_milliseconds
from cerver.http import http_stage_label, http_abort_reason_label, http_client_state_string
from cerver.http import HTTP_STAGES, HTTP_STAGE_UPLOAD, HTTP_ABORT_REASON_RESET, HTTP_CLIENT_STATE_CLOSED
from cerver.http import http_cerver_set_request_id, http_cerver_set_date_header
from cerver.http import http_cerver_set_trusted_proxies, http_cerver_add_trusted_proxy
from cerver.http import HTTP_TRUSTED_PROXIES_LIST, http_proxy_is_trusted
from cerver.http import http_cerver_set_compression_level, http_cerver_set_compression_min_size
from cerver.http import http_cerver_add_origin_to_whitelist, http_cerver_enable_admin_routes
from cerver.http import http_cerver_metrics, http_cerver_routes_compile, http_cerver_routes_json
from cerver.http import http_cerver_set_uploads_path, http_cerver_generate_uploads_path
from cerver.http import http_create_route, http_create_child_route, REQUEST_METHOD_GET
from cerver.http import http_handler, HttpGroup, http_group

pytestmark = [pytest.mark.integration]

CERVER_NAME = b"pycerver-configuration-test"
CERVER_PORT = 5997
CERVER_CONNECTION_QUEUE = 4

MAX_BODY_SIZE = 1 << 20
HEADERS_TIMEOUT = 8

# milliseconds
HEADERS_TIMEOUT_MILLISECONDS = 1500
REQUEST_TIMEOUT_MILLISECONDS = 4500
IDLE_TIMEOUT_MILLISECONDS = 250
SEND_TIMEOUT_MILLISECONDS = 750
COMPRESSION_LEVEL = 4
COMPRESSION_MIN_SIZE = 1 << 9
DRAIN_TIMEOUT = 2

def _handler (http_receive, request):
	return None

@pytest.fixture
def cerver ():
	cerver = cerver_create_web (CERVER_NAME, CERVER_PORT, CERVER_CONNECTION_QUEUE)

	yield cerver

	cerver_teardown (cerver)

def _endpoints (http_cerver) -> set:
	http_cerver_routes_compile (http_cerver)
	return {(endpoint["method"], endpoint["path"]) for endpoint in http_cerver_routes_json (http_cerver)["endpoints"]}

class TestConfiguration:

	def test_cerver_settings (self, cerver):
		assert cerver_set_bind_address (cerver, b"::1") == 0
		assert cerver_set_bind_address (cerver, b"not an ip") == 1
		cerver_set_ipv6_only (cerver, True)
		cerver_set_overload_policy (cerver, CERVER_OVERLOAD_POLICY_REJECT)
		cerver_set_drain_policy (cerver, CERVER_DRAIN_POLICY_REJECT)
		cerver_set_drain_timeout (cerver, DRAIN_TIMEOUT)

	def test_http_settings (self, cerver):
		http_cerver = http_cerver_get (cerver)

		http_cerver_set_max_body_size (http_cerver, MAX_BODY_SIZE)
		http_cerver_set_headers_timeout (http_cerver, HEADERS_TIMEOUT)
		http_cerver_set_request_id (http_cerver, True)
		http_cerver_set_date_header (http_cerver, False)
		http_cerver_set_compression_level (http_cerver, COMPRESSION_LEVEL)
		http_cerver_set_compression_min_size (http_cerver, COMPRESSION_MIN_SIZE)
		http_cerver_set_uploads_path (http_cerver, b"/tmp/pycerver-uploads")
		http_cerver_generate_uploads_path (http_cerver, "/tmp/pycerver-uploads-%s")
		http_cerver_enable_admin_routes (http_cerver, True)

		assert http_cerver_add_origin_to_whitelist (http_cerver, b"https://app.example.com") == 0

	def test_trusted_proxies (self, cerver):
		http_cerver = http_cerver_get (cerver)

		http_cerver_set_trusted_proxies (http_cerver, HTTP_TRUSTED_PROXIES_LIST)
		assert http_cerver_add_trusted_proxy (http_cerver, b"10.0.0.0/8") == 0

		assert http_proxy_is_trusted (http_cerver, b"10.1.1.1", 8)
		assert not http_proxy_is_trusted (http_cerver, b"11.1.1.1", 8)

	def test_timeouts_in_milliseconds (self, cerver):
		http_cerver = http_cerver_get (cerver)

		http_cerver_set_headers_timeout_milliseconds (http_cerver, HEADERS_TIMEOUT_MILLISECONDS)
		http_cerver_set_request_timeout_milliseconds (http_cerver, REQUEST_TIMEOUT_MILLISECONDS)
		http_cerver_set_idle_timeout_milliseconds (http_cerver, IDLE_TIMEOUT_MILLISECONDS)
		http_cerver_set_send_timeout_milliseconds (http_cerver, SEND_TIMEOUT_MILLISECONDS)
		http_cerver_set_half_close_is_gone (http_cerver, False)

	def test_metrics (self, cerver):
		metrics = http_cerver_metrics (http_cerver_get (cerver))
		assert "cerver_info{version=" in metrics
		assert "cerver_http_request_duration_seconds" in metrics

	def test_gone_metrics (self, cerver):
		metrics = http_cerver_metrics (http_cerver_get (cerver))
		assert "cerver_http_failed_responses_total 0" in metrics
		assert 'cerver_http_aborted_requests_total{stage="upload",reason="reset"} 0' in metrics
		assert 'cerver_http_vanished_requests_total{stage="queued"} 0' in metrics

	def test_stage_names (self):
		assert HTTP_STAGES == 7
		assert http_stage_label (HTTP_STAGE_UPLOAD) == b"upload"
		assert http_abort_reason_label (HTTP_ABORT_REASON_RESET) == b"reset"
		assert http_client_state_string (HTTP_CLIENT_STATE_CLOSED) == b"Closed"

	def test_service_configuration (self):
		service = http_cerver_configuration ("configuration", port=CERVER_PORT + 1)
		assert service
		cerver_teardown (service)

class TestRoutes:

	def test_first_api_with_children (self, cerver):
		http_cerver = http_cerver_get (cerver)
		handler = http_handler (_handler)

		parent = http_create_route (http_cerver, REQUEST_METHOD_GET, "legacy", handler)
		http_create_child_route (parent, REQUEST_METHOD_GET, "child", handler)

		assert {("GET", "/legacy"), ("GET", "/legacy/child")} <= _endpoints (http_cerver)

	def test_head_and_options (self, cerver):
		http_cerver = http_cerver_get (cerver)
		api = http_group (http_cerver, "api/items", REQUEST_METHOD_GET, _handler)
		api.head ("probe") (_handler)
		api.options ("probe") (_handler)

		assert {("GET", "/api/items"), ("HEAD", "/api/items/probe"), ("OPTIONS", "/api/items/probe")} <= _endpoints (http_cerver)

	def test_group_class_root (self, cerver):
		api = HttpGroup.create (http_cerver_get (cerver), "api/root")
		assert api.root (REQUEST_METHOD_GET, _handler)
