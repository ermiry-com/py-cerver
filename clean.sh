#!/bin/bash

# clear python cache
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs sudo rm -rf

# remove test sources
make clean

# remove uploads path
sudo rm -r uploads
