"""Helpers of the package that do not call cerver."""

import sys

__all__ = [
	"printf", "strtobool"
]

TRUE_VALUES = ("y", "yes", "t", "true", "on", "1")
FALSE_VALUES = ("n", "no", "f", "false", "off", "0")

def printf (format: str, *args) -> None:
	"""Writes a message with a printf like format to stdout.

	Args:
		format: The format, with % conversions.
		*args: The values of the conversions.
	"""
	sys.stdout.write (format % args)

def strtobool (value: str) -> int:
	"""Converts the text of a truth value into 1 or 0.

	Args:
		value: 'y', 'yes', 't', 'true', 'on' or '1' for true; 'n', 'no', 'f', 'false',
			'off' or '0' for false, in any case.

	Returns:
		1 for a true value, 0 for a false one.

	Raises:
		ValueError: If the value is not one of them.
	"""
	result = None

	lowered = value.lower ()
	if (lowered in TRUE_VALUES):
		result = 1

	elif (lowered in FALSE_VALUES):
		result = 0

	else:
		raise ValueError (f"invalid truth value {value!r}")

	return result
