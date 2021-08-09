#!/bin/bash

# ensure a clean build
make clean

# remove any active container
sudo docker kill $(sudo docker ps -q)

# compile tests
make TYPE=test -j4 test || { exit 1; }

# compile docker
echo "Building local test docker image..."
sudo docker build -t ermiry/pycerver:local -f Dockerfile.local . || { exit 1; }

# ping
echo "Ping integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 7000:7000 \
	ermiry/pycerver:local python3 ping.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/ping || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# web
echo "Web integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/web.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/web || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# auth
echo "Web Auth integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/auth.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/auth || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# api
echo "API integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/api.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/api || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# upload
echo "Upload integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/upload.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/upload || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# multiple
echo "Multiple integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/multiple.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/multiple || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# jobs
echo "Jobs integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/jobs.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/jobs || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# admin
echo "Admin integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/admin.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/admin || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# wrapper
echo "Wrapper integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/wrapper.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/wrapper || { exit 1; }

sudo docker kill $(sudo docker ps -q)

printf "\n\nDone\n\n"
