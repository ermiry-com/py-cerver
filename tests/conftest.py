"""Shared configuration of the pycerver suite.

The package comes from PYTHONPATH (the working tree that
run.sh mounts), never from an installed copy; nothing of cerver or the
package is stubbed. The profile of hypothesis comes from HYPOTHESIS_PROFILE.
"""

import os
import sys
from pathlib import Path

from hypothesis import HealthCheck
from hypothesis import settings

tests_root = Path (__file__).resolve ().parent

sys.path.insert (0, str (tests_root))

HYPOTHESIS_PROFILE_CI = "ci"
HYPOTHESIS_PROFILE_NIGHTLY = "nightly"

HYPOTHESIS_CI_EXAMPLES = 200
HYPOTHESIS_NIGHTLY_EXAMPLES = 5000

settings.register_profile (
	HYPOTHESIS_PROFILE_CI,
	max_examples=HYPOTHESIS_CI_EXAMPLES, deadline=None, database=None,
	suppress_health_check=[HealthCheck.too_slow]
)

settings.register_profile (
	HYPOTHESIS_PROFILE_NIGHTLY,
	max_examples=HYPOTHESIS_NIGHTLY_EXAMPLES, deadline=None, database=None,
	suppress_health_check=[HealthCheck.too_slow]
)

settings.load_profile (os.environ.get ("HYPOTHESIS_PROFILE", HYPOTHESIS_PROFILE_CI))
