## General
- Updated Dockerfiles to use cerver 2.0b-52
- Updated test & script to use latest HTTP cerver

## Threads
- Added method to create a detached thread binding

## HTTP
- Added check before decoding query pair value
- Added methods to cast query value to int or float directly
- Added method to get body value without checking size
- Added body int & float values validation methods
- Added ability to completely validate uploaded file

## Tests
- Updating validation integration test with latest methods
- Added dedicated test data file to test float validation