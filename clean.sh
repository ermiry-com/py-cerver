#!/bin/bash

# clear python cache
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs sudo rm -rf

# remove test sources
make clean

# what a run of the test suite leaves in tests/
rm -rf tests/htmlcov tests/.coverage tests/.coverage.* tests/.hypothesis

# remove uploads path
sudo rm -r uploads

# the files that the legacy test servers received
sudo rm -rf tests/legacy/uploads/*

# remove generated build
sudo rm -r build
sudo rm -r dist
sudo rm -r pycerver.egg-info
