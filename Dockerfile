ARG CERVER_VERSION=2.0b-30

ARG BUILD_DEPS='libssl-dev'
ARG RUNTIME_DEPS='libssl1.1'

FROM gcc as builder

ARG BUILD_DEPS
RUN apt-get update && apt-get install -y ${BUILD_DEPS}

# cerver
ARG CERVER_VERSION
RUN mkdir /opt/cerver && cd /opt/cerver \
    && wget -q --no-check-certificate https://github.com/ermiry/cerver/archive/${CERVER_VERSION}.zip \
    && unzip ${CERVER_VERSION}.zip \
    && cd cerver-${CERVER_VERSION} \
    && make TYPE=production -j4

############
FROM python:3.8.5-alpine

ARG RUNTIME_DEPS
RUN apt-get update && apt-get install -y ${RUNTIME_DEPS} && apt-get clean

# cerver
ARG CERVER_VERSION
COPY --from=builder /opt/cerver/cerver-${CERVER_VERSION}/bin/libcerver.so /usr/local/lib/
COPY --from=builder /opt/cerver/cerver-${CERVER_VERSION}/include/cerver /usr/local/include/cerver

# pycerver
RUN pip install --no-cache-dir pycerver==0.3

RUN ldconfig

CMD ["/bin/bash"]