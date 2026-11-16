## General
- Released pycerver 1.1.4, bound to cerver 2.0b-76: the binding of thpool_has_queued

## Bindings
- Added the binding of thpool_has_queued, whether a job waits in the queue without the mutex of the thpool

## Tests
- Checking thpool_has_queued with a thpool whose jobs ran & without a thpool
- Pinned cerver 2.0b-76 in the Dockerfiles, the workflows & cerver-install.sh
