## General
- Updated Dockerfiles to use cerver 2.0b-45
- Refactored test Dockerfile to be used for debugging
- Added Dockerfile to be used for integration tests
- Added dedicated script to build local test image

## Threads
- Added job queue wait & signal methods bindings
- Added new worker related definitions & methods

## HTTP
- Added ability to register a worker to HTTP admin

## Examples
- Added base dedicated HTTP worker example
- Refactored examples to use binary strings directly

## Tests
- Refactored tests run script to use local image
- Updated test curl methods to take an expected status
- Updated web clients tests with new curl methods
- Refactored HTTP integration tests to match examples
- Added base HTTP worker integration test service
- Added matching web worker client test sources