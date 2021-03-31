import os, sys
import json
import ctypes
import cerver

api_cerver = None

def end (signum, frame):
    cerver.http_cerver_all_stats_print (cerver.http_cerver_get (api_cerver))
    cerver.cerver_teardown (api_cerver)
    cerver.cerver_end ()
    sys.exit ("Done!")

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def main_handler(http_receive, request):
    cerver.http_send (http_receive, cerver.HTTP_STATUS_OK, {"msg": "Wrapper works!"})

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def echo_handler(http_receive, request):
    body_values = cerver.http_request_get_query_params (request)
    value = cerver.http_request_get_query_value (body_values, "value")
    cerver.http_send (http_receive, cerver.HTTP_STATUS_OK, {"echo_says": f"Wrapper received: {value}"})

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def data_handler(http_receive, request):
    body = cerver.http_request_get_body_json (request)
    cerver.http_send (http_receive, cerver.HTTP_STATUS_OK, {"echo": body})


@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def token_handler(http_receive, request):
    body = cerver.http_request_get_body_json (request)
    cerver.http_jwt_sign_and_send(http_receive, cerver.HTTP_STATUS_OK, body)

@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def auth_handler(http_receive, request):
    token_values = cerver.http_jwt_token_decode(request)
    cerver.http_send(http_receive, cerver.HTTP_STATUS_OK, {"msg": "is authenticated",
        "token_values": token_values
    })

def start():
    global api_cerver

    api_cerver = cerver.cerver_main_http_configuration ()
    http_cerver = cerver.http_cerver_get(api_cerver)
    cerver.cerver_auth_http_configuration(http_cerver, cerver.JWT_ALG_RS256, "keys/key.key", "keys/key.pub")

    #GET /
    main_route = cerver.http_create_route(cerver.REQUEST_METHOD_GET, "/", main_handler, http_cerver = http_cerver)

    #GET /echo
    echo_route = cerver.http_create_route(cerver.REQUEST_METHOD_GET, "echo", echo_handler, main_route)

    #POST /data
    data_route = cerver.http_create_route(cerver.REQUEST_METHOD_POST, "data", data_handler, main_route)

    #POST /token
    token_route = cerver.http_create_route(cerver.REQUEST_METHOD_POST, "token", token_handler, main_route)

    #GET /auth
    auth_route = cerver.http_create_secure_route (cerver.REQUEST_METHOD_GET, "auth", auth_handler, main_route)

    cerver.cerver_start(api_cerver)

if __name__ == "__main__":
    cerver.cerver_initialize(end, True)

    start()