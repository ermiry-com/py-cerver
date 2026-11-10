"""Unit tests for version.py - the version prints of pycerver and cerver.

Bugs these tests fixed:
- pycerver_version_print_version_id () and _name () read version.id and version.name
  of a dict, so they raised AttributeError
"""

import pytest

from cerver.version import cerver_version_print_full
from cerver.version import cerver_version_print_version_id
from cerver.version import cerver_version_print_version_name
from cerver.version import pycerver_version_print_full
from cerver.version import pycerver_version_print_version_id
from cerver.version import pycerver_version_print_version_name
from cerver.version import version

pytestmark = [pytest.mark.unit]

class TestVersion:

	def test_version_values (self):
		assert version["id"]
		assert version["name"]

	@pytest.mark.parametrize ("version_print", [
		pycerver_version_print_full,
		pycerver_version_print_version_id,
		pycerver_version_print_version_name,
		cerver_version_print_full,
		cerver_version_print_version_id,
		cerver_version_print_version_name
	])
	def test_print (self, version_print):
		version_print ()
