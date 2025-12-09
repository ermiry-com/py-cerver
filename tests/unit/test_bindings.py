"""The bindings of the package agree with the prototypes of the headers of cerver.

Every function declared with lib_function () is compared with its prototype in
/usr/local/include/cerver (the headers of the libcerver of the image):

- the number of arguments, and that a variadic function has no argtypes
- the kind and the width of each argument and of the result: a pointer, a bool, a double,
  a struct by value or an integer of its bytes (a u64 bound as c_int is truncated, a pointer
  bound without its restype is read as 32 bits)
- that no binding is a CERVER_PRIVATE function, which can change at any time
- the coverage: every CERVER_EXPORT and CERVER_PUBLIC function of the headers that the
  package wraps is bound, unless it is excluded here with its reason
"""

import ctypes
import pytest
import re
from pathlib import Path

import cerver
from cerver.lib import lib_functions

pytestmark = [pytest.mark.unit]

HEADERS = Path ("/usr/local/include/cerver")

PROTOTYPE = re.compile (r"CERVER_(EXPORT|PUBLIC|PRIVATE)\s+([^;{}]+?)\s*\b(\w+)\s*\(([^;{}]*?)\)\s*;", re.DOTALL)

TYPEDEF_ENUM = re.compile (r"typedef\s+enum\s*\w*\s*\{[^}]*\}\s*(\w+)\s*;", re.DOTALL)
TYPEDEF_FUNCTION = re.compile (r"typedef\s+[^;()]*\(\s*\*\s*(\w+)\s*\)\s*\(", re.DOTALL)
TYPEDEF_INTEGER = re.compile (r"typedef\s+(u?int\d+_t|unsigned\s+char|u32|u64)\s+(\w+)\s*;")

# the headers whose functions the package wraps (service + client)
INCLUDED_HEADERS = (
	"auth.h", "cerver.h", "client.h", "connection.h", "errors.h", "events.h", "files.h",
	"handler.h", "network.h", "packets.h", "socket.h", "timer.h", "udp.h", "version.h",
	"threads/bsem.h", "threads/jobs.h", "threads/manager.h", "threads/thpool.h",
	"threads/thread.h", "threads/worker.h",
	"utils/log.h",
	"http/auth.h", "http/compression.h", "http/conditional.h", "http/content.h", "http/date.h",
	"http/headers.h", "http/http.h", "http/method.h", "http/metrics.h", "http/middleware.h",
	"http/multipart.h", "http/origin.h", "http/proxy.h", "http/request.h", "http/response.h",
	"http/route.h", "http/status.h", "http/stream.h", "http/tree.h", "http/url.h", "http/utils.h",
	"http/validator.h", "http/jwt/alg.h"
)

# the functions of the included headers that are not bound, with their reason
EXCLUDED = {
	"files_get_from_dir": "returns a DoubleList, the collections are not bound",
	"file_get_lines": "returns a DoubleList, the collections are not bound",
	"file_open_as_file": "takes a struct stat and returns a FILE *, use open () of Python",
	"file_open_as_fd": "takes a struct stat, use os.open () of Python",
	"http_parse_query_into_pairs": "returns a DoubleList that is released with the collections",
	"http_route_stats_snapshot": "copies an HttpRouteStats, a struct that is not mirrored",
	"http_route_file_stats_snapshot": "copies an HttpRouteFileStats, a struct that is not mirrored"
}

# a C type of 1, 2, 4 or 8 bytes by its name, after the qualifiers are removed
INTEGER_WIDTHS = {
	"char": 1, "unsigned char": 1, "u8": 1, "i8": 1, "uchar": 1, "ascii_char": 1, "uint8_t": 1, "int8_t": 1,
	"short": 2, "unsigned short": 2, "u16": 2, "i16": 2, "in_port_t": 2, "uint16_t": 2, "int16_t": 2,
	"int": 4, "unsigned int": 4, "unsigned": 4, "u32": 4, "i32": 4, "int32_t": 4, "uint32_t": 4,
	"mode_t": 4, "socklen_t": 4, "ProtocolID": 4, "pid_t": 4,
	"long": 8, "unsigned long": 8, "u64": 8, "i64": 8, "size_t": 8, "ssize_t": 8, "time_t": 8,
	"pthread_t": 8, "uint64_t": 8, "int64_t": 8, "long long": 8
}

# the structs that are passed by value
STRUCT_VALUES = {"ProtocolVersion": 4, "PacketVersion": 8}

# the enums whose typedef is not a typedef enum { } Name
EXTRA_ENUMS = {"jwt_alg_t", "http_status", "http_header", "enum http_method"}

KIND_POINTER = "pointer"
KIND_BOOL = "bool"
KIND_DOUBLE = "double"
KIND_VOID = "void"
KIND_VARIADIC = "variadic"
KIND_STRUCT = "struct"
KIND_INTEGER = "integer"

QUALIFIERS = re.compile (r"\b(const|volatile|struct|enum)\b")

def header_texts () -> dict:
	"""path -> text of every header without its comments."""
	texts = {}
	for header in HEADERS.rglob ("*.h"):
		text = re.sub (r"/\*.*?\*/", "", header.read_text (), flags=re.DOTALL)
		texts[str (header.relative_to (HEADERS))] = re.sub (r"//[^\n]*", "", text)

	return texts

TEXTS = header_texts ()

ENUMS = set (EXTRA_ENUMS)
FUNCTION_TYPES = set ()
for text in TEXTS.values ():
	ENUMS.update (TYPEDEF_ENUM.findall (text))
	FUNCTION_TYPES.update (TYPEDEF_FUNCTION.findall (text))

