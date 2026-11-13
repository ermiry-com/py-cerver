# Incompatibilities

The changes of each version that can break code built with the version before it, the newest first.
Unlike `CHANGELOG.md`, which only has the current version, every entry stays here.

## 1.2b-1 (from 1.1)

1.2b-1 binds the 2.1 line of cerver (`nightly`), the 2.1b-13: the parser is llhttp. It needs a `libcerver.so` of the
2.1b-13 or newer of that line, and it does not load against a cerver of the 2.0 line (the bindings of WebSocket, of
the methods and of the headers of the responses are not in it).

- Without `http_method_str ()` (cerver removed it): `http_request_method_str ()` names every method
- `REQUEST_METHOD_UNDEFINED` is 255 (it was 34) and `REQUEST_METHOD_SIZE` is 47 (it was 29); new
  `REQUEST_METHOD_*` for the 34 methods of HTTP and `QUERY`, all of them can be registered
- `HTTP_ROUTE_METHODS_STRING_SIZE` is 512 (it was 128)
- `http_cerver_set_max_url_size ()` and `http_cerver_set_max_header_size ()` with 0 set the default value
- Only `HTTP/1.0` and `HTTP/1.1` are served: another protocol is a 400 and another version of HTTP a 505, unless
  `HTTP_PARSER_LENIENT_VERSION` is set
- The headers of a response are a list (`http_response_header_set ()`, `_add ()`, `_remove ()`, `_count ()`,
  `_get ()` and the same with `_by_name`): a header can be repeated, like `Set-Cookie`, and it can have any name.
  They arrive in the order they were added, `Connection: close` is added by cerver when the response is sent, and a
  value with a CR, a LF or a NUL is rejected (`http_response_add_header ()` returns 1)
- The WebSocket connections, the clients, the registry and the handshake are opaque: they are only used through
  their functions. The timeouts of WebSocket are set with the `_milliseconds` setters (the old names were removed)
- New: the lenient flags of the parser (`HTTP_PARSER_LENIENT_*`, `http_cerver_set_parser_lenient ()`,
  `http_parser_lenient_string ()`, `http_parser_lenient_description ()`) and
  `http_cerver_add_responses_header_by_name ()`
- New: WebSocket in `cerver.http.websockets`, the endpoints and the groups with `http_group_web_socket_add ()` and
  `web_socket_handlers ()`, the connections, rooms and broadcast, their stats (`http_cerver_web_socket_get_stats ()`,
  `http_web_socket_get_stats ()`), the headers of the upgrade (`http_web_socket_upgrade_add_header ()`), the query
  of a connection (`http_web_socket_get_query ()`) and the client (`http_web_socket_client_*`)
- New: the examples of `websockets/`, `requests/methods.py` and `requests/abandoned.py`

## 1.1 (from 1.0)

1.1 binds cerver 2.0b-72: it needs a `libcerver.so` of that version or newer, and it does not load against an older
one (the bindings of the client state, the stages, the timeouts in milliseconds, the serializer, the histograms, the
system, the game, the settings of the JWTs and the size of the custom headers are not in it). cerver 2.0b-68
recycles the HTTP responses and the buffers of the bodies and 2.0b-69 is the style of the JWT and the JSON: their API
is the one of 2.0b-67, so the bindings did not change with them. cerver 2.0b-70 is the port of the core of cerver
1.8.1, that adds fields to the data of the events and the errors (below). cerver 2.0b-71 and 2.0b-72 are the fixes
of the audit of the HTTP receive (below, in their own section).

- `CerverEventData` and `ClientEventData` have `owns_action_args`, and `CerverErrorEventData` and `ClientErrorData`
  have `delete_action_args` and `owns_action_args` before `error_message`: the `error_message` of an error read with
  a 1.0 structure against cerver 2.0b-70 comes from the wrong bytes
- `cerver_set_sessions (cerver, None)` uses the default session id generator of cerver, 64 hex characters of random
  bytes of the kernel; it returned an error

### Protocol

cerver 2.0b-66 has the protocol of cerver 1.8: a 1.1 client or cerver only talks with a cerver or a client of 2.0b-66
or newer, or of 1.8.

