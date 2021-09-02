from ctypes import c_int, c_char_p, c_bool

from ..lib import lib

ContentType = c_int

HTTP_CONTENT_TYPE_NONE = 0
HTTP_CONTENT_TYPE_AAC = 1
HTTP_CONTENT_TYPE_ABIWORD = 2
HTTP_CONTENT_TYPE_ARCHIVE = 3
HTTP_CONTENT_TYPE_AVI = 4
HTTP_CONTENT_TYPE_KINDLE = 5
HTTP_CONTENT_TYPE_BIN = 6
HTTP_CONTENT_TYPE_BMP = 7
HTTP_CONTENT_TYPE_BZIP = 8
HTTP_CONTENT_TYPE_BZIP2 = 9
HTTP_CONTENT_TYPE_CSHELL = 10
HTTP_CONTENT_TYPE_CSS = 11
HTTP_CONTENT_TYPE_CSV = 12
HTTP_CONTENT_TYPE_DOC = 13
HTTP_CONTENT_TYPE_DOCX = 14
HTTP_CONTENT_TYPE_EOT = 15
HTTP_CONTENT_TYPE_EPUB = 16
HTTP_CONTENT_TYPE_GZIP = 17
HTTP_CONTENT_TYPE_GIF = 18
HTTP_CONTENT_TYPE_HTML = 19
HTTP_CONTENT_TYPE_ICO = 20
HTTP_CONTENT_TYPE_ICS = 21
HTTP_CONTENT_TYPE_JAR = 22
HTTP_CONTENT_TYPE_JPG = 23
HTTP_CONTENT_TYPE_JPEG = 24
HTTP_CONTENT_TYPE_JS = 25
HTTP_CONTENT_TYPE_JSON = 26
HTTP_CONTENT_TYPE_JSONLD = 27
HTTP_CONTENT_TYPE_MIDI = 28
HTTP_CONTENT_TYPE_MJS = 29
HTTP_CONTENT_TYPE_MP3 = 30
HTTP_CONTENT_TYPE_CDA = 31
HTTP_CONTENT_TYPE_MP4 = 32
HTTP_CONTENT_TYPE_MPEG = 33
HTTP_CONTENT_TYPE_MPKG = 34
HTTP_CONTENT_TYPE_ODP = 35
HTTP_CONTENT_TYPE_ODS = 36
HTTP_CONTENT_TYPE_ODT = 37
HTTP_CONTENT_TYPE_OGA = 38
HTTP_CONTENT_TYPE_OGV = 39
HTTP_CONTENT_TYPE_OGX = 40
HTTP_CONTENT_TYPE_OPUS = 41
HTTP_CONTENT_TYPE_OTF = 42
HTTP_CONTENT_TYPE_PNG = 43
HTTP_CONTENT_TYPE_PDF = 44
HTTP_CONTENT_TYPE_PHP = 45
HTTP_CONTENT_TYPE_PPT = 46
HTTP_CONTENT_TYPE_PPTX = 47
HTTP_CONTENT_TYPE_RAR = 48
HTTP_CONTENT_TYPE_RTF = 49
HTTP_CONTENT_TYPE_SHELL = 50
HTTP_CONTENT_TYPE_SVG = 51
HTTP_CONTENT_TYPE_SWF = 52
HTTP_CONTENT_TYPE_TAR = 53
HTTP_CONTENT_TYPE_TIFF = 54
HTTP_CONTENT_TYPE_TS = 55
HTTP_CONTENT_TYPE_TTF = 56
HTTP_CONTENT_TYPE_TXT = 57
HTTP_CONTENT_TYPE_VSD = 58
HTTP_CONTENT_TYPE_WAV = 59
HTTP_CONTENT_TYPE_WEBA = 60
HTTP_CONTENT_TYPE_WEBM = 61
HTTP_CONTENT_TYPE_WEBP = 62
HTTP_CONTENT_TYPE_WOFF = 63
HTTP_CONTENT_TYPE_WOFF2 = 64
HTTP_CONTENT_TYPE_XHTML = 65
HTTP_CONTENT_TYPE_XLS = 66
HTTP_CONTENT_TYPE_XLSX = 67
HTTP_CONTENT_TYPE_XML = 68
HTTP_CONTENT_TYPE_XUL = 69
HTTP_CONTENT_TYPE_ZIP = 70
HTTP_CONTENT_TYPE_3GP = 71
HTTP_CONTENT_TYPE_3G2 = 72
HTTP_CONTENT_TYPE_7Z = 73

http_content_type_extension = lib.http_content_type_extension
http_content_type_extension.argtypes = [ContentType]
http_content_type_extension.restype = c_char_p

http_content_type_description = lib.http_content_type_description
http_content_type_description.argtypes = [ContentType]
http_content_type_description.restype = c_char_p

http_content_type_mime = lib.http_content_type_mime
http_content_type_mime.argtypes = [ContentType]
http_content_type_mime.restype = c_char_p

http_content_type_by_mime = lib.http_content_type_by_mime
http_content_type_by_mime.argtypes = [c_char_p]
http_content_type_by_mime.restype = ContentType

http_content_type_by_extension = lib.http_content_type_by_extension
http_content_type_by_extension.argtypes = [c_char_p]
http_content_type_by_extension.restype = ContentType

http_content_type_mime_by_extension = lib.http_content_type_mime_by_extension
http_content_type_mime_by_extension.argtypes = [c_char_p]
http_content_type_mime_by_extension.restype = c_char_p

http_content_type_is_json = lib.http_content_type_is_json
http_content_type_is_json.argtypes = [c_char_p]
http_content_type_is_json.restype = c_bool

http_content_type_from_filename = lib.http_content_type_from_filename
http_content_type_from_filename.argtypes = [c_char_p]
http_content_type_from_filename.restype = ContentType
