from ctypes import c_uint8, c_void_p, c_char_p, c_bool, c_int, c_size_t, CFUNCTYPE, POINTER

from .lib import lib

from .types.string import String

from .alg import jwt_alg_t
from .route import HttpRouteAuthType

# types
CatchAllHandler = CFUNCTYPE (None, c_void_p, c_void_p)
NotFoundHandler = CFUNCTYPE (None, c_void_p, c_void_p)
UploadsFilenameGenerator = CFUNCTYPE (None, c_void_p, c_char_p, c_char_p)
UploadsDirnameGenerator = CFUNCTYPE (POINTER (String), c_void_p)

# main
http_cerver_get = lib.http_cerver_get
http_cerver_get.argtypes = [c_void_p]
http_cerver_get.restype = c_void_p

# public
http_static_path_set_auth = lib.http_static_path_set_auth
http_static_path_set_auth.argtypes = [c_void_p, HttpRouteAuthType]

http_cerver_static_path_add = lib.http_cerver_static_path_add
http_cerver_static_path_add.argtypes = [c_void_p, c_char_p]
http_cerver_static_path_add.restype = c_void_p

http_receive_public_path_remove = lib.http_receive_public_path_remove
http_receive_public_path_remove.argtypes = [c_void_p, c_char_p]
http_receive_public_path_remove.restype = c_uint8

# routes
http_cerver_set_main_route = lib.http_cerver_set_main_route
http_cerver_set_main_route.argtypes = [c_void_p, c_void_p]

http_cerver_route_register = lib.http_cerver_route_register
http_cerver_route_register.argtypes = [c_void_p, c_void_p]

http_cerver_set_catch_all_route = lib.http_cerver_set_catch_all_route
http_cerver_set_catch_all_route.argtypes = [c_void_p, CatchAllHandler]

http_cerver_set_not_found_handler = lib.http_cerver_set_not_found_handler
http_cerver_set_not_found_handler.argtypes = [c_void_p]

http_cerver_set_not_found_route = lib.http_cerver_set_not_found_route
http_cerver_set_not_found_route.argtypes = [c_void_p, NotFoundHandler]

# uploads
http_cerver_set_uploads_path = lib.http_cerver_set_uploads_path
http_cerver_set_uploads_path.argtypes = [c_void_p, c_char_p]

http_cerver_set_uploads_filename_generator = lib.http_cerver_set_uploads_filename_generator
http_cerver_set_uploads_filename_generator.argtypes = [c_void_p, UploadsFilenameGenerator]

http_cerver_set_uploads_dirname_generator = lib.http_cerver_set_uploads_dirname_generator
http_cerver_set_uploads_dirname_generator.argtypes = [c_void_p, UploadsDirnameGenerator]

http_cerver_set_uploads_delete_when_done = lib.http_cerver_set_uploads_delete_when_done
http_cerver_set_uploads_delete_when_done.argtypes = [c_void_p, c_bool]

# auth
http_jwt_get_bearer = lib.http_jwt_get_bearer
http_jwt_get_bearer.argtypes = [c_void_p]
http_jwt_get_bearer.restype = c_char_p

http_jwt_get_bearer_len = lib.http_jwt_get_bearer_len
http_jwt_get_bearer_len.argtypes = [c_void_p]
http_jwt_get_bearer_len.restype = c_size_t

http_jwt_get_json = lib.http_jwt_get_json
http_jwt_get_json.argtypes = [c_void_p]
http_jwt_get_json.restype = c_char_p

http_jwt_get_json_len = lib.http_jwt_get_json_len
http_jwt_get_json_len.argtypes = [c_void_p]
http_jwt_get_json_len.restype = c_size_t

# sets the jwt algorithm used for encoding & decoding jwt tokens
# the default value is JWT_ALG_HS256
http_cerver_auth_set_jwt_algorithm = lib.http_cerver_auth_set_jwt_algorithm
http_cerver_auth_set_jwt_algorithm.argtypes = [c_void_p, jwt_alg_t]

# sets the filename from where the jwt private key will be loaded
http_cerver_auth_set_jwt_priv_key_filename = lib.http_cerver_auth_set_jwt_priv_key_filename
http_cerver_auth_set_jwt_priv_key_filename.argtypes = [c_void_p, c_char_p]

# sets the filename from where the jwt public key will be loaded
http_cerver_auth_set_jwt_pub_key_filename = lib.http_cerver_auth_set_jwt_pub_key_filename
http_cerver_auth_set_jwt_pub_key_filename.argtypes = [c_void_p, c_char_p]

http_cerver_auth_jwt_new = lib.http_cerver_auth_jwt_new
http_cerver_auth_jwt_new.restype = c_void_p

http_cerver_auth_jwt_delete = lib.http_cerver_auth_jwt_delete
http_cerver_auth_jwt_delete.argtypes = [c_void_p]

http_cerver_auth_jwt_add_value = lib.http_cerver_auth_jwt_add_value
http_cerver_auth_jwt_add_value.argtypes = [c_void_p, c_char_p, c_char_p]

http_cerver_auth_jwt_add_value_bool = lib.http_cerver_auth_jwt_add_value_bool
http_cerver_auth_jwt_add_value_bool.argtypes = [c_void_p, c_char_p, c_bool]

http_cerver_auth_jwt_add_value_int = lib.http_cerver_auth_jwt_add_value_int
http_cerver_auth_jwt_add_value_int.argtypes = [c_void_p, c_char_p, c_int]

http_cerver_auth_generate_bearer_jwt_json = lib.http_cerver_auth_generate_bearer_jwt_json
http_cerver_auth_generate_bearer_jwt_json.argtypes = [c_void_p, c_void_p]
http_cerver_auth_generate_bearer_jwt_json.restype = c_uint8

# stats
http_cerver_all_stats_print = lib.http_cerver_all_stats_print
http_cerver_all_stats_print.argtypes = [c_void_p]

# admin
http_cerver_enable_admin_routes = lib.http_cerver_enable_admin_routes
http_cerver_enable_admin_routes.argtypes = [c_void_p, c_bool]

# parser
http_query_pairs_get_value = lib.http_query_pairs_get_value
http_query_pairs_get_value.argtypes = [c_void_p, c_char_p]
http_query_pairs_get_value.restype = POINTER (String)

http_query_pairs_print = lib.http_query_pairs_print
http_query_pairs_print.argtypes = [c_void_p]

# handler
http_receive_get_cerver = lib.http_receive_get_cerver
http_receive_get_cerver.argtypes = [c_void_p]
http_receive_get_cerver.restype = c_void_p
