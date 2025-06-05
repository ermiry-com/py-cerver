from ctypes import POINTER, Structure, c_size_t, c_char_p
from typing import TypeAlias

class String (Structure):
	_fields_ = [
		("max_len", c_size_t),
		("len", c_size_t),
		("str", c_char_p),
	]

StringPointer: TypeAlias = POINTER (String) # type: ignore
