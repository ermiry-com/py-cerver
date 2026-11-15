## General
- Released pycerver 1.1.3, bound to cerver 2.0b-75: the fixes of the audit of cerver & the videos of RFC 9110

## Bindings
- Added shared_args to CerverEventData & CerverErrorEventData, the reference of each trigger to the args
- Added the bindings of timer_get_gmt_time_r & timer_get_local_time_r, the old ones are deprecated
- Added the bindings of lobby_get_reference & lobby_search_with_id_reference, that take a reference to the lobby
- Updated the docs of the videos (200, 206 & 416) & of the custom data of the endpoints & the groups

## Tests
- Reading the prototypes of cerver wrapped in DEPRECATED () in the test of the bindings
- Building the probe with -D _GNU_SOURCE, that config.h of cerver 2.0b-75 needs
- Pinned cerver 2.0b-75 in the Dockerfiles, the workflows & cerver-install.sh