- `PacketHeader` is the header in memory, not the bytes in the wire: the wire has `PACKET_HEADER_SIZE` (32) bytes
  in little endian, written by `packet_header_encode ()` and read by `packet_header_decode ()`
  (`packet_header_to_bytes ()` and `packet_header_from_bytes ()` in Python). Code that sent or read a
  `PacketHeader` with `bytes ()` or `from_buffer_copy ()` breaks
- `PacketHeader.sock_fd` is `route_id` (`c_uint32`), with the generation of the route of a load balancer, its
  `packet_size` is `c_uint64` and it has `flags` (`PACKET_FLAG_SERIALIZED`); `packet_set_header_values ()` takes
  the route id as its last argument
- `Packet` has `lobby`, `encoded_header`, `data_class` and `recycle_next`, so its layout changed
- The objects that cerver sends (the `CerverSummary`, the `ErrorMessage`, the `LobbySummary`) are encoded by their
  schemas, compatible with CBOR: `serializer_schema ()`, `serializer_encode_bytes ()`, `serializer_decode_bytes ()`,
  `packet_create_serialized ()` and `packet_get_object ()`
- `FileHeader.len` is `c_uint64`, and `file_header_get ()` takes the packet and the header

### Names

- `CERVER_DEFAULT_UPDATE_INTERVAL_SECS` is `CERVER_DEFAULT_UPDATE_INTERVAL_SECONDS`
- `CERVER_EVENT_UNKNOWN`, `CERVER_ERROR_UNKNOWN`, `CLIENT_EVENT_UNKNOWN` and `CLIENT_ERROR_UNKNOWN` have new values,
  after the new events and errors of the game
- `ClientEventData` has `owns_response_data` and `CerverEventData` has `lobby`, so their layouts changed

### HTTP

- A static path with authentication (`http_static_path_set_auth ()`) authenticates its requests before their files
  are looked for, and a file that does not exist is answered like a protected one (401 without authentication).
  Before, the authentication of a static path was never applied
- All the sends of a response share one deadline, the send timeout of the cerver or the one of
  `http_cerver_set_send_timeout_milliseconds ()`, so a client that stops reading ends the response at the deadline
  and not after a timeout for each send

### New

- `cerver.games`: the game cerver, the game types, the lobbies with their request objects (`LobbyCreate`,
  `LobbyJoin`, `LobbyRequest`, `LobbySummary`), `lobby_request_send ()`, `lobby_event_on ()`, the players and
  the scoreboards (`game_score_board ()`)
- `cerver.core.serializers` and `cerver.core.systems` (memory, load, cpu, host name and process),
  `cerver.utils.histograms`, `RequestStats` and `HandlerStats` with `cerver_get_request_stats ()` and
  `handler_get_stats ()`
- `cerver_set_auth_schema ()`, `cerver_set_poll_fds ()`, `cerver_set_on_hold_poll_fds ()`,
  `cerver_set_request_handler ()`, `connection_set_auth_object ()`, `connection_set_auth_token ()`,
  `files_copy ()`, `files_remove_recursive ()`, the sends of a socket with a deadline (`socket_send_*_until ()`)
- `http_cerver_set_send_timeout_milliseconds ()`, `http_static_path_set_decode_data ()` and
  `http_static_path_set_authentication_handler ()`

### From 2.0b-70 (the audit of the HTTP receive)

- A response header that does not fit in its slot is rejected: `http_response_add_header ()`,
  `http_response_add_custom_header ()` and `http_cerver_add_responses_header ()` return 1 and the response keeps the
  header that it had; before, the header was sent cut
- The query and the values of a form are split by `&` and `=` before they are decoded: `?key=a%26b` is one value,
  `a&b`. A client that escaped the whole body of a form, with its `=` and `&`, has to escape each value
- The default request timeout is `HTTP_CERVER_DEFAULT_REQUEST_TIMEOUT` (300 secs, it was 0): a request whose body
  takes longer is answered with 408, and `http_cerver_set_request_timeout (http_cerver, 0)` keeps the old behavior
