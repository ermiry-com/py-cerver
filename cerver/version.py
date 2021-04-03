from .lib import lib

from .utils.log import LOG_TYPE_NONE, cerver_log_both

PYCERVER_VERSION					= "0.5".encode ('utf-8')
PYCERVER_VERSION_NAME				= "Version 0.5".encode ('utf-8')
PYCERVER_VERSION_DATE				= "02/04/2021".encode ('utf-8')
PYCERVER_VERSION_TIME				= "22:05 CST".encode ('utf-8')
PYCERVER_VERSION_AUTHOR				= "Erick Salas".encode ('utf-8')

cerver_version_print_full = lib.cerver_version_print_full
cerver_version_print_version_id = lib.cerver_version_print_version_id
cerver_version_print_version_name = lib.cerver_version_print_version_name

def pycerver_version_print_full ():
	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		"\nPyCerver Version: %s".encode ('utf-8'), PYCERVER_VERSION_NAME
	)

	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		"Release Date & time: %s - %s".encode ('utf-8'),
		PYCERVER_VERSION_DATE, PYCERVER_VERSION_TIME
	)

	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		"Author: %s\n".encode ('utf-8'),
		PYCERVER_VERSION_AUTHOR
	)

def cerver_version_print_version_id ():
	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		"\nPyCerver Version ID: %s\n".encode ('utf-8'),
		PYCERVER_VERSION
	)

def cerver_version_print_version_name ():
	cerver_log_both (
		LOG_TYPE_NONE, LOG_TYPE_NONE,
		"\nPyCerver Version: %s\n".encode ('utf-8'),
		PYCERVER_VERSION_NAME
	)
