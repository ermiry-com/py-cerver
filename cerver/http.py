from ctypes import c_void_p, c_char_p, CFUNCTYPE

from .lib import lib

from .alg import jwt_alg_t

UploadsFilenameGenerator = CFUNCTYPE (None, c_void_p, c_char_p, c_char_p)

# main
http_cerver_get = lib.http_cerver_get
http_cerver_get.argtypes = [c_void_p]
http_cerver_get.restype = c_void_p

# stats
http_cerver_all_stats_print = lib.http_cerver_all_stats_print
http_cerver_all_stats_print.argtypes = [c_void_p]

# public
http_cerver_static_path_add = lib.http_cerver_static_path_add
http_cerver_static_path_add.argtypes = [c_void_p, c_char_p]
http_cerver_static_path_add.restype = c_void_p

# routes
http_cerver_route_register = lib.http_cerver_route_register
http_cerver_route_register.argtypes = [c_void_p, c_void_p]

# uploads
http_cerver_set_uploads_path = lib.http_cerver_set_uploads_path
http_cerver_set_uploads_path.argtypes = [c_void_p, c_char_p]

http_cerver_set_uploads_filename_generator = lib.http_cerver_set_uploads_filename_generator
http_cerver_set_uploads_filename_generator.argtypes = [c_void_p, UploadsFilenameGenerator]

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
