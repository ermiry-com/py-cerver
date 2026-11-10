"""Many requests, one worker thread: the handlers of the requests push their work to a handlers
queue and wait for it, so a resource that is not thread safe (like a model) is only used by the
thread of the queue, while the cerver keeps several threads for the requests.

	python3 examples/workers/handlers.py
	curl -X POST http://localhost:8080/api/predict -d '{"values": [1, 2, 3]}'
"""

import os
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.callbacks import callback_wrap
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_BAD_REQUEST
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_request_get_body_json, validate_body_list, http_response_json_send
from cerver.threads import JOB_QUEUE_TYPE_HANDLERS, JobQueueHandler
from cerver.threads import job_queue_create, job_queue_set_handler, job_queue_start
from cerver.threads import job_queue_stop, job_queue_delete, job_handler_wait, job_queue_stats

SERVICE_NAME = "queue"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))
SERVICE_THREADS = 8

VALUES_MAXIMUM = 1024

class Model:
	"""A resource that only the thread of the queue uses."""

	def __init__ (self):
		self.runs = 0

	def predict (self, values: list) -> float:
		self.runs += 1
		return sum (values) / len (values)

model = Model ()

def predict_work (work: dict) -> None:
	"""Runs in the thread of the queue, the request waits until it returns."""
	work["result"] = model.predict (work["values"])

def register (http_cerver: int, queue: int) -> None:
	api = http_group (http_cerver, "api")

	@api.post ("/predict")
	def predict (http_receive, request):
		errors = {}
		values = validate_body_list (
			http_request_get_body_json (request) or {}, "values", errors,
			item=float, min_items=1, max_items=VALUES_MAXIMUM
		)

		if (errors):
			http_response_json_send (http_receive, HTTP_STATUS_BAD_REQUEST, {"errors": errors})

		else:
			work = {"values": values, "result": None}
			job_handler_wait (queue, work, None)

			http_response_json_send (http_receive, HTTP_STATUS_OK, {
				"prediction": work["result"], "runs": model.runs, "queued": job_queue_stats (queue)["total_jobs"]
			})

def main () -> int:
	cerver_init ()

	queue = job_queue_create (JOB_QUEUE_TYPE_HANDLERS)
	job_queue_set_handler (queue, callback_wrap (predict_work, JobQueueHandler))
	job_queue_start (queue)

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT, n_threads=SERVICE_THREADS)
	register (http_cerver_get (service), queue)

	result = cerver_run (service)

	job_queue_stop (queue)
	job_queue_delete (queue)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
