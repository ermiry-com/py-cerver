import os, signal, sys
import time
import ctypes

from cerver import *
from cerver.http import *
from cerver.threads import *

worker_service = None
worker = None

next_id = 0

class Data ():
	def __init__ (self, id, value):
		self.id = id
		self.value = value

	def __del__ (self):
		print (f"Destroying data {self.id}...")

	def __str__ (self):
		return f'Data: \n\t{self.id} \n\t{self.value}'

def data_create (value):
	global next_id
	data = Data (next_id, value)
	next_id += 1

	return data

# end
def end (signum, frame):
	# cerver_stats_print (worker_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (worker_service))
	cerver_teardown (worker_service)
	cerver_end ()

	worker.end ()

	time.sleep (1)

	sys.exit ("Done!")

@ctypes.CFUNCTYPE (None, ctypes.py_object)
def custom_worker_method (data):
	print ("Doing work with data...")
	print (data)
	time.sleep (1)
	print ("Done working with data!")

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	http_response_json_key_value_send (
		http_receive, HTTP_STATUS_OK,
		b"oki", b"doki"
	)

# POST /work
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def worker_handler (http_receive, request):
	value = http_request_multi_parts_get_value (request, b"value")

	if (value):
		data = data_create (value)
		if (not worker.push (data)):
			http_response_json_key_value_send (
				http_receive, HTTP_STATUS_OK,
				b"oki", b"doki"
			)

		else:
			http_response_json_error_send (
				http_receive,
				HTTP_STATUS_INTERNAL_SERVER_ERROR,
				b"Failed to push to worker!"
			)

	else:
		http_response_json_error_send (
			http_receive,
			HTTP_STATUS_BAD_REQUEST,
			b"Missing values!"
		)

# GET /work/start
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def worker_start_handler (http_receive, request):
	if (not worker.resume ()):
		http_response_json_key_value_send (
			http_receive, HTTP_STATUS_OK,
			b"oki", b"doki"
		)

	else:
		http_response_json_error_send (
			http_receive,
			HTTP_STATUS_INTERNAL_SERVER_ERROR,
			b"Worker is running!"
		)

# GET /work/stop
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def worker_stop_handler (http_receive, request):
	if (not worker.stop ()):
		http_response_json_key_value_send (
			http_receive, HTTP_STATUS_OK,
			b"oki", b"doki"
		)

	else:
		http_response_json_error_send (
			http_receive,
			HTTP_STATUS_INTERNAL_SERVER_ERROR,
			b"Worker is NOT running!"
		)

def start ():
	global worker_service
	global worker

	worker_service = cerver_create_web (
		b"worker-service", 8080, 10
	)

	# main configuration
	cerver_set_receive_buffer_size (worker_service, 4096)
	cerver_set_thpool_n_threads (worker_service, 4)
	cerver_set_handler_type (worker_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (worker_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (worker_service)

	# GET /
	main_route = http_route_create (REQUEST_METHOD_GET, b"/", main_handler)
	http_cerver_route_register (http_cerver, main_route)

	# POST /worker
	worker_route = http_route_create (REQUEST_METHOD_POST, b"work", worker_handler)
	http_route_set_modifier (worker_route, HTTP_ROUTE_MODIFIER_MULTI_PART)
	http_cerver_route_register (http_cerver, worker_route)

	# GET /work/start
	worker_start_route = http_route_create (REQUEST_METHOD_GET, b"work/start", worker_start_handler)
	http_cerver_route_register (http_cerver, worker_start_route)

	# GET /work/stop
	worker_stop_route = http_route_create (REQUEST_METHOD_GET, b"work/stop", worker_stop_handler)
	http_cerver_route_register (http_cerver, worker_stop_route)

	# worker
	worker = Worker ("test", custom_worker_method)
	worker.start ()

	# HTTP admin configuration
	http_cerver_enable_admin_routes (http_cerver, True)
	http_cerver_register_admin_worker (http_cerver, worker.worker)

	# start
	cerver_start (worker_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
