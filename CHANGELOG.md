## General
- Refactored main cerver methods organization
- Updated Dockerfiles to use cerver 2.0b-36
- Updated test workflow to use latest HTTP cerver

## HTTP
- Added http_status_string () method binding
- Refactored http_route_create () definition
- Refactored HTTP response methods organization
- Added http_cerver_auth_generate_bearer_jwt_json_with_value ()
- Added base HTTP headers methods bindings

## Examples
- Updated examples to use HTTP status definitions
- Added base HTTP quick start example

## Tests
- Refactored web integration test handlers

## Fixes
- Fixed http_request_get_content_type () typo

## Documentation
- Added documentation submodule
- Updated documentation to Version 1.0
- Added dedicated workflow to publish docs