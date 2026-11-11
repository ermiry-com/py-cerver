"""The histograms of cerver: the count, total, min, max and distribution of a value."""

from ctypes import POINTER, Structure
from ctypes import c_char_p, c_double, c_uint, c_uint64
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"HISTOGRAM_MAX_EXPONENT", "HISTOGRAM_BUCKETS",
	"Histogram", "HistogramPointer",
	"histogram_init", "histogram_bucket", "histogram_add", "histogram_copy",
	"histogram_mean", "histogram_min", "histogram_print"
]

# buckets[i] counts the values up to 2^i,
# the last bucket counts the ones bigger than 2^HISTOGRAM_MAX_EXPONENT
HISTOGRAM_MAX_EXPONENT = 20
HISTOGRAM_BUCKETS = HISTOGRAM_MAX_EXPONENT + 2

class Histogram (Structure):
	"""The count, total, min, max and distribution of a value, like microseconds or bytes, ``Histogram``.

	Attributes:
		count: The number of values.
		total: Their sum.
		min: The min, the max of u64 without values (histogram_min () returns 0 then).
		max: The max.
		buckets: buckets[i] counts the values up to 2^i, the last one the bigger ones.
	"""

	_fields_ = [
		("count", c_uint64),
		("total", c_uint64),
		("min", c_uint64),
		("max", c_uint64),

		("buckets", c_uint64 * HISTOGRAM_BUCKETS)
	]

HistogramPointer: TypeAlias = POINTER (Histogram) # type: ignore

histogram_init = lib_function (
	"histogram_init", [HistogramPointer], None,
	"""Sets the histogram without values.

	Args:
		histogram: The Histogram.
	"""
)

histogram_bucket = lib_function (
	"histogram_bucket", [c_uint64], c_uint,
	"""Returns the bucket of a value.

	Args:
		value: The value.

	Returns:
		The index of its bucket.
	"""
)

histogram_add = lib_function (
	"histogram_add", [HistogramPointer, c_uint64], None,
	"""Adds a value to the histogram, with atomics.

	Args:
		histogram: The Histogram.
		value: The value.
	"""
)

histogram_copy = lib_function (
	"histogram_copy", [HistogramPointer, HistogramPointer], None,
	"""Copies the values of the histogram with atomic reads.

	Args:
		destination: The Histogram that gets the values.
		source: The Histogram to copy.
	"""
)

histogram_mean = lib_function (
	"histogram_mean", [HistogramPointer], c_double,
	"""Returns the mean of the values.

	Args:
		histogram: The Histogram.

	Returns:
		The mean, 0 without values.
	"""
)

histogram_min = lib_function (
	"histogram_min", [HistogramPointer], c_uint64,
	"""Returns the min of the values.

	Args:
		histogram: The Histogram.

	Returns:
		The min, 0 without values.
	"""
)

histogram_print = lib_function (
	"histogram_print", [c_char_p, c_char_p, HistogramPointer], None,
	"""Prints the histogram with the cerver log.

	Args:
		name: Its name, as bytes.
		unit: The unit of its values, as bytes.
		histogram: The Histogram.
	"""
)
