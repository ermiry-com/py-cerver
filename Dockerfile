ARG CERVER_VERSION=2.0b-34

ARG RUNTIME_DEPS='libssl1.1'

FROM gcc as builder

ARG RUNTIME_DEPS
RUN apt-get update && apt-get install -y ${RUNTIME_DEPS}

# cerver
ARG CERVER_VERSION
RUN mkdir /opt/cerver && cd /opt/cerver \
    && wget -q --no-check-certificate https://github.com/ermiry/cerver/archive/${CERVER_VERSION}.zip \
    && unzip ${CERVER_VERSION}.zip \
    && cd cerver-${CERVER_VERSION} \
    && make TYPE=production -j4

############
FROM python:3.9.2-slim-buster

# libssl
COPY --from=builder /usr/lib/x86_64-linux-gnu/libssl.so.1.1 /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libcrypto.so.1.1 /usr/lib/x86_64-linux-gnu/

# cerver
ARG CERVER_VERSION
COPY --from=builder /opt/cerver/cerver-${CERVER_VERSION}/bin/libcerver.so /usr/local/lib/
COPY --from=builder /opt/cerver/cerver-${CERVER_VERSION}/include/cerver /usr/local/include/cerver

# pycerver
WORKDIR /home/pycerver
RUN pip install --no-cache-dir pycerver==0.6

CMD ["/bin/bash"]
