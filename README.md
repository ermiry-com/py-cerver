![Cerver Banner](./images/banner.png)

PyCerver is a pure Python wrapper around the [cerver](https://cerver.ermiry.com) framework. It uses the built-in ctypes module to interface with cerver, and provides simple Python classes and wrappers for common cerver functionality. You can check the original project's source code [here](https://github.com/ermiry/cerver)!

## Trying out

### Local

You can test out PyCerver without actually installing it. You just need to set up your PYTHONPATH to point to the location of the source distribution package.

``` bash
export PYTHONPATH=/path/to/py-cerver:$PYTHONPATH
```

### Docker

0. Buid local **development** docker image

``` bash
bash development.sh
```

1. Run **development** image with local source

``` bash
sudo docker run \
  -it \
  --name pycerver --rm \
  -p 8080:8080 \
  -v /home/ermiry/Documents/py-cerver:/home/pycerver \
  ermiry/pycerver:development /bin/bash
```

2. Handle **pycerver** module

``` bash
export PYTHONPATH=$pwd:$PYTHONPATH
```

3. Run any of the included examples

``` bash
python3 examples/http/web.py
```

## Getting Started

1. Import the necessary dependencies

``` python
# provides the ability to handle signals to stop the application
import signal
import sys			# to use sys.exit () to exit the program

# needed to interact with the low level cerver framework
import ctypes

# get access to main and HTTP cerver methods
from cerver import *
from cerver.http import *
```

2. Create a global **Cerver** instance reference

``` python
# define a global reference to the cerver instance
web_service = None
```

3. Define an **end** method to be used as the callback when catching signals. We can use this method to display the cerver's stats and to correctly dispose all the memory that has been allocated by our application

``` python
def end (signum, frame):
  # prints the HTTP cerver stats
  # like how many requests were handled by each route
  http_cerver_all_stats_print (http_cerver_get (web_service))

  # correctly disposes HTTP cerver references
  cerver_teardown (web_service)

  # correctly disposes cerver internal global values.
  # Should be called only once at the very end of the program
  cerver_end ()

  # exit the application with a custom message
  sys.exit ("Done!")
```

4. Create a handler method for the **GET /test** route

``` python
# GET /test
@ctypes.CFUNCTYPE (None, ctypes.c_void_p, ctypes.c_void_p)
def test_handler (http_receive, request):
  # creates a HTTP response with a status code and a JSON body
  response = http_response_json_msg (
    HTTP_STATUS_OK, b"Test route works!"
  )

  # prints the generated HTTP response
  http_response_print (response)

  # send the HTTP response to the client
  http_response_send (response, http_receive)

  # correctly disposes a HTTP response and all of its data
  http_response_delete (response)
```

5. Define a start method where the **Cerver** instance will be created and its configuration will be set before starting it

``` python
def start ():
  # tells Python to use the global reference
  global web_service

  # creates a new cerver of type CERVER_TYPE_WEB
  # that will bind and listen to port 8080 and with a connection queue of size 10
  web_service = cerver_create_web (b"web-service", 8080, 10)

  # main configuration
  # set the cerver's thpool number of threads
  # This will enable the ability to handle requests using multiple threads
  cerver_set_thpool_n_threads (web_service, 4);
  cerver_set_handler_type (web_service, CERVER_HANDLER_TYPE_THREADS);

  # enable cerver's reusable address flags
  # to avoid errors when binding to the selected port
  cerver_set_reusable_address_flags (web_service, True)

  # HTTP configuration
  # gets a reference to the cerver's internal HTTP structure
  http_cerver = http_cerver_get (web_service)

  # GET /test
  # create a new HTTP route to handle GET requests at /test endpoint
  # using the previously defined test_handler ()
  test_route = http_route_create (
    REQUEST_METHOD_GET, b"test", test_handler
  )

  # register the new test route to the HTTP cerver
  http_cerver_route_register (http_cerver, test_route)

  # start
  # start listening for connections and handling requests
  cerver_start (web_service)
```

6. Define the application's entry point where the **cerver** is initialized and the signals are handled

``` python
if __name__ == "__main__":
  # register to the desired signals and sets the end () method to handle them
  signal.signal (signal.SIGINT, end)
  signal.signal (signal.SIGTERM, end)
  signal.signal (signal.SIGPIPE, signal.SIG_IGN)

  # initializes global cerver values
  # Should be called only once at the start of the program
  cerver_init ()

  # prints the base cerver framework version information
  cerver_version_print_full ()

  # prints the pycerver wrapper version information
  pycerver_version_print_full ()

  # calls the previously defined start () method
  start ()
```

You can also take a look at the official [wiki](https://github.com/ermiry-com/py-cerver/wiki) to get better explanations about the included examples and of all the methods that are available in the framework.

---

Ermiry - Never Stop Creating