- A custom header fits up to `http_cerver_set_max_custom_header_size ()` (new), by default
  `HTTP_CERVER_DEFAULT_MAX_CUSTOM_HEADER_SIZE` (8192 bytes); it was 512 bytes
- The trailers of a chunked body count for the size and the number of the headers (431), the spaces after the value
  of a header are not part of it, and a target in absolute form is routed by its path
- `Range: bytes=-N` is the range of the last N bytes of the file, with the new `HTTP_RANGE_TYPE_SUFFIX`

### From 2.0b-66 (the security of JWT and JSON)

- `http_cerver_auth_set_jwt_algorithm ()` returns 0 or 1 and does not accept `JWT_ALG_NONE`;
  `http_cerver_auth_configuration ()` does not set an algorithm for `JWT_ALG_NONE`
- The keys are checked when the cerver starts: a secret shorter than its hash, an RSA key of less than 2048 bits or
  an ES key of another curve stops it
- `http_cerver_auth_jwt_add_value_int ()` takes 64 bits; a text value longer than 127 bytes is cut at a complete
  UTF-8 character; `HTTP_JWT_TOKEN_SIZE` is `1 << 14` and `HTTP_JWT_BEARER_SIZE` (new) `1 << 13`
- Tokens are verified strictly with the algorithm of the cerver (canonical base64url, objects without repeated
  keys, the names of RFC 7518, `exp` and `nbf` integers, a maximum size)
- The json responses escape their values and write the reals without `%f` (`1.5`, before `1.500000`)
- New: `http_cerver_auth_set_jwt_max_size ()`, `_require_expiration ()`, `_leeway_seconds ()`, `_issuer ()`,
  `_audience ()`, `HTTP_CERVER_DEFAULT_JWT_MAX_SIZE`

### From 2.0b-65

- `cerver_http_requests_incompleted_total` only counts the requests that cerver could not parse: a client that left is
  in `cerver_http_aborted_requests_total{stage,reason}`, one that a timeout ended in
  `cerver_http_vanished_requests_total{stage}`, and a response that could not be sent in
  `cerver_http_failed_responses_total` (`HTTP_RECEIVE_STATUS_RESPONSE_FAILED`)
- The files of a request that was not completed are always removed, even if `uploads_delete_when_done` is false
- New: `http_receive_get_client_state ()`, `http_receive_is_client_gone ()`, `http_receive_get_stage ()`,
  `http_cerver_set_half_close_is_gone ()`, `http_cerver_set_{headers,request,idle}_timeout_milliseconds ()`, the
  `HTTP_STAGE_*`, `HTTP_ABORT_REASON_*` and `HTTP_CLIENT_STATE_*` constants and their strings

## 1.0 (from 0.9.8)

1.0 binds cerver 2.0b-64: it needs a `libcerver.so` of that version or newer, and it does not load against an older
one (the bindings of the UDP, IPv6, thpool, job queue, worker manager and proxy APIs are not in it).

### Modules

The package is split in subpackages, each one with an explicit `__all__`. The names are the same ones that every
subpackage re-exports, so `from cerver import ...`, `from cerver.http import ...` and `from cerver.threads import ...`
keep working; only the imports of the old modules break:

| 0.9.8 | 1.0 |
|---|---|
| `cerver.cerver` | `cerver.core.cerver`, `cerver.core.policies`, `cerver.core.update`, `cerver.core.run` |
| `cerver.files`, `cerver.handler`, `cerver.timer`, `cerver.packets` | `cerver.core.files`, `cerver.core.handler`, `cerver.core.timer`, `cerver.core.packets` |
| `cerver.network` (a module) | `cerver.network.network` (`cerver.network` is a subpackage) |
| `cerver.http.http` | `cerver.http.cerver.server`, `.routes`, `.uploads`, `.limits`, `.defaults`, `.auth`, `.origins`, `.admin`, `.receive`; `cerver.http.compression`, `cerver.http.proxy` |
| `cerver.http.request` | `cerver.http.requests.methods`, `.getters`, `.params`, `.query`, `.body`, `.multipart`, `.values` |
| `cerver.http.query` | `cerver.http.requests.query` |
| `cerver.http.response` | `cerver.http.responses.core`, `.json`, `.files`, `.stream` |
| `cerver.http.redirect` | `cerver.http.responses.redirects` |
| `cerver.http.route` | `cerver.http.routes` |
| `cerver.http.alg` | `cerver.http.algorithms` |
| `cerver.http.validation` (a module) | `cerver.http.validation.query`, `.body`, `.multipart`, `.image`, `.common` |
| `cerver.threads.job` | `cerver.threads.jobs` |

