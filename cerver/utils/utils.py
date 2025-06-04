import sys

def printf (format, *args):
	sys.stdout.write (format % args)

def strtobool (value: str) -> int:
	"""Convert a string representation of truth to true (1) or false (0).

	True values are 'y', 'yes', 't', 'true', 'on', and '1'; false values
	are 'n', 'no', 'f', 'false', 'off', and '0'.  Raises ValueError if
	'val' is anything else.
	"""
	value = value.lower ()
	if value in ("y", "yes", "t", "true", "on", "1"):
		return 1
	elif value in ("n", "no", "f", "false", "off", "0"):
		return 0
	else:
		raise ValueError ("invalid truth value {!r}".format(value))
