"""The values that the probe of the test image (tests/probe/probe.c) reads from the headers of cerver."""

import subprocess
from pathlib import Path

PROBE = Path ("/opt/pycerver/probe")

PROBE_CONSTANT = "constant"
PROBE_SIZE = "size"
PROBE_OFFSET = "offset"

def probe_read () -> dict:
	"""Runs the probe and returns its values by kind: constants, sizes and offsets."""
	values = {PROBE_CONSTANT: {}, PROBE_SIZE: {}, PROBE_OFFSET: {}}

	output = subprocess.run ([str (PROBE)], capture_output=True, text=True, check=True).stdout
	for line in output.splitlines ():
		kind, name, value = line.split ()
		values[kind][name] = int (value)

	return values

PROBE_VALUES = probe_read ()
