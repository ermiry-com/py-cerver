## General
- Updated Dockerfiles to use cerver 2.0b-40
- Updated test workflow to use latest HTTP cerver
- Added methods to set cerver alias and welcome
- Changed previous clear script name to clean
- Added script to download and install cerver

## Threads
- Added ability to request jobs from queue by id
- Changed jobs methods return values types

## HTTP
- Added method to generate HTTP uploads paths
- Changed http_cerver_set_uploads_path () to only take a static path
- Added ability to set route custom auth handler
- Added methods to set default uploads generators

## Examples
- Changed uploads example to use default generator
- Setting default uploads generators in multiple example
- Added example to showcase different auth types

## Tests
- Updated curl_post_form_value () to handle data
- Added base curl_perform_request () to better handle responses status codes
- Updated multiple integration test to match example
- Updated jobs client test with new curl methods
- Added base dedicated HTTP auth integration test