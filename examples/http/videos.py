import os, signal, sys
import ctypes

from cerver import *
from cerver.http import *
from cerver.utils import *

videos_service = None

# end
def end (signum, frame):
	# cerver_stats_print (videos_service, False, False)
	http_cerver_all_stats_print (http_cerver_get (videos_service))
	cerver_teardown (videos_service)
	cerver_end ()
	sys.exit ("Done!")

# GET /
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler (http_receive, request):
	if (http_response_send_file (
		http_receive, HTTP_STATUS_OK,
		b"./examples/http/public/video.html"
	)):
		cerver_log_error (
			b"Failed to send ./examples/http/public/video.html"
		)

# GET /video
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def video_handler (http_receive, request):
	http_response_handle_video (http_receive, b"./data/videos/redis.webm")

def start ():
	global videos_service
	videos_service = cerver_create_web (
		b"videos-service", 5000, 10
	)

	# main configuration
	cerver_set_alias (videos_service, b"videos")

	cerver_set_receive_buffer_size (videos_service, 4096)
	cerver_set_thpool_n_threads (videos_service, 4)
	cerver_set_handler_type (videos_service, CERVER_HANDLER_TYPE_THREADS)

	cerver_set_reusable_address_flags (videos_service, True)

	# HTTP configuration
	http_cerver = http_cerver_get (videos_service)

	http_cerver_static_path_add (http_cerver, b"./examples/http/public")

	# GET /
	main_route = http_route_create (REQUEST_METHOD_GET, b"/", main_handler)
	http_cerver_route_register (http_cerver, main_route)

	# GET /video
	video_route = http_route_create (REQUEST_METHOD_GET, b"video", video_handler)
	http_cerver_route_register (http_cerver, video_route)

	# start
	cerver_start (videos_service)

if __name__ == "__main__":
	signal.signal (signal.SIGINT, end)
	signal.signal (signal.SIGTERM, end)
	signal.signal (signal.SIGPIPE, signal.SIG_IGN)

	cerver_init ()

	cerver_version_print_full ()

	pycerver_version_print_full ()

	start ()
