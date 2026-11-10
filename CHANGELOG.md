## General
- Released pycerver 1.0, bound to cerver 2.0b-64: the breaking changes from 0.9.8 are in incompatibilities.md
- Split the package in subpackages (core, network, client, threads, http with its cerver, requests, responses & validation), each one with an explicit __all__
- Loading libcerver from CERVER_LIBRARY, /usr/local/lib or the system linker, with a CerverLibraryError when it is missing
- Added the docstrings of every public binding & helper in Google style
- Replaced setup.py & setup.cfg with a PEP 621 pyproject.toml, with py.typed

## Bindings
- Added the bindings of the cerver setters & getters, handlers, events & errors, files, timer & packets
- Added the bindings of the thread pool & its stats, the job queue with priorities & its stats, workers & the worker manager
- Added the bindings of network, sockets & UDP, and of the client & its connections, events, errors & files
- Added the HTTP bindings of proxies, compression, conditional requests, dates, request ids, routes stats, the routes tree & metrics
- Fixed the Job, HttpOrigin & ThreadWork structures & types to match cerver
- Every callback argument of a raw binding takes a CFUNCTYPE object, a plain Python function is rejected

## Helpers
- Writing the log messages as they are, formatting their arguments in Python
- Added the request values helpers that return Python text & the decoded JWT JSON
- Added typed validators of the query & of the body (string, int, float, bool, choice, list & date)
- Added the prebuilt JSON responses & a bearer JWT string helper
- Added cerver_run () to run a cerver from the main thread until SIGINT or SIGTERM
- Fixed the JWT values, the list bodies of http_send_response (), the validation messages & the optional image validator
- Added the head & options decorators of HttpGroup, and the root handler of http_group ()

## Examples
- Rewrote every example with groups, decorators & cerver_run (), in folders by topic, with their smoke test

## Tests
- Moved every test to tests/: the unit, integration & e2e tiers, the C clients & the legacy servers
- Checking every binding, constant & mirrored structure against the headers & a C probe of the cerver of the image
- Running every tier with the address & undefined sanitizers, with gcc 16.2 & Python 3.14
- Pinned cerver 2.0b-64, gcc 16.2 & Python 3.14 in the Dockerfiles & workflows
