"""Every constant of the package has the value of its enum or define in the headers of cerver.

The probe of the test image prints the value of each constant compiled against the headers,
so a value written by hand that drifts from C (like HTTP_HEADER_UNDEFINED was 53 when C had
63, or HTTP_HEADER_REAL_IP that was missing) fails here.
"""

import importlib
import pkgutil
import pytest
import re

import cerver

from probes import PROBE_VALUES, PROBE_CONSTANT

pytestmark = [pytest.mark.unit]

CONSTANT_NAME = re.compile (r"[A-Z][A-Z0-9_]+")

# the constants that only the package defines
PYTHON_CONSTANTS = {
	"CERVER_RUN_POLL_SECONDS", "CLIENT_SESSION_ID_SIZE", "FILES_DEFAULT_DIRECTORY_MODE",
	"HTTP_CERVER_DEFAULT_BUFFER_SIZE", "HTTP_CERVER_DEFAULT_PORT", "HTTP_CERVER_DEFAULT_THREADS"
}

def package_constants () -> dict:
	"""name -> value of every integer constant that a module of the package exports."""
	constants = {}
	for module in pkgutil.walk_packages (cerver.__path__, prefix="cerver."):
		imported = importlib.import_module (module.name)
		for name in getattr (imported, "__all__", ()):
			value = getattr (imported, name)
			if (CONSTANT_NAME.fullmatch (name) and isinstance (value, int) and not isinstance (value, bool)):
				constants[name] = value

	return constants

CONSTANTS = package_constants ()
C_CONSTANTS = PROBE_VALUES[PROBE_CONSTANT]

class TestConstants:

	def test_constants_were_found (self):
		assert len (CONSTANTS) > 500

	@pytest.mark.parametrize ("name", sorted (set (CONSTANTS) - PYTHON_CONSTANTS))
	def test_constant_is_the_one_of_c (self, name):
		assert name in C_CONSTANTS, f"{name} is not in the probe"
		assert CONSTANTS[name] == C_CONSTANTS[name]

	@pytest.mark.parametrize ("name", sorted (C_CONSTANTS))
	def test_probe_constant_is_in_the_package (self, name):
		assert name in CONSTANTS

	def test_real_ip_header (self):
		assert CONSTANTS["HTTP_HEADER_REAL_IP"] == C_CONSTANTS["HTTP_HEADER_REAL_IP"]
