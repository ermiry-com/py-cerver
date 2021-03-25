#!/bin/bash

# web
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/cerver:test ./bin/web/web

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/web || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# api
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/cerver:test ./bin/web/api

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/api || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# upload
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/cerver:test ./bin/web/upload

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/upload || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# jobs
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/cerver:test ./bin/web/jobs

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/jobs || { exit 1; }

sudo docker kill $(sudo docker ps -q)

# admin
sudo docker run \
	-d \
	--name test --rm \
	-p 8080:8080 \
	ermiry/cerver:test ./bin/web/admin

sleep 2

sudo docker inspect test --format='{{.State.ExitCode}}' || { exit 1; }

./test/bin/client/web/admin || { exit 1; }

sudo docker kill $(sudo docker ps -q)