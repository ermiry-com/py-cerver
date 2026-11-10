"""JWTs: a login that signs a bearer token, and a group whose endpoints require it.

The key is generated at start in a temporary file and signs with HS256; with RS256 the private
key signs and the public key validates (openssl genrsa / openssl rsa -pubout).

	python3 examples/auth/tokens.py
	TOKEN=$(curl -s -X POST http://localhost:8080/api/login -d '{"username": "user"}' | jq -r .token)
	curl http://localhost:8080/api/profile -H "Authorization: $TOKEN"
	curl -i http://localhost:8080/api/profile                       # 401
"""

import os
import secrets
import sys
import tempfile
import time

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, HTTP_STATUS_BAD_REQUEST, HTTP_ROUTE_AUTH_TYPE_BEARER, JWT_ALG_HS256
from cerver.http import http_cerver_configuration, http_cerver_get, http_group, http_cerver_auth_configuration
from cerver.http import http_group_set_auth, http_group_set_decode_data_into_json
from cerver.http import http_request_get_body_json, http_request_get_decoded_json
from cerver.http import http_jwt_create_and_send, http_response_json_send, http_response_json_error_send

SERVICE_NAME = "tokens"
SERVICE_PORT = int (os.environ.get ("PORT", 8080))

KEY_BYTES = 64

def register (http_cerver: int) -> None:
	api = http_group (http_cerver, "api")

	@api.post ("/login")
	def login (http_receive, request):
		body = http_request_get_body_json (request) or {}
		username = body.get ("username")
		if (isinstance (username, str) and username):
			http_jwt_create_and_send (http_receive, HTTP_STATUS_OK, {
				"username": username, "admin": False, "issued": int (time.time ())
			})

		else:
			http_response_json_error_send (http_receive, HTTP_STATUS_BAD_REQUEST, b"Missing username!")

	private = http_group (http_cerver, "api/profile")
	http_group_set_auth (private.group, HTTP_ROUTE_AUTH_TYPE_BEARER)
	http_group_set_decode_data_into_json (private.group)

	@private.get ("/")
	def profile (http_receive, request):
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"token": http_request_get_decoded_json (request)})

def main () -> int:
	cerver_init ()

	with tempfile.NamedTemporaryFile ("wb", suffix=".key", delete=False) as key:
		key.write (secrets.token_hex (KEY_BYTES).encode ("utf-8"))

	service = http_cerver_configuration (SERVICE_NAME, port=SERVICE_PORT)
	http_cerver = http_cerver_get (service)

	# with HS256 the same secret signs and validates
	http_cerver_auth_configuration (http_cerver, JWT_ALG_HS256, key.name, key.name)

	register (http_cerver)

	result = cerver_run (service)

	os.unlink (key.name)
	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
