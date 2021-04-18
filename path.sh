#!/bin/bash

# find directory
SITEDIR=$(python -m site --user-site)

# create if it doesn't exist
mkdir -p "$SITEDIR"

# create new .pth file with our path
echo "/home/pycerver" > "$SITEDIR/cerver.pth"