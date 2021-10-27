import os, signal, sys
import time
import ctypes

from cerver import *
from cerver.http import *
from cerver.threads import *

web_service = None
job_queue = None

class Data ():
	def __init__ (self, value):
		self.value = value
		self.result = None

# end
def end (signum, frame):
	# cerver_stats_print (web_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (web_service))
	cerver_teardown (web_service)
	cerver_end ()
	sys.exit ("Done!")

@ctypes.CFUNCTYPE (None, ctypes.py_object)
def custom_handler_method (data):
	print ("custom_handler_method ()")
	print (data.value)
	data.result = "Hello there!"
	time.sleep (1)

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, b"Main handler!"
	)

# POST /jobs
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def jobs_handler (http_receive, request):
	global job_queue

	value = http_request_multi_parts_get_value (
		request, b"value"
	)

	data = Data (value)

	job_handler_wait (job_queue, data, None)

	http_response_json_msg_send (
		http_receive, HTTP_STATUS_OK, data.result.encode ("utf-8")
	)

def start ():
	global web_service
	global job_queue

	web_service = cerver_create_web (
		b"web-service", 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (web_service, 4096)
	cerver_set_thpool_n_threads (web_service, 4)
	cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (web_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (web_service)

	# GET /
	main_route = http_route_create (REQUEST_METHOD_GET, b"/", main_handler)
	http_cerver_route_register (http_cerver, main_route)

	# POST /jobs
	jobs_route = http_route_create (REQUEST_METHOD_POST, b"jobs", jobs_handler)
	http_route_set_modifier (jobs_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, jobs_route)

	# job queue
	job_queue = job_queue_create (JOB_QUEUE_TYPE_HANDLERS)
	job_queue_set_handler (job_queue, custom_handler_method)
	job_queue_start (job_queue)

	# start
	cerver_start (web_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
