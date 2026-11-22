import faulthandler
import multiprocessing
import os

from hypothesis import settings

# `make check` must give the same answer on every run: random examples have
# sent runner tickets to `error` on failures unrelated to their change. So the
# examples are fixed (derived from each test's source), and there is no example
# database, which would replay one machine's old failures. Per-example timing
# is noise under `unittest-parallel`, so there is no deadline.
settings.register_profile("tests", deadline=None, derandomize=True)
settings.load_profile("tests")

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
