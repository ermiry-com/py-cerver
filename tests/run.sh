#!/bin/bash
# Runs the pycerver test suite inside the test container.
#
# The package is bind-mounted from its working tree and goes first in PYTHONPATH, so edits
# take effect on the next run with no rebuild. Rebuild (./build.sh) when cerver,
# requirements.txt or tests/Dockerfile change.
#
# Every tier needs only the image: e2e starts the servers of tests/e2e/ and of tests/legacy/
# as subprocesses inside the container and talks to them through localhost.

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

IMAGE_NAME="ermiry/pycerver:tests"
ASAN_IMAGE_NAME="ermiry/pycerver:tests-address-undefined"

# TESTS_CONTAINER_NAME overrides the container name, to run two sessions of the suite at once
CONTAINER_NAME="${TESTS_CONTAINER_NAME:-pycerver-tests}"

PACKAGE_ROOT="$(cd "$(dirname "$0")/.." && pwd)"

# the profile of hypothesis: ci (the default runs) or nightly (./run.sh fuzz)
HYPOTHESIS_PROFILE="${HYPOTHESIS_PROFILE:-ci}"

DOCKER_RUN_ARGS=(
	--rm
	--name "${CONTAINER_NAME}"
	-e HYPOTHESIS_PROFILE="${HYPOTHESIS_PROFILE}"
	-v "${PACKAGE_ROOT}:/home/pycerver"
)

RUN_IMAGE="${IMAGE_NAME}"
if [ "$1" == "asan" ]; then
	RUN_IMAGE="${ASAN_IMAGE_NAME}"
fi

# TESTS_IMAGE runs another tag, the one that build.sh built with it
RUN_IMAGE="${TESTS_IMAGE:-${RUN_IMAGE}}"

if ! docker image inspect "${RUN_IMAGE}" > /dev/null 2>&1; then
	echo -e "${RED}✗ Test image not found: ${RUN_IMAGE}${NC}"
	echo -e "${YELLOW}Run ./build.sh first (SANITIZER=address,undefined ./build.sh for asan)${NC}"
	exit 1
fi

echo -e "${GREEN}=== Running pycerver Tests in Docker ===${NC}"

# Arguments passed to pytest inside the container, relative to tests/.
# A tier keyword forwards whatever follows it: ./run.sh unit -k url
PYTEST_ARGS=()
RUN_COMMAND=()

case "$1" in
	"")
		echo -e "${YELLOW}Running every tier...${NC}"
		;;
	"unit")
		PYTEST_ARGS=(unit/ "${@:2}")
		;;
	"integration")
		PYTEST_ARGS=(integration/ "${@:2}")
		;;
	"e2e")
		# serial: the servers listen on fixed ports
		PYTEST_ARGS=(e2e/ "${@:2}")
		;;
	"coverage")
		PYTEST_ARGS=(
			--cov=/home/pycerver/cerver
			--cov-report=term
			--cov-report=html:/home/pycerver/tests/htmlcov
		)
		;;
	"fast")
		PYTEST_ARGS=(-n auto unit/ "${@:2}")
		;;
	"asan")
		# the python interpreter is not instrumented: the runtime of the sanitizers is preloaded,
		# and the leaks are not checked because CPython does not release its memory at exit
		echo -e "${YELLOW}Running every tier with address and undefined sanitizers...${NC}"
		DOCKER_RUN_ARGS+=(
			-e LD_PRELOAD="/opt/gcc/lib64/libasan.so.8:/opt/gcc/lib64/libubsan.so.1"
			-e ASAN_OPTIONS="detect_leaks=0:abort_on_error=1:halt_on_error=1"
			-e UBSAN_OPTIONS="print_stacktrace=1:halt_on_error=1"
		)
		PYTEST_ARGS=("${@:2}")
		;;
	"fuzz")
		echo -e "${YELLOW}Running the fuzz tests with the nightly profile...${NC}"
		DOCKER_RUN_ARGS+=(-e HYPOTHESIS_PROFILE=nightly)
		PYTEST_ARGS=(-m fuzz unit/ "${@:2}")
		;;
	"repeat")
		# ./run.sh repeat <test> [count]: stops at the first failure, to find a flaky test
		TARGET="$2"
		COUNT="${3:-100}"
		if [ -z "${TARGET}" ]; then
			echo -e "${RED}usage: ./run.sh repeat <test> [count]${NC}"
			exit 2
		fi

		RUN_COMMAND=(bash -c "for run in \$(seq 1 ${COUNT}); do pytest -q -p no:cacheprovider '${TARGET}' > /tmp/repeat.log 2>&1 || { tail -n 64 /tmp/repeat.log; echo 'failed in run '\$run' of ${COUNT}'; exit 1; }; done; echo 'passed ${COUNT} runs'")
		;;
	"shell")
		docker run -it "${DOCKER_RUN_ARGS[@]}" "${RUN_IMAGE}" /bin/bash
		exit $?
		;;
	*)
		PYTEST_ARGS=("$@")
		;;
esac

if [ ${#RUN_COMMAND[@]} -gt 0 ]; then
	docker run "${DOCKER_RUN_ARGS[@]}" "${RUN_IMAGE}" "${RUN_COMMAND[@]}"
else
	docker run "${DOCKER_RUN_ARGS[@]}" "${RUN_IMAGE}" pytest "${PYTEST_ARGS[@]}"
fi

exit_code=$?

if [ $exit_code -eq 0 ]; then
	echo -e "${GREEN}✓ All tests passed!${NC}"
else
	echo -e "${RED}✗ Some tests failed${NC}"
fi

exit $exit_code
