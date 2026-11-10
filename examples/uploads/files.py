"""Uploads: multipart requests whose files are saved in a directory for each request, a
validated image with a value, and the files that are deleted when the request ends.

	python3 examples/uploads/files.py
	curl -F "image=@photo.png" -F "title=A photo" http://localhost:8080/api/images
	curl -F "first=@a.txt" -F "second=@b.txt" http://localhost:8080/api/documents
"""

import os
import sys
import tempfile

from cerver import cerver_init, cerver_end, cerver_run, files_create_dir
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_CREATED, HTTP_STATUS_BAD_REQUEST
from cerver.http import HTTP_ROUTE_MODIFIER_MULTI_PART
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_cerver_set_uploads_path, http_cerver_set_uploads_delete_when_done
from cerver.http import http_cerver_set_default_uploads_dirname_generator
from cerver.http import http_cerver_set_default_uploads_filename_generator
from cerver.http import http_request_multi_parts, http_multi_part_get_file, http_multi_part_is_file
from cerver.http import http_request_multi_part_keep_files
from cerver.http import validate_mparts_file_is_image, validate_mparts_value
from cerver.http import http_response_json_send

SERVICE_NAME = "uploads"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

UPLOADS_PATH = os.environ.get ("UPLOADS_PATH", os.path.join (tempfile.gettempdir (), "pycerver-uploads"))
UPLOADS_MODE = 0o755

TITLE_MINIMUM = 1
TITLE_MAXIMUM = 64

def register (http_cerver: int) -> None:
	api = http_group (http_cerver, "api")

	@api.post ("/images", modifier=HTTP_ROUTE_MODIFIER_MULTI_PART)
	def image_upload (http_receive, request):
		errors = {}
		image = validate_mparts_file_is_image (request, "image", errors)
		title = validate_mparts_value (request, "title", TITLE_MINIMUM, TITLE_MAXIMUM, errors)

		if (errors):
			http_response_json_send (http_receive, HTTP_STATUS_BAD_REQUEST, {"errors": errors})

		else:
			# the image stays after the request, the other uploads are deleted
			http_request_multi_part_keep_files (request)
			http_response_json_send (http_receive, HTTP_STATUS_CREATED, {"title": title, "image": image})

	@api.post ("/documents", modifier=HTTP_ROUTE_MODIFIER_MULTI_PART)
	def documents_upload (http_receive, request):
		files = [
			http_multi_part_get_file (mpart)
			for mpart in http_request_multi_parts (request) if (http_multi_part_is_file (mpart))
		]

		http_response_json_send (http_receive, HTTP_STATUS_OK, {"files": files})

def main () -> int:
	cerver_init ()

	files_create_dir (UPLOADS_PATH.encode ("utf-8"), UPLOADS_MODE)

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	http_cerver_set_uploads_path (http_cerver, UPLOADS_PATH.encode ("utf-8"))
	http_cerver_set_default_uploads_dirname_generator (http_cerver)
	http_cerver_set_default_uploads_filename_generator (http_cerver)
	http_cerver_set_uploads_delete_when_done (http_cerver, True)

	register (http_cerver)

	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
