"""The configuration of the service, from environment variables with their defaults."""

import os

SERVICE_NAME = os.environ.get ("SERVICE_NAME", "notes")

PORT = int (os.environ.get ("PORT", 8080))
CONNECTION_QUEUE = int (os.environ.get ("CONNECTION_QUEUE", 64))
RECEIVE_BUFFER_SIZE = int (os.environ.get ("RECEIVE_BUFFER_SIZE", 4096))
THREADS = int (os.environ.get ("THREADS", 4))

MAX_BODY_SIZE = int (os.environ.get ("MAX_BODY_SIZE", 1 << 20))

# a service behind a proxy reads the client from X-Forwarded-For
TRUSTED_PROXY = os.environ.get ("TRUSTED_PROXY", "127.0.0.0/8")

# how often the expired notes are removed, in seconds
CLEANUP_INTERVAL = int (os.environ.get ("CLEANUP_INTERVAL", 60))
