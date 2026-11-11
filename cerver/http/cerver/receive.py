"""The HttpReceive of a request: the connection, the cerver and the endpoint that handle it."""

from ctypes import c_void_p, c_char_p, c_int, c_bool
from typing import TypeAlias

from ...lib import lib_function

__all__ = [
	"HttpReceiveStatus",
	"HTTP_RECEIVE_STATUS_NONE", "HTTP_RECEIVE_STATUS_HEADERS", "HTTP_RECEIVE_STATUS_BODY",
	"HTTP_RECEIVE_STATUS_COMPLETED", "HTTP_RECEIVE_STATUS_INCOMPLETED", "HTTP_RECEIVE_STATUS_UNHANDLED",
	"HTTP_RECEIVE_STATUS_TIMEOUT", "HTTP_RECEIVE_STATUS_CLOSED", "HTTP_RECEIVE_STATUS_PARSER_ERROR",
	"HTTP_RECEIVE_STATUS_LIMIT", "HTTP_RECEIVE_STATUS_REJECTED", "HTTP_RECEIVE_STATUS_UPLOAD_ERROR",
	"HTTP_RECEIVE_STATUS_RESPONSE_FAILED",
	"http_receive_status_str",
	"HttpStage",
	"HTTP_STAGE_QUEUED", "HTTP_STAGE_REQUEST_LINE", "HTTP_STAGE_HEADERS", "HTTP_STAGE_BODY",
	"HTTP_STAGE_UPLOAD", "HTTP_STAGE_HANDLER", "HTTP_STAGE_RESPONSE", "HTTP_STAGES",
	"http_stage_string", "http_stage_label",
	"HttpAbortReason",
	"HTTP_ABORT_REASON_CLOSED", "HTTP_ABORT_REASON_RESET", "HTTP_ABORT_REASONS",
	"http_abort_reason_string", "http_abort_reason_label",
	"HttpClientState",
	"HTTP_CLIENT_STATE_CONNECTED", "HTTP_CLIENT_STATE_CLOSED", "HTTP_CLIENT_STATE_RESET",
	"http_client_state_string",
	"http_receive_get_cerver_receive", "http_receive_get_sock_fd", "http_receive_get_cerver",
	"http_receive_get_endpoint", "http_receive_get_route_custom_data",
	"http_receive_get_cerver_custom_data", "http_receive_is_head", "http_receive_get_allow",
	"http_receive_get_stage", "http_receive_get_client_state", "http_receive_is_client_gone"
]

HttpReceiveStatus: TypeAlias = c_int # type: ignore

HTTP_RECEIVE_STATUS_NONE = 0
HTTP_RECEIVE_STATUS_HEADERS = 1
HTTP_RECEIVE_STATUS_BODY = 2
HTTP_RECEIVE_STATUS_COMPLETED = 3
HTTP_RECEIVE_STATUS_INCOMPLETED = 4
HTTP_RECEIVE_STATUS_UNHANDLED = 5
HTTP_RECEIVE_STATUS_TIMEOUT = 6
HTTP_RECEIVE_STATUS_CLOSED = 7
HTTP_RECEIVE_STATUS_PARSER_ERROR = 8
HTTP_RECEIVE_STATUS_LIMIT = 9
HTTP_RECEIVE_STATUS_REJECTED = 10
HTTP_RECEIVE_STATUS_UPLOAD_ERROR = 11

# the client left while its response was sent
HTTP_RECEIVE_STATUS_RESPONSE_FAILED = 12

http_receive_status_str = lib_function (
	"http_receive_status_str", [HttpReceiveStatus], c_char_p,
	"""Returns the name of a receive status.

	Args:
		status: An HTTP_RECEIVE_STATUS_* value.

	Returns:
		The name, as bytes.
	"""
)

# the stage of a request where cerver noticed that its client left
HttpStage: TypeAlias = c_int # type: ignore

HTTP_STAGE_QUEUED = 0
HTTP_STAGE_REQUEST_LINE = 1
HTTP_STAGE_HEADERS = 2
HTTP_STAGE_BODY = 3
HTTP_STAGE_UPLOAD = 4
HTTP_STAGE_HANDLER = 5
HTTP_STAGE_RESPONSE = 6

HTTP_STAGES = 7

http_stage_string = lib_function (
	"http_stage_string", [HttpStage], c_char_p,
	"""Returns the name of a stage.

	Args:
		stage: An HTTP_STAGE_* value.

	Returns:
		The name, as bytes.
	"""
)

