#!/bin/bash

# ensure a clean build
make clean

# remove the test container of a previous run, never the other containers of the machine
sudo docker kill test 2> /dev/null

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

./tests/clients/bin/client/ping || { exit 1; }

sudo docker kill test

# web
echo "Web integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/web.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/web || { exit 1; }

sudo docker kill test

# query
echo "Query integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/query.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/query || { exit 1; }

sudo docker kill test

# JSON
echo "JSON integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/responses.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/json || { exit 1; }

sudo docker kill test

# auth
echo "Web Auth integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/auth.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/auth || { exit 1; }

sudo docker kill test

# api
echo "API integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/api.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/api || { exit 1; }

sudo docker kill test

# multi
echo "Multi integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/multi.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/multi || { exit 1; }

sudo docker kill test

# upload
echo "Upload integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/upload.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/upload || { exit 1; }

sudo docker kill test

# multiple
echo "Multiple integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/multiple.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/multiple || { exit 1; }

sudo docker kill test

# jobs
echo "Jobs integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/jobs.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/jobs || { exit 1; }

sudo docker kill test

# worker
echo "Worker integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/worker.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/worker || { exit 1; }

sudo docker kill test

# admin
echo "Admin integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/admin.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/admin || { exit 1; }

sudo docker kill test

# validation
echo "Validation integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/validation.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/validation || { exit 1; }

sudo docker kill test

# wrapper
echo "Wrapper integration test..."
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/pycerver:local python3 web/wrapper.py

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./tests/clients/bin/client/web/wrapper || { exit 1; }

sudo docker kill test

printf "\n\nDone\n\n"
