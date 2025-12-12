"""Background jobs: the requests are answered right away and their work runs in a worker
manager, that adds workers while the jobs wait and removes the idle ones.

	python3 examples/workers/manager.py
	curl -X POST http://localhost:8080/api/reports -d '{"name": "monthly", "urgent": true}'
	curl http://localhost:8080/api/reports/stats
"""

import os
import sys
import threading
import time
import uuid

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_ACCEPTED, HTTP_STATUS_BAD_REQUEST
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_request_get_body_json, validate_body_string, validate_body_bool
from cerver.http import http_response_json_send
from cerver.threads import WorkerManager, JOB_QUEUE_PRIORITY_HIGH, JOB_QUEUE_PRIORITY_NORMAL
from cerver.utils import cerver_log_success

SERVICE_NAME = "manager"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

WORKERS_MINIMUM = 1
WORKERS_MAXIMUM = 4

# the time that a report takes, in seconds
REPORT_SECONDS = 0.5

done = []
lock = threading.Lock ()

def report_build (report: dict) -> None:
	"""Runs in a thread of a worker of the manager."""
	time.sleep (REPORT_SECONDS)

	with lock:
		done.append (report["id"])

	cerver_log_success (f"Report {report['name']} ({report['id']}) is done")

def register (http_cerver: int, manager: WorkerManager) -> None:
	reports = http_group (http_cerver, "api/reports")

	@reports.post ("/")
	def report_create (http_receive, request):
		errors = {}
		body = http_request_get_body_json (request) or {}

		report = {
			"id": uuid.uuid4 ().hex,
			"name": validate_body_string (body, "name", errors),
			"urgent": validate_body_bool (body, "urgent", errors, required=False, default=False)
		}

		if (errors):
			http_response_json_send (http_receive, HTTP_STATUS_BAD_REQUEST, {"errors": errors})

		else:
			priority = JOB_QUEUE_PRIORITY_HIGH if (report["urgent"]) else JOB_QUEUE_PRIORITY_NORMAL
			manager.push (report, priority)
			http_response_json_send (http_receive, HTTP_STATUS_ACCEPTED, {"id": report["id"]})

	@reports.get ("/stats")
	def report_stats (http_receive, request):
		with lock:
			count = len (done)

		http_response_json_send (http_receive, HTTP_STATUS_OK, {"done": count, "manager": manager.stats ()})

def main () -> int:
	cerver_init ()

	manager = WorkerManager ("reports", report_build, min_workers=WORKERS_MINIMUM, max_workers=WORKERS_MAXIMUM)
	manager.start ()

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	register (http_cerver_get (service), manager)

	result = cerver_run (service)

	# the jobs that are still queued are released with the manager
	manager.delete ()

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
