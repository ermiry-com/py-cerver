"""The values of the host and of this process: file systems, memory, load, cpu, host name and resources."""

from ctypes import POINTER, Structure
from ctypes import c_bool, c_char_p, c_double, c_size_t, c_uint, c_uint64, c_ulong
from ctypes import byref, create_string_buffer
from typing import TypeAlias

from ..lib import lib_function, lib_text

__all__ = [
	"SYSTEM_LOADS", "SYSTEM_HOSTNAME_SIZE",
	"FileSystemStats", "FileSystemStatsPointer",
	"SystemMemory", "SystemMemoryPointer", "SystemLoad", "SystemLoadPointer",
	"SystemCpuSample", "SystemCpuSamplePointer", "SystemProcess", "SystemProcessPointer",
	"system_get_available_space", "system_get_used_space", "system_get_stats", "system_print_stats",
	"system_get_memory", "system_print_memory", "system_get_load", "system_print_load",
	"system_cpu_sample", "system_cpu_usage", "system_get_hostname",
	"system_get_process", "system_print_process",
	"system_hostname", "system_memory"
]

SYSTEM_LOADS = 3
SYSTEM_HOSTNAME_SIZE = 256

class FileSystemStats (Structure):
	"""The space of a file system in bytes, ``FileSystemStats``."""

	_fields_ = [
		("total", c_double),
		("available", c_double),
		("used", c_double),
		("used_percentage", c_double)
	]

FileSystemStatsPointer: TypeAlias = POINTER (FileSystemStats) # type: ignore

class SystemMemory (Structure):
	"""The memory of the host in bytes, from /proc/meminfo, ``SystemMemory``.

	Attributes:
		available: The memory that can be used without swapping.
	"""

	_fields_ = [
		("total", c_uint64),
		("free", c_uint64),
		("available", c_uint64),
		("swap_total", c_uint64),
		("swap_free", c_uint64)
	]

SystemMemoryPointer: TypeAlias = POINTER (SystemMemory) # type: ignore

class SystemLoad (Structure):
	"""The load of the host, from sysinfo (), ``SystemLoad``.

	Attributes:
		loads: The load averages of 1, 5 and 15 minutes.
		uptime: The seconds since the host started.
		processes: The processes of the host.
		cpus: The cpus that are online.
	"""

	_fields_ = [
		("loads", c_double * SYSTEM_LOADS),
		("uptime", c_uint64),
		("processes", c_uint),
		("cpus", c_uint)
	]

SystemLoadPointer: TypeAlias = POINTER (SystemLoad) # type: ignore

class SystemCpuSample (Structure):
	"""The cpu times of the host since it started, from /proc/stat, ``SystemCpuSample``."""

	_fields_ = [
		("busy", c_uint64),
		("total", c_uint64)
	]

SystemCpuSamplePointer: TypeAlias = POINTER (SystemCpuSample) # type: ignore

class SystemProcess (Structure):
	"""The resources of this process, from /proc/self, ``SystemProcess``.

	Attributes:
		resident: The resident memory in bytes.
		threads: The threads of the process.
		open_files: Its open file descriptors.
	"""

	_fields_ = [
		("resident", c_uint64),
		("threads", c_uint),
		("open_files", c_uint)
	]

SystemProcessPointer: TypeAlias = POINTER (SystemProcess) # type: ignore

system_get_available_space = lib_function (
	"system_get_available_space", [c_char_p, POINTER (c_ulong)], c_bool,
	"""Gets the available bytes of a file system.

	Args:
		path: A path of the file system, as bytes.
		available_space: A pointer to a c_ulong that gets the bytes.

	Returns:
		True on success.
	"""
)

system_get_used_space = lib_function (
	"system_get_used_space", [c_char_p, POINTER (c_ulong)], c_bool,
	"""Gets the used bytes of a file system.

	Args:
		path: A path of the file system, as bytes.
		used_space: A pointer to a c_ulong that gets the bytes.

	Returns:
		True on success.
	"""
)

system_get_stats = lib_function (
	"system_get_stats", [c_char_p, FileSystemStatsPointer], c_bool,
	"""Fills the stats of a file system.

	Args:
		path: A path of the file system, as bytes.
		stats: The FileSystemStats that gets the values.

	Returns:
		True on success.
	"""
)

system_print_stats = lib_function (
	"system_print_stats", [FileSystemStatsPointer], None,
	"""Prints the stats of a file system.

	Args:
		stats: The FileSystemStats.
	"""
)

system_get_memory = lib_function (
	"system_get_memory", [SystemMemoryPointer], c_bool,
	"""Fills the memory of the host.

	Args:
		memory: The SystemMemory that gets the values.

	Returns:
		True on success.
	"""
)

system_print_memory = lib_function (
	"system_print_memory", [SystemMemoryPointer], None,
	"""Prints the memory of the host.

	Args:
		memory: The SystemMemory.
	"""
)

system_get_load = lib_function (
	"system_get_load", [SystemLoadPointer], c_bool,
	"""Fills the load of the host.

	Args:
		load: The SystemLoad that gets the values.

	Returns:
		True on success.
	"""
)

system_print_load = lib_function (
	"system_print_load", [SystemLoadPointer], None,
	"""Prints the load of the host.

	Args:
		load: The SystemLoad.
	"""
)

system_cpu_sample = lib_function (
	"system_cpu_sample", [SystemCpuSamplePointer], c_bool,
	"""Takes a sample of the cpu times of the host.

	Args:
		sample: The SystemCpuSample that gets the values.

	Returns:
		True on success.
	"""
)

system_cpu_usage = lib_function (
	"system_cpu_usage", [SystemCpuSamplePointer, SystemCpuSamplePointer], c_double,
	"""Returns the percentage (0 to 100) of the cpu that was used between two samples.

	Args:
		first: The first SystemCpuSample.
		second: The second one.

	Returns:
		The percentage, 0 if the samples are equal or the second one is older.
	"""
)

system_get_hostname = lib_function (
	"system_get_hostname", [c_char_p, c_size_t], c_bool,
	"""Copies the name of the host.

	Args:
		hostname: A buffer (create_string_buffer ()) that gets the name with its NUL.
		size: The size of the buffer.

	Returns:
		True on success, False if it failed or the name does not fit (the buffer is left empty).
	"""
)

system_get_process = lib_function (
	"system_get_process", [SystemProcessPointer], c_bool,
	"""Fills the resources of this process.

	Args:
		process: The SystemProcess that gets the values.

	Returns:
		True on success.
	"""
)

system_print_process = lib_function (
	"system_print_process", [SystemProcessPointer], None,
	"""Prints the resources of this process.

	Args:
		process: The SystemProcess.
	"""
)

def system_hostname () -> str | None:
	"""Returns the name of the host.

	Returns:
		The name, None if it could not be read.
	"""
	result = None

	buffer = create_string_buffer (SYSTEM_HOSTNAME_SIZE)
	if (system_get_hostname (buffer, SYSTEM_HOSTNAME_SIZE)):
		result = lib_text (buffer.value)

	return result

def system_memory () -> SystemMemory | None:
	"""Returns the memory of the host.

	Returns:
		A SystemMemory, None if it could not be read.
	"""
	memory = SystemMemory ()

	return memory if (system_get_memory (byref (memory))) else None
