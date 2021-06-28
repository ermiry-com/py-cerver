## General
- Updated Dockerfiles to use cerver 2.0b-37
- Added custom create directories methods
- Added more files methods like files_get_file_extension_reference () & file_exists ()
- Added custom printf () utility implementation
- Added base instructions to debug PyCerver
- Added Dockerfile to build custom python image

## HTTP
- Added new request dirname methods bindings
- Added request's get n files and values methods
- Refactored HTTP uploads definitions & methods
- Added the ability to set file & dir creation modes
- Added more HttpReceive methods bindings
- Added dedicated multi-part structure getters
- Added methods to traverse request's multi-parts
- Refactored HTTP headers enum type definition

## Examples
- Added multi-parts iter handlers in upload example
- Added discard handler in HTTP upload example
- Added base dedicated HTTP multiple example
- Updated jobs example with new multi-parts

## Tests
- Added iter routes in upload integration tests
- Added curl_upload_two_files () in test methods
- Added dedicated multiple integration test
- Refactored jobs client test requests methods