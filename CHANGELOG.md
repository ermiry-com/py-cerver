## General
- Released pycerver 1.1.5, bound to cerver 2.0b-77: the shared args of the client events & errors

## Bindings
- Added shared_args & shared_response to ClientEventData & shared_args to ClientErrorData, the fields of the 2.0b-77
- Updated the doc of files_create_dir: a directory that already exists is a success

## Tests
- Checking the offsets of the new fields of ClientEventData & ClientErrorData in the probe
- Pinned cerver 2.0b-77 in the Dockerfiles, the workflows & cerver-install.sh
