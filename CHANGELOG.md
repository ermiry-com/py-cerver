## General
- Updated Dockerfiles to use cerver 2.0b-50
- Updated custom String type structure definition
- Added more image files types related methods

## HTTP
- Added method to get content type value by extension
- Added base HTTP response handle video implementation
- Added dedicated method to print full request headers
- Replaced HTTP response render with send file
- Added latest HTTP JSON responses methods bindings

## Examples
- Removed JSON handlers from main web example
- Added base web example to showcase JSON methods
- Added dedicated example public video html source
- Added base example to showcase HTTP video stream
- Added base Dockerfile to be used for running examples
- Added dedicated script to build examples image

## Tests
- Removed JSON methods from main web tests
- Added dedicated curl method to upload JSON in body
- Added base dedicated web JSON integration tests
- Added JSON data files to be used in web tests