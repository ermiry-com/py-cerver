#!/bin/bash

# ensure a clean build
make clean

# remove any active container
sudo docker kill $(sudo docker ps -q)

# compile tests
make TYPE=test -j4 test || { exit 1; }

# compile docker
sudo docker build -t ermiry/pycerver:test -f Dockerfile.test . || { exit 1; }

# web
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:test python3 web.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/web || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# api
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:test python3 api.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/api || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# upload
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:test python3 upload.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/upload || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# jobs
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:test python3 jobs.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/jobs || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# admin
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:test python3 admin.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/admin || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# wrapper
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:test python3 wrapper.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/wrapper || { exit 1; }

sudo docker kill $(sudo docker ps -q)
