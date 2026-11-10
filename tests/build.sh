#!/bin/bash
# Builds the test image of pycerver with cerver from its local sources.
#
# SANITIZER=address,undefined builds the variant that run.sh asan uses.
# TESTS_IMAGE builds another tag, eg. over the sources before a fix to see its tests fail.

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SANITIZER="${SANITIZER:-}"

CERVER_DIR="${CERVER_DIR:-/Users/ermiry/Documents/cerver-http}"

IMAGE_NAME="ermiry/pycerver:tests"
if [ -n "${SANITIZER}" ]; then
	IMAGE_NAME="ermiry/pycerver:tests-$(echo "${SANITIZER}" | tr ',' '-')"
fi

IMAGE_NAME="${TESTS_IMAGE:-${IMAGE_NAME}}"

# Build from the package root, the parent of tests/
cd "$(dirname "$0")/.." || exit 1

echo -e "${YELLOW}Building ${IMAGE_NAME}...${NC}"

# native platform: the sanitizers are not reliable under emulation, like in the gate of cerver
docker build \
	--build-context cerver="${CERVER_DIR}" \
	--build-arg SANITIZER="${SANITIZER}" \
	-f tests/Dockerfile -t "${IMAGE_NAME}" .

if [ $? -eq 0 ]; then
	echo -e "${GREEN}✓ ${IMAGE_NAME} built${NC}"
else
	echo -e "${RED}✗ Failed to build ${IMAGE_NAME}${NC}"
	exit 1
fi
