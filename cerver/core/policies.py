"""What a cerver does with its connections when it is full or when it is drained."""

from ctypes import c_void_p, c_char_p, c_int, c_uint32
from typing import TypeAlias

from ..lib import lib_function

__all__ = [
	"CerverOverloadPolicy",
	"CERVER_OVERLOAD_POLICY_NONE", "CERVER_OVERLOAD_POLICY_WAIT", "CERVER_OVERLOAD_POLICY_REJECT",
	"CERVER_DEFAULT_OVERLOAD_POLICY", "CERVER_DEFAULT_OVERLOAD_WAIT_TIMEOUT",
	"CerverDrainPolicy",
	"CERVER_DRAIN_POLICY_NONE", "CERVER_DRAIN_POLICY_RUN", "CERVER_DRAIN_POLICY_REJECT",
	"CERVER_DEFAULT_DRAIN_POLICY",
	"cerver_overload_policy_to_string", "cerver_overload_policy_description",
	"cerver_drain_policy_to_string", "cerver_drain_policy_description",
	"cerver_set_overload_policy", "cerver_set_overload_wait_timeout",
	"cerver_set_drain_policy", "cerver_set_drain_timeout"
]

# what happens with a new connection when the thpool queue is full
CerverOverloadPolicy: TypeAlias = c_int # type: ignore

CERVER_OVERLOAD_POLICY_NONE = 0
CERVER_OVERLOAD_POLICY_WAIT = 1
CERVER_OVERLOAD_POLICY_REJECT = 2

CERVER_DEFAULT_OVERLOAD_POLICY = CERVER_OVERLOAD_POLICY_WAIT

# the secs that a request of a cerver with CERVER_HANDLER_TYPE_EVENTS waits for a place in a full thpool
CERVER_DEFAULT_OVERLOAD_WAIT_TIMEOUT = 32

# what happens with the queued connections when the cerver is drained
CerverDrainPolicy: TypeAlias = c_int # type: ignore

CERVER_DRAIN_POLICY_NONE = 0
CERVER_DRAIN_POLICY_RUN = 1
CERVER_DRAIN_POLICY_REJECT = 2

CERVER_DEFAULT_DRAIN_POLICY = CERVER_DRAIN_POLICY_RUN

cerver_overload_policy_to_string = lib_function (
	"cerver_overload_policy_to_string", [CerverOverloadPolicy], c_char_p,
	"""Returns the name of an overload policy.

	Args:
		policy: A CERVER_OVERLOAD_POLICY_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_overload_policy_description = lib_function (
	"cerver_overload_policy_description", [CerverOverloadPolicy], c_char_p,
	"""Returns the description of an overload policy.

	Args:
		policy: A CERVER_OVERLOAD_POLICY_* value.

	Returns:
		The description, as bytes.
	"""
)

cerver_drain_policy_to_string = lib_function (
	"cerver_drain_policy_to_string", [CerverDrainPolicy], c_char_p,
	"""Returns the name of a drain policy.

	Args:
		policy: A CERVER_DRAIN_POLICY_* value.

	Returns:
		The name, as bytes.
	"""
)

cerver_drain_policy_description = lib_function (
	"cerver_drain_policy_description", [CerverDrainPolicy], c_char_p,
	"""Returns the description of a drain policy.

	Args:
		policy: A CERVER_DRAIN_POLICY_* value.

	Returns:
		The description, as bytes.
	"""
)

cerver_set_overload_policy = lib_function (
	"cerver_set_overload_policy", [c_void_p, CerverOverloadPolicy], None,
	"""Sets what happens with a new connection when the queue of the thpool is full.

	Args:
		cerver: The cerver.
		policy: CERVER_OVERLOAD_POLICY_WAIT (the default) stops accepting until there is space,
			CERVER_OVERLOAD_POLICY_REJECT closes the connection (503 in web cervers).
	"""
)

cerver_set_overload_wait_timeout = lib_function (
	"cerver_set_overload_wait_timeout", [c_void_p, c_uint32], None,
	"""Sets how long a request of a cerver with CERVER_HANDLER_TYPE_EVENTS waits for a place in a full thpool
	with CERVER_OVERLOAD_POLICY_WAIT.

	The request waits in its event loop without using a thread; when the time ends it is answered with 503
	and a Retry-After header. The other handler types ignore it: they stop accepting until there is space.

	Args:
		cerver: The cerver.
		seconds: The seconds, 0 answers 503 as soon as the thpool has no place,
			CERVER_DEFAULT_OVERLOAD_WAIT_TIMEOUT by default.
	"""
)

cerver_set_drain_policy = lib_function (
	"cerver_set_drain_policy", [c_void_p, CerverDrainPolicy], None,
	"""Sets what happens with the queued connections when the cerver is drained by cerver_teardown ().

	Args:
		cerver: The cerver.
		policy: CERVER_DRAIN_POLICY_RUN (the default) still handles them,
			CERVER_DRAIN_POLICY_REJECT rejects them (503 in web cervers).
	"""
)

cerver_set_drain_timeout = lib_function (
	"cerver_set_drain_timeout", [c_void_p, c_uint32], None,
	"""Sets the seconds that the cerver waits for its connections when it is drained.

	Args:
		cerver: The cerver.
		drain_timeout: The seconds, 0 waits for every connection, CERVER_DEFAULT_DRAIN_TIMEOUT by default.
	"""
)