def split_arguments (arguments: str) -> list:
	"""Splits the arguments of a prototype by its commas outside of parentheses."""
	parts, depth, current = [], 0, ""
	for character in arguments:
		if ((character == ",") and (depth == 0)):
			parts.append (current)
			current = ""

		else:
			depth += (character == "(") - (character == ")")
			current += character

	parts.append (current)

	return [" ".join (part.split ()) for part in parts if part.strip ()]

def argument_type (argument: str) -> str:
	"""Removes the name of an argument, keeping its type."""
	result = argument

	if ("(" not in argument) and ("[" not in argument):
		words = argument.replace ("*", " * ").split ()
		if ((len (words) > 1) and (words[-1] not in INTEGER_WIDTHS) and (words[-1] != "*")):
			result = " ".join (words[:-1])

	return result

def c_kind (c_type: str) -> tuple:
	"""Returns the kind and the width of a C type."""
	result = None

	clean = " ".join (QUALIFIERS.sub (" ", c_type).split ())
	enum_name = " ".join (c_type.replace ("const", " ").split ())

	if ((c_type == "...")):
		result = (KIND_VARIADIC, 0)

	elif (("*" in clean) or ("[" in clean) or ("(" in clean) or (clean in FUNCTION_TYPES)):
		result = (KIND_POINTER, 8)

	elif (clean == "void"):
		result = (KIND_VOID, 0)

	elif (clean == "bool"):
		result = (KIND_BOOL, 1)

	elif (clean in ("double", "float")):
		result = (KIND_DOUBLE, 8)

	elif (clean in STRUCT_VALUES):
		result = (KIND_STRUCT, STRUCT_VALUES[clean])

	elif ((clean in ENUMS) or (enum_name in ENUMS)):
		result = (KIND_INTEGER, 4)

	elif (clean in INTEGER_WIDTHS):
		result = (KIND_INTEGER, INTEGER_WIDTHS[clean])

	else:
		raise AssertionError (f"unknown C type {c_type!r}")

	return result

def ctypes_kind (ctype) -> tuple:
	"""Returns the kind and the width of a ctypes type."""
	result = None

	if (ctype is None):
		result = (KIND_VOID, 0)

	elif ((ctype in (ctypes.c_void_p, ctypes.c_char_p, ctypes.py_object))
		or (isinstance (ctype, type) and issubclass (ctype, (ctypes._Pointer, ctypes._CFuncPtr)))):
		result = (KIND_POINTER, 8)

	elif (ctype is ctypes.c_bool):
		result = (KIND_BOOL, 1)

	elif (ctype in (ctypes.c_double, ctypes.c_float)):
		result = (KIND_DOUBLE, 8)

	elif (isinstance (ctype, type) and issubclass (ctype, ctypes.Structure)):
		result = (KIND_STRUCT, ctypes.sizeof (ctype))

	else:
		result = (KIND_INTEGER, ctypes.sizeof (ctype))

	return result

def prototypes () -> dict:
	"""name -> (macro, header, result type, argument types) of every function of the headers."""
	found = {}
	for header, text in TEXTS.items ():
		for macro, result, name, arguments in PROTOTYPE.findall (text):
			types = [argument_type (argument) for argument in split_arguments (arguments)]
			if (types == ["void"]):
				types = []

			found[name] = (macro, header, " ".join (result.split ()), types)

	return found

PROTOTYPES = prototypes ()

PUBLIC_INCLUDED = sorted (
	name for name, (macro, header, _, _) in PROTOTYPES.items ()
	if ((macro != "PRIVATE") and (header in INCLUDED_HEADERS))
)

class TestBindings:

	def test_bindings_were_found (self):
		assert len (lib_functions) > 700

	def test_the_package_is_the_working_tree (self):
		assert cerver.__file__.startswith ("/home/pycerver")

	@pytest.mark.parametrize ("name", sorted (lib_functions))
	def test_symbol_has_a_prototype (self, name):
		assert name in PROTOTYPES

	@pytest.mark.parametrize ("name", sorted (name for name in lib_functions if (name in PROTOTYPES)))
	def test_is_not_private (self, name):
		assert PROTOTYPES[name][0] != "PRIVATE", f"{name} is CERVER_PRIVATE in {PROTOTYPES[name][1]}"

	@pytest.mark.parametrize ("name", sorted (name for name in lib_functions if (name in PROTOTYPES)))
	def test_result_agrees_with_the_prototype (self, name):
		_, _, result, _ = PROTOTYPES[name]
		assert ctypes_kind (lib_functions[name].restype) == c_kind (result), f"{name} returns {result}"

	@pytest.mark.parametrize ("name", sorted (name for name in lib_functions if (name in PROTOTYPES)))
	def test_arguments_agree_with_the_prototype (self, name):
		_, _, _, arguments = PROTOTYPES[name]
		function = lib_functions[name]

		if ("..." in arguments):
			assert function.argtypes is None, f"{name} is variadic"

		else:
			argtypes = function.argtypes or []
			assert len (argtypes) == len (arguments), f"{name} takes {arguments}"

			for position, (ctype, c_type) in enumerate (zip (argtypes, arguments)):
				assert ctypes_kind (ctype) == c_kind (c_type), f"{name} argument {position} is {c_type}"

	@pytest.mark.parametrize ("name", PUBLIC_INCLUDED)
	def test_public_function_is_bound (self, name):
		assert (name in lib_functions) or (name in EXCLUDED), f"{name} of {PROTOTYPES[name][1]} is not bound"

	@pytest.mark.parametrize ("name", sorted (EXCLUDED))
	def test_excluded_function_exists (self, name):
		assert name in PROTOTYPES
