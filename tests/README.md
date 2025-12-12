# pycerver tests

The test suite of the package. It runs only inside its image: cerver is compiled there from its local
sources (`CERVER_DIR`, the `http` line), and the working tree of the package is mounted and goes first in
`PYTHONPATH`, so the suite always tests the working tree.

| Directory | What |
|---|---|
| `unit/` | Every module imports; every binding agrees with its prototype in the headers of cerver (arguments, widths, result, no private function, the coverage of the public API); every constant and every mirrored struct agrees with C (`probe/`); the validators, the readers of a request, the log, files, network, threads, the callbacks, hypothesis |
| `integration/` | A real web cerver created and configured, never started: the groups and their decorators, typed params, middleware, registration errors, the settings, the metrics |
| `e2e/` | `e2e/server.py` (the features of HTTP), `e2e/run.py` (`cerver_run ()`), `e2e/echo.py` with a client of pycerver over TCP and UDP in IPv4 and `::1`, the servers of `legacy/` with their C clients and with their Python equivalents |
| `legacy/` | The servers of the first routes API, `web/` and `cerver/ping.py`, started from this directory |
| `clients/` | The C clients of the legacy servers (libcurl), compiled in the image by the `makefile` of the root |
| `probe/` | A C program compiled in the image that prints the constants and the layouts of the structs of cerver |
| `data/` | The JSON bodies of the C clients |

## Running

```bash
./build.sh                          # ermiry/pycerver:tests
./run.sh                            # every tier
./run.sh unit -k url                # a tier forwards what follows it to pytest

SANITIZER=address,undefined ./build.sh
./run.sh asan                       # every tier with libcerver instrumented, the servers and clients inherit the preload
./run.sh fuzz                       # hypothesis with the nightly profile
./run.sh repeat e2e/test_server.py 20
./run.sh coverage                   # tests/htmlcov
```

`TESTS_IMAGE=<tag>` and `CERVER_DIR` build and run another tag over other sources.

## Rules

- A server of the e2e writes its output to a file, never to a pipe that nobody reads: a full pipe blocks it.
- A cerver started in the main thread only stops when the signal interrupts its `accept ()`, a signal that
  arrives before it is lost: a server runs with `cerver_run (cerver)`, that starts cerver in a thread, waits for
  SIGINT or SIGTERM in the main thread and returns after `cerver_shutdown ()` and `cerver_teardown ()`.
- A callback given to cerver must be kept: the high level API (`HttpGroup`, `http_handler`, the `*_on ()`
  functions, `Worker`, `WorkerManager`) keeps it; the raw bindings take a CFUNCTYPE object that is already kept,
  and they reject a plain function with `TypeError`.
- A binding that is added must agree with `unit/test_bindings.py`, and a constant or a mirrored struct with
  `probe/probe.c`: add it there too.
