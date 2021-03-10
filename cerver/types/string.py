from ctypes import Structure, c_uint, c_char_p

class String (Structure):
	_fields_ = [
		("len", c_uint),
		("str", c_char_p),
	]