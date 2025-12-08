# syntax=docker/dockerfile:1
# the test image of pycerver: cerver compiled from its local sources, with the sanitizer
# of the variant; the package is mounted by run.sh and put first in PYTHONPATH,
# so the suite always tests the working tree
# build with --build-context cerver=<path> (see build.sh)

ARG SANITIZER=''

ARG RUNTIME_DEPS='libssl3t64 libcurl4t64 libbrotli1 zlib1g'

FROM gcc:16.2 AS builder

ARG SANITIZER

RUN apt-get update && apt-get install -y libssl-dev libcurl4-openssl-dev zlib1g-dev && apt-get clean

# cerver
COPY --from=cerver . /opt/cerver
RUN cd /opt/cerver \
	&& make clean \
	&& make TYPE=test SANITIZER=${SANITIZER} ZLIB=1 -j4 \
	&& make TYPE=test SANITIZER=${SANITIZER} ZLIB=1 install \
	&& make clean

WORKDIR /opt/pycerver

COPY tests/probe tests/probe
RUN gcc -Wall -I /usr/local/include tests/probe/probe.c -o tests/probe/probe

COPY makefile makefile
COPY tests/clients tests/clients
RUN make clean && make test

############
FROM python:3.14.10-slim-trixie

ARG RUNTIME_DEPS
RUN apt-get update && apt-get install -y ${RUNTIME_DEPS} && apt-get clean

# the runtime of the sanitizers, loaded with LD_PRELOAD by run.sh asan
COPY --from=builder /usr/local/lib64 /opt/gcc/lib64

COPY --from=builder /usr/local/lib/libcerver.so /usr/local/lib/
COPY --from=builder /usr/local/include/cerver /usr/local/include/cerver

COPY --from=builder /opt/pycerver/tests/probe/probe /opt/pycerver/probe
COPY --from=builder /opt/pycerver/tests/clients/bin /opt/pycerver/clients

RUN echo "/opt/gcc/lib64" > /etc/ld.so.conf.d/gcc.conf && ldconfig

WORKDIR /home/pycerver

COPY tests/requirements.txt tests/requirements.txt
RUN pip install --no-cache-dir -r tests/requirements.txt

ENV PYTHONPATH=/home/pycerver
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /home/pycerver/tests

CMD ["pytest"]
