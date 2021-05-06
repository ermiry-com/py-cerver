from ctypes import c_int, c_char_p, c_bool

from .lib import lib

ImageType = c_int

IMAGE_TYPE_NONE = 0
IMAGE_TYPE_PNG = 1
IMAGE_TYPE_JPEG = 2
IMAGE_TYPE_GIF = 3
IMAGE_TYPE_BMP = 4

files_image_type_to_string = lib.files_image_type_to_string
files_image_type_to_string.argtypes = [ImageType]
files_image_type_to_string.restype = c_char_p

# opens the file and returns the file's image type
files_image_get_type = lib.files_image_get_type
files_image_get_type.argtypes = [c_char_p]
files_image_get_type.restype = ImageType

# returns the correct image type based on the filename's extension
files_image_get_type_by_extension = lib.files_image_get_type_by_extension
files_image_get_type_by_extension.argtypes = [c_char_p]
files_image_get_type_by_extension.restype = ImageType

# returns true if the filename's extension is jpg or jpeg
files_image_extension_is_jpeg = lib.files_image_extension_is_jpeg
files_image_extension_is_jpeg.argtypes = [c_char_p]
files_image_extension_is_jpeg.restype = c_bool

# returns true if the filename's extension is png
files_image_extension_is_png = lib.files_image_extension_is_png
files_image_extension_is_png.argtypes = [c_char_p]
files_image_extension_is_png.restype = c_bool
