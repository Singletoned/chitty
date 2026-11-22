import faulthandler
import os

from hypothesis import settings

CHECK_EXAMPLE_DIVISOR = 5
THOROUGH_EXAMPLE_FACTOR = 5


def example_count(profile: str, base: int) -> int:
    if profile == "check":
        return max(1, base // CHECK_EXAMPLE_DIVISOR)
    if profile == "thorough":
        return base * THOROUGH_EXAMPLE_FACTOR
    raise ValueError(f"no example count for Hypothesis profile {profile!r}")


def examples(base: int) -> int:
    return example_count(settings.get_current_profile_name(), base)


# Fixed examples make checks repeatable; thorough runs explore and replay failures.
settings.register_profile(
    "check", deadline=None, derandomize=True, max_examples=example_count("check", 100)
)
settings.register_profile(
    "thorough", deadline=None, derandomize=False, max_examples=example_count("thorough", 100)
)
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
# The `pytest` controller only waits on its workers, so its dump names no
# test. It fires later, letting a hung worker's dump, which names the test, come
# first.
PARENT_GRACE_SECONDS = 30
_is_worker = os.environ.get("PYTEST_XDIST_WORKER") is not None
faulthandler.dump_traceback_later(
    SUITE_TIMEOUT_SECONDS + (0 if _is_worker else PARENT_GRACE_SECONDS), exit=True
)
