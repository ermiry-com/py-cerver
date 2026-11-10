"""The versions of pycerver and of the cerver that it wraps."""

from .lib import lib_function

from .utils.log import LOG_TYPE_NONE, cerver_log_both

__all__ = [
	"PYCERVER_VERSION", "PYCERVER_VERSION_NAME", "PYCERVER_VERSION_DATE",
	"PYCERVER_VERSION_TIME", "PYCERVER_VERSION_AUTHOR",
	"PYCERVER_CERVER_VERSION",
	"version",
	"cerver_version_print_full", "cerver_version_print_version_id",
	"cerver_version_print_version_name",
	"pycerver_version_print_full", "pycerver_version_print_version_id",
	"pycerver_version_print_version_name"
]

PYCERVER_VERSION = "1.0"
PYCERVER_VERSION_NAME = "Release 1.0"
PYCERVER_VERSION_DATE = "13/12/2025"
PYCERVER_VERSION_TIME = "17:23 CST"
PYCERVER_VERSION_AUTHOR = "Erick Salas"

# the version of cerver whose API this release binds
PYCERVER_CERVER_VERSION = "2.0b-64"

version = {
	"id": PYCERVER_VERSION,
	"name": PYCERVER_VERSION_NAME,
	"date": PYCERVER_VERSION_DATE,
	"time": PYCERVER_VERSION_TIME,
	"author": PYCERVER_VERSION_AUTHOR,
	"cerver": PYCERVER_CERVER_VERSION
}

cerver_version_print_full = lib_function (
	"cerver_version_print_full", [], None,
	"""Prints the version of cerver with its date and its author."""
)

cerver_version_print_version_id = lib_function (
	"cerver_version_print_version_id", [], None,
	"""Prints the version id of cerver."""
)

cerver_version_print_version_name = lib_function (
	"cerver_version_print_version_name", [], None,
	"""Prints the version name of cerver."""
)

def pycerver_version_print_full () -> None:
	"""Prints the version of pycerver with its date, its author and the version of cerver it binds."""
	output = (
		"\nPyCerver Version: {name}\n"
		"Release Date: {date} - {time}\n"
		"Author: {author}\n"
		"Cerver: {cerver}\n"
	).format (**version)

	cerver_log_both (LOG_TYPE_NONE, LOG_TYPE_NONE, output)

def pycerver_version_print_version_id () -> None:
	"""Prints the version id of pycerver."""
	cerver_log_both (LOG_TYPE_NONE, LOG_TYPE_NONE, f"\nPyCerver Version ID: {version['id']}\n")

def pycerver_version_print_version_name () -> None:
	"""Prints the version name of pycerver."""
	cerver_log_both (LOG_TYPE_NONE, LOG_TYPE_NONE, f"\nPyCerver Version: {version['name']}\n")