http_stage_label = lib_function (
	"http_stage_label", [HttpStage], c_char_p,
	"""Returns the value of the stage label of the metrics of a stage.

	Args:
		stage: An HTTP_STAGE_* value.

	Returns:
		The label, as bytes.
	"""
)

# how a client that left ended its connection
HttpAbortReason: TypeAlias = c_int # type: ignore

HTTP_ABORT_REASON_CLOSED = 0
HTTP_ABORT_REASON_RESET = 1

HTTP_ABORT_REASONS = 2

http_abort_reason_string = lib_function (
	"http_abort_reason_string", [HttpAbortReason], c_char_p,
	"""Returns the name of an abort reason.

	Args:
		reason: An HTTP_ABORT_REASON_* value.

	Returns:
		The name, as bytes.
	"""
)

http_abort_reason_label = lib_function (
	"http_abort_reason_label", [HttpAbortReason], c_char_p,
	"""Returns the value of the reason label of the metrics of an abort reason.

	Args:
		reason: An HTTP_ABORT_REASON_* value.

	Returns:
		The label, as bytes.
	"""
)

# the state of the client of a request, CLOSED is an EOF (a close or a half-close)
HttpClientState: TypeAlias = c_int # type: ignore

HTTP_CLIENT_STATE_CONNECTED = 0
HTTP_CLIENT_STATE_CLOSED = 1
HTTP_CLIENT_STATE_RESET = 2

http_client_state_string = lib_function (
	"http_client_state_string", [HttpClientState], c_char_p,
	"""Returns the name of a client state.

	Args:
		state: An HTTP_CLIENT_STATE_* value.

	Returns:
		The name, as bytes.
	"""
)

http_receive_get_cerver_receive = lib_function (
	"http_receive_get_cerver_receive", [c_void_p], c_void_p,
	"""Returns the CerverReceive of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The CerverReceive.
	"""
)

http_receive_get_sock_fd = lib_function (
	"http_receive_get_sock_fd", [c_void_p], c_int,
	"""Returns the socket of the connection of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The socket.
	"""
)

http_receive_get_cerver = lib_function (
	"http_receive_get_cerver", [c_void_p], c_void_p,
	"""Returns the HttpCerver that handles a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The HttpCerver.
	"""
)

http_receive_get_endpoint = lib_function (
	"http_receive_get_endpoint", [c_void_p], c_void_p,
	"""Returns the endpoint that handles a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The HttpEndpoint, None if no endpoint matched.
	"""
)

http_receive_get_route_custom_data = lib_function (
	"http_receive_get_route_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of the endpoint of a request (its own, its group's or its route's).

	Args:
		http_receive: The HttpReceive.

	Returns:
		The data, None if it has none.
	"""
)

http_receive_get_cerver_custom_data = lib_function (
	"http_receive_get_cerver_custom_data", [c_void_p], c_void_p,
	"""Returns the custom data of the HttpCerver of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The data, None if it has none.
	"""
)

http_receive_is_head = lib_function (
	"http_receive_is_head", [c_void_p], c_bool,
	"""Returns if a request is a HEAD handled by the GET handler, its responses are sent without body.

	Args:
		http_receive: The HttpReceive.

	Returns:
		True for a HEAD.
	"""
)

http_receive_get_allow = lib_function (
	"http_receive_get_allow", [c_void_p], c_char_p,
	"""Returns the value of the Allow header of the path of a request.

	Args:
		http_receive: The HttpReceive.

	Returns:
		The methods, as bytes.
	"""
)

http_receive_get_stage = lib_function (
	"http_receive_get_stage", [c_void_p], HttpStage,
	"""Returns the stage that a request has reached.

	Args:
		http_receive: The HttpReceive.

	Returns:
		An HTTP_STAGE_* value.
	"""
)

http_receive_get_client_state = lib_function (
	"http_receive_get_client_state", [c_void_p], HttpClientState,
	"""Checks, without waiting and without reading its data, if the client of a request is still connected.

	A handler that takes long can call it to stop the work of a client that left.

	Args:
		http_receive: The HttpReceive.

	Returns:
		HTTP_CLIENT_STATE_CONNECTED, HTTP_CLIENT_STATE_CLOSED (an EOF) or HTTP_CLIENT_STATE_RESET.
	"""
)

http_receive_is_client_gone = lib_function (
	"http_receive_is_client_gone", [c_void_p], c_bool,
	"""Returns if the client of a request left.

	A reset client is gone, a closed one is gone unless the cerver takes a half-close
	as still connected (http_cerver_set_half_close_is_gone ()), and so is the client
	of a response that could not be sent.

	Args:
		http_receive: The HttpReceive.

	Returns:
		True if the client is gone.
	"""
)
