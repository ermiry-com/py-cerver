"""Every module of the package imports over the real libcerver.

ctypes resolves every bound symbol when its module is imported, so a symbol that the
libcerver of the image does not export fails here instead of at the start of a service.
"""

import importlib
import pkgutil
import pytest

import cerver

pytestmark = [pytest.mark.unit]

PACKAGE_ROOT = "/home/pycerver/cerver"

PACKAGE_MODULES = sorted (
	module.name for module in pkgutil.walk_packages (cerver.__path__, prefix="cerver.")
)

class TestImports:

	@pytest.mark.parametrize ("module_name", PACKAGE_MODULES)
	def test_module_imports (self, module_name):
		assert importlib.import_module (module_name) is not None

	def test_the_package_is_the_working_tree (self):
		assert cerver.__file__.startswith (PACKAGE_ROOT)

	def test_every_module_was_found (self):
		assert "cerver.http.tree" in PACKAGE_MODULES
		assert "cerver.http.decorators" in PACKAGE_MODULES
