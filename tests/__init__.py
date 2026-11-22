import faulthandler
import multiprocessing
import os

from hypothesis import settings

CHECK_EXAMPLE_DIVISOR = 5
THOROUGH_EXAMPLE_FACTOR = 5


def example_count(profile: str, base: int) -> int:
    raise NotImplementedError


# Fixed examples make checks repeatable; thorough runs explore and replay failures.
settings.register_profile("check", deadline=None, derandomize=True)
settings.register_profile("thorough", deadline=None, derandomize=False)
settings.load_profile(os.environ.get("TEST_TIER", "check"))

AGENT_PREFIXES = ("PI_", "CLAUDE_", "CODEX_", "CHITTY_")

for _name in list(os.environ):
    if _name.startswith(AGENT_PREFIXES):
        del os.environ[_name]

# A hung test (for example a subprocess that never exits) must fail loudly
# rather than stall `make check` forever. Every process that imports the test
# package dumps all thread tracebacks and exits non-zero once this long has
# passed. The slowest `make check` seen took about 320 seconds on a heavily
# loaded machine.
SUITE_TIMEOUT_SECONDS = 1200
# The `unittest-parallel` parent only waits on its workers, so its dump names no
# test. It fires later, letting a hung worker's dump, which names the test, come
# first.
PARENT_GRACE_SECONDS = 30
_is_worker = multiprocessing.parent_process() is not None
faulthandler.dump_traceback_later(
    SUITE_TIMEOUT_SECONDS + (0 if _is_worker else PARENT_GRACE_SECONDS), exit=True
)
