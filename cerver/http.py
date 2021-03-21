from ctypes import c_uint8, c_void_p, c_char_p, c_bool, CFUNCTYPE

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
# sets the jwt algorithm used for encoding & decoding jwt tokens
# the default value is JWT_ALG_HS256
http_cerver_route_register = lib.http_cerver_route_register
http_cerver_route_register.argtypes = [c_void_p, jwt_alg_t]

# sets the filename from where the jwt private key will be loaded
http_cerver_auth_set_jwt_priv_key_filename = lib.http_cerver_auth_set_jwt_priv_key_filename
http_cerver_auth_set_jwt_priv_key_filename.argtypes = [c_void_p, c_char_p]

# sets the filename from where the jwt public key will be loaded
http_cerver_auth_set_jwt_pub_key_filename = lib.http_cerver_auth_set_jwt_pub_key_filename
http_cerver_auth_set_jwt_pub_key_filename.argtypes = [c_void_p, c_char_p]

# stats
http_cerver_all_stats_print = lib.http_cerver_all_stats_print
http_cerver_all_stats_print.argtypes = [c_void_p]
