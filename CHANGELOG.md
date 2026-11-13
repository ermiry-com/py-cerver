## General
- Released pycerver 1.1, bound to cerver 2.0b-72: the breaking changes from 1.0 are in incompatibilities.md
- Added the games subpackage with the game cerver, its types, the lobbies & their requests, the players & the scoreboards
- Removing the test containers by their name in the scripts & the workflows, and cleaning the files of the legacy servers

## Bindings
- Added the HTTP client states, the stages of a request, the abort reasons & the half close setting
- Added the HTTP timeouts in milliseconds, the send timeout & the limit of the size of the custom headers
- Binding the portable packet header of 32 bytes, its encoding & the route id with its generation
- Added the serializer with its schemas, compatible with CBOR, & the objects that cerver sends with it
- Added the system bindings of memory, load, cpu, host name & processes, and the histograms of the request stats
- Added the new events & errors of the game, with the action arguments that the events & errors own
- Added the new setters of the cerver, the auth of the connections, the copies of files & the socket sends with deadlines
- Added the authentication of the static paths with their decode data & their authentication handler
- Binding the JWT settings (max size, expiration, leeway, issuer & audience) & the 64 bit values of the tokens
- Added the suffix range type of a Range header with the last bytes of a file

## Tests
- Probing the new constants & the mirrored structures against cerver 2.0b-72
- Added a C game cerver, the unit tests of the scoreboards & the lobbies, and the e2e tests of the protocol as CBOR
- Added e2e tests of the handlers whose client left, of the authentication of static paths & of the send timeout
- Encoding each value of the forms of the C web API client, without their separators
- Pinned cerver 2.0b-72 in the Dockerfiles, the workflows & cerver-install.sh
