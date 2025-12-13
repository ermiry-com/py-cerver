# Incompatibilities

The changes of each version that can break code built with the version before it, the newest first.
Unlike `CHANGELOG.md`, which only has the current version, every entry stays here.

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