A `patch ()` of a test must target the module that uses the name now, like `cerver.http.requests.values` or
`cerver.http.validation.query`.

### Names

- The type aliases are in CamelCase: `http_status` is `HttpStatus`, `http_header` is `HttpHeaderType` and
  `jwt_alg_t` is `JwtAlgorithm`
- `http_response_add_custom_header_format` (the variadic C function) is `http_response_add_custom_header_variadic`;
  `http_response_add_custom_header_value ()` is the same
- `PROTOCOL_NONE` was removed, it is not a value of the `Protocol` of cerver
- `handler_delete` was removed, it is a private function of cerver; `worker_remove_reference` was removed, the `Worker`
  class keeps its own callbacks
- The modules no longer leak what they import: `signal`, `json`, `ctypes` and the names of other modules have to be
  imported where they are used

### Behavior

- The library is loaded from `CERVER_LIBRARY`, then from `/usr/local/lib/libcerver.so` and then with
  `ctypes.util.find_library`; when none loads, the import raises `CerverLibraryError` instead of an `OSError`
- Every callback argument of a raw binding is a `c_void_p`: a `CFUNCTYPE` object (like a function decorated with
  `@HttpHandler` or `@ctypes.CFUNCTYPE (...)`) is accepted, a plain Python function raises `ctypes.ArgumentError`
  instead of passing a thunk that is released while cerver still calls it; the helpers (`HttpGroup`, `http_handler`,
  `cerver_event_on`, `client_event_on`, `Worker`, ...) keep the callbacks that they wrap
- `cerver_log_*` pass the message as the argument of a `"%s"` format: a `%` in a message without arguments is written
  as it is (`%%` is written as two), it is no longer read as a printf conversion (a `%n` aborted the process); a
  message with arguments is formatted in Python (`message % arguments`), so `%s` with bytes or str arguments works
  like before. The C functions are `cerver_log_*_variadic`
- `Job` has its `id`, so the offsets of its other fields changed; `HttpOrigin.value` is a `char [256]` and
  `ThreadWork` returns a `void *`, like in C
- `worker_set_delete_data ()` takes a `WorkerDataDelete`, it took a `WorkerMethod`
- `Worker` no longer calls cerver in `__del__`, its worker must be released with `Worker.delete ()`
- `http_jwt_create ()` and `http_jwt_create_and_send ()` raise `TypeError`, before the JWT is created, for a value
  that is not a `str`, an `int` or a `bool` (a `float` used to be dropped in silence); `values` defaults to `None`
- `http_send_response ()` sends a `list` as JSON, like a `dict`
- The validators write `"Field <name> is invalid."` for a value that is present but is not valid (a JSON number of
  `validate_body_int_value_exists ()` / `validate_body_float_value_exists ()` that is of another type); they wrote
  `"Field <name> is required."`
- `validate_query_int_actual_value ()` writes `"Failed to validate field <name>."`, it wrote
  `"Failed to validate field <name> value."`
- `validate_mparts_optional_file_is_image ()` never writes an error, it wrote `"File <name> is not png or jpeg."` for
  a file that is not an image; its `errors` is optional
- `HttpGroup` has `head` and `options`, and `http_group ()` adds the handler of its root

### Packaging

- `setup.py` and `setup.cfg` were replaced by a PEP 621 `pyproject.toml`; Python 3.10 or newer
- The package has a `py.typed`

### Services

The services that are migrated to 1.0 have to change:
- `from cerver.http import http_status` (the error tables of 37 services) to `HttpStatus`
- the imports of the old modules of the table above
- any plain Python function that is passed to a raw binding as a callback, which has to be a `CFUNCTYPE` object
