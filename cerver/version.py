from .lib import lib

from .utils.log import LOG_TYPE_NONE, cerver_log_both

PYCERVER_VERSION = "0.8.8"
PYCERVER_VERSION_NAME = "Version 0.8.8"
PYCERVER_VERSION_DATE = "23/11/2021"
PYCERVER_VERSION_TIME = "21:08 CST"
PYCERVER_VERSION_AUTHOR = "Erick Salas"

version = {
	"id": PYCERVER_VERSION,
	"name": PYCERVER_VERSION_NAME,
	"date": PYCERVER_VERSION_DATE,
	"time": PYCERVER_VERSION_TIME,
	"author": PYCERVER_VERSION_AUTHOR
}

cerver_version_print_full = lib.cerver_version_print_full
cerver_version_print_version_id = lib.cerver_version_print_version_id
cerver_version_print_version_name = lib.cerver_version_print_version_name

def pycerver_version_print_full ():
	output = "\nPyCerver Version: {name}\n" \
		"Release Date: {date} - {time}\n" \
		"Author: {author}\n".format (**version)

	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		output.encode ("utf-8")
	)

def pycerver_version_print_version_id ():
	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		f"\nPyCerver Version ID: {version.id}\n".encode ("utf-8")
	)

def pycerver_version_print_version_name ():
	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		f"\nPyCerver Version: {version.name}\n".encode ("utf-8")
	)
