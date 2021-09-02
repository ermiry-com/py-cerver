from ctypes import Structure, c_size_t, c_char_p

class String (Structure):
	_fields_ = [
		("max_len", c_size_t),
		("len", c_size_t),
		("str", c_char_p),
	]