# PyCerver

PyCerver is a pure Python wrapper around the cerver framework. It uses the built-in ctypes module to interface with cerver, and provides simple Python classes and wrappers for common cerver functionality.

## Trying out

### Local

You can test out PyCerver without actually installing it. You just need to set up your PYTHONPATH to point to the location of the source distribution package.

```
export PYTHONPATH=/path/to/py-cerver:$PYTHONPATH
```

### Docker

0. Buid local **development** docker image

```
bash development.sh
```

1. Run **development** image with local source

```
sudo docker run \
  -it \
  --name pycerver --rm \
  -p 5000:5000 \
  -v /home/ermiry/Documents/ermiry/Projects/py-cerver:/home/pycerver \
  -e RUNTIME=development \
  -e PORT=5000 \
  -e CERVER_RECEIVE_BUFFER_SIZE=4096 -e CERVER_TH_THREADS=4 \
  -e CERVER_CONNECTION_QUEUE=4 \
  -e PRIV_KEY=/home/pycerver/keys/key.key \
  -e PUB_KEY=/home/pycerver/keys/key.pub \
  ermiry/pycerver:development /bin/bash
```

2. Handle **pycerver** module

```
export PYTHONPATH=$pwd:$PYTHONPATH
```
