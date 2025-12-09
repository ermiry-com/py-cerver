"""Builders shared by the tiers of the suite."""

from ctypes import pointer

from cerver.types import String
from cerver.types import StringPointer

def build_string (content: bytes):
	"""A real cerver String with the content, as the getters of cerver return it."""
	return pointer (String (len (content), len (content), content))

def build_null_string ():
	"""The NULL String pointer that a getter of cerver returns for a missing value."""
	return StringPointer ()
