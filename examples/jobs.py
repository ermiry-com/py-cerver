import os, signal, sys
import time
import ctypes

import cerver
import cerver.threads

web_cerver = None
job_queue = None

# end
def end (signum, frame):
	# cerver.cerver_stats_print (web_cerver, False, False)
	cerver.http_cerver_all_stats_print (cerver.http_cerver_get (web_cerver))
	cerver.cerver_teardown (web_cerver)
	cerver.cerver_end ()
	sys.exit ("Done!")

@ctypes.CFUNCTYPE (None, ctypes.c_void_p)
def custom_handler_method (job_handler):
	print ("custom_handler_method ()")
	time.sleep (1)

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	cerver.http_response_json_msg_send (
		http_receive, 200, "Main handler!".encode ('utf-8')
	)

# GET /jobs
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def jobs_handler (http_receive, request):
	global job_queue
	cerver.threads.job_handler_wait (job_queue, None, None)

	cerver.http_response_json_msg_send (
		http_receive, 200, "Jobs route works!".encode ('utf-8')
	)

def start ():
	global web_cerver
	global job_queue

	web_cerver = cerver.cerver_create_web (
		"web-cerver".encode ('utf-8'), 8080, 10
	)

	# main configuration
	cerver.cerver_set_receive_buffer_size (web_cerver, 4096);
	cerver.cerver_set_thpool_n_threads (web_cerver, 4);
	cerver.cerver_set_handler_type (web_cerver, cerver.CERVER_HANDLER_TYPE_THREADS);

	cerver.cerver_set_reusable_address_flags (web_cerver, True);

	# HTTP configuration
	http_cerver = cerver.http_cerver_get (web_cerver)

	# GET /
	main_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "/".encode ('utf-8'), main_handler)
	cerver.http_cerver_route_register (http_cerver, main_route)

	# GET /jobs
	jobs_route = cerver.http_route_create (cerver.REQUEST_METHOD_GET, "jobs".encode ('utf-8'), jobs_handler)
	cerver.http_cerver_route_register (http_cerver, jobs_route)

	# job queue
	job_queue = cerver.threads.job_queue_create (cerver.threads.JOB_QUEUE_TYPE_HANDLERS)
	cerver.threads.job_queue_set_handler (job_queue, custom_handler_method)
	cerver.threads.job_queue_start (job_queue)

	# start
	cerver.cerver_start (web_cerver)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver.cerver_init ()

	cerver.cerver_version_print_full ()

	start ()
