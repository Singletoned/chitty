import os

from hypothesis import settings

settings.register_profile("tests", deadline=None)
settings.load_profile("tests")

AGENT_PREFIXES = ("PI_", "CLAUDE_", "CODEX_", "CHITTY_")

for _name in list(os.environ):
    if _name.startswith(AGENT_PREFIXES):
        del os.environ[_name]
