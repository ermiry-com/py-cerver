"""The metrics of an HTTP cerver in the text format of Prometheus."""

from ctypes import c_void_p

from ...lib import lib_function

from ...types.string import StringPointer, string_take_text

__all__ = [
	"http_cerver_metrics_generate", "http_cerver_metrics"
]

http_cerver_metrics_generate = lib_function (
	"http_cerver_metrics_generate", [c_void_p], StringPointer,
	"""Generates the metrics of an HTTP cerver, the body of GET /cerver/metrics.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		A new StringPointer, NULL on error.
	"""
)

def http_cerver_metrics (http_cerver: int) -> str | None:
	"""Returns the metrics of an HTTP cerver in the text format of Prometheus.

	Args:
		http_cerver: The HttpCerver.

	Returns:
		The metrics, None on error.
	"""
	return string_take_text (http_cerver_metrics_generate (http_cerver))
