## General
- Updated Dockerfiles to use cerver 2.0b-55
- Updated test & script to use latest HTTP cerver

## HTTP
- Added dedicated multi-part is not empty method binding
- Added custom request get bool query value wrapper
- Added validation methods arguments & returns types
- Removed errors dict argument from mparts validate with default
- Added base validate methods for request query values

## Examples
- Removed errors from defaults in HTTP validation example

## Tests
- Added dedicated HTTP multi-part test to check for errors
- Added base custom HTTP request query integration tests
- Added dedicated tests for query values validation methods