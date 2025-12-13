![Cerver Banner](https://ermiry.com/api/images/cerver/banner.png)

PyCerver is a pure Python wrapper around the [cerver](https://cerver.ermiry.com) framework. It uses the built-in ctypes module to interface with cerver, and provides Python helpers for the common cerver functionality: HTTP services with groups and decorators, request values as Python text, JSON responses, validators, JWTs, thread pools, job queues, workers, and TCP / UDP cervers and clients. You can check the original project's source code [here](https://github.com/ermiry/cerver)!

## Compatibility

| pycerver | cerver | Python |
|---|---|---|
| 1.0 | 2.0b-64 or newer | 3.10 to 3.14 |

PyCerver loads `libcerver.so` at import time: from the path in the `CERVER_LIBRARY` environment variable, then from `/usr/local/lib/libcerver.so`, and then from the paths of the system linker. The breaking changes of each version are in [incompatibilities.md](incompatibilities.md).

## Installation

1. Compile and install cerver (see [cerver-install.sh](cerver-install.sh))

``` bash
bash cerver-install.sh
```

2. Install pycerver

``` bash
pip install pycerver==1.0
```

You can also use the source distribution without installing it, with your `PYTHONPATH` pointing to it:

``` bash
export PYTHONPATH=/path/to/py-cerver:$PYTHONPATH
```

## Getting Started

A web service with a group of two endpoints, that runs until it gets SIGINT or SIGTERM:

``` python
import sys

from cerver import cerver_init, cerver_end, cerver_run
from cerver.http import HTTP_STATUS_OK, REQUEST_METHOD_GET
from cerver.http import http_cerver_configuration, http_cerver_get, http_group
from cerver.http import http_request_get_named_param_string, http_response_json_send

def hello (http_receive, request):
	"""GET /api/hello"""
	http_response_json_send (http_receive, HTTP_STATUS_OK, {"msg": "Hello from pycerver!"})

def main () -> int:
	cerver_init ()

	service = http_cerver_configuration ("quick", port=8080)
	http_cerver = http_cerver_get (service)

	api = http_group (http_cerver, "api/hello", REQUEST_METHOD_GET, hello)

	@api.get ("/:name")
	def hello_name (http_receive, request):
		"""GET /api/hello/:name"""
		name = http_request_get_named_param_string (request, "name")
		http_response_json_send (http_receive, HTTP_STATUS_OK, {"msg": f"Hello {name}!"})

	# starts the cerver in its own thread, and stops it and tears it down with SIGINT or SIGTERM
	result = cerver_run (service)

	cerver_end ()

	return result

if __name__ == "__main__":
	sys.exit (main ())
```

``` bash
curl http://localhost:8080/api/hello/world
```

## Packages

| Package | What it has |
|---|---|
| `cerver` | The cerver: creation, configuration, `cerver_run`, handlers, events, errors, files, timer, packets and connections |
| `cerver.http` | The HTTP cerver: routes, groups and decorators, middleware, requests, responses, validation, JWTs, origins, proxies, compression and metrics |
| `cerver.threads` | Threads, the thread pool and its stats, job queues with priorities, workers and the worker manager |
| `cerver.network` | Address resolution and parsing, sockets and UDP |
| `cerver.client` | The cerver client: connections, events, errors and files |
| `cerver.types`, `cerver.utils` | The `String` of cerver and the log |

Every package has an explicit `__all__`, and the raw bindings keep the names of the C functions. A callback that is passed to a raw binding has to be a `CFUNCTYPE` object (like `HttpHandler (function)`); the helpers (`http_group`, `HttpGroup`, `http_handler`, `cerver_event_on`, `Worker`, ...) take plain Python functions and keep them alive.

## Examples

The [examples](examples) run with `python3 examples/<folder>/<example>.py`, and read the port from `PORT`:

| Folder | What they show |
|---|---|
| `basics` | The smallest service, its configuration from the environment (address, threads, limits, timeouts and policies), static files and the version |
| `routing` | Groups, subgroups, typed and catch all params, the answers without a route and the routes tree |
| `requests` | Query, JSON body, headers, typed validators, and the real IP behind proxies with request ids |
| `responses` | JSON and prebuilt error responses, custom headers, files, streams, redirects, entity tags and gzip |
| `auth` | JWTs, a custom authentication and the admin routes with their metrics |
| `uploads` | Multipart uploads, a validated image and the files deleted when the request ends |
| `middleware` | The middleware of the cerver, of a group and of an endpoint, and CORS |
| `service` | The layout of a service: configuration from the environment, controllers, routes and an errors table |
| `workers` | A job queue that handles requests in its own thread, the worker manager and a worker without HTTP |
| `client` | A TCP and UDP client of a cerver, with reconnection |
| `deployment` | A compose with nginx in front of the service |

## Tests

The tests run in Docker, against a cerver compiled from its sources (see [tests/README.md](tests/README.md)):

``` bash
CERVER_DIR=/path/to/cerver ./tests/build.sh
./tests/run.sh
```

You can also take a look at the official [wiki](https://github.com/ermiry-com/py-cerver/wiki) to get better explanations about all the methods that are available in the framework.

---

Ermiry - Never Stop Creating
