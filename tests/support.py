import os
import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from chitty.config import CHITTY_VERSION

CONFIG = textwrap.dedent(
    f"""
    format = 1
    default_context = "tasks"
    chitty_version = "{CHITTY_VERSION}"
    workflow = "runner"
    autocommit = false
    check = "true"
    agent_command = "pi --chitty-{{mode}} {{id}}"

    [contexts.tasks]
    prefix = "TASK"

    [contexts.human]
    prefix = "HUMAN"
    """
).lstrip()


class RepoTestCase(unittest.TestCase):
    """Each test gets a fresh repo and XDG config/data homes in a temp dir."""

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.tmp = Path(directory.name).resolve()
        self.root = self.tmp / "repo"
        self.root.mkdir()
        (self.root / "chitty.toml").write_text(CONFIG)
        self.config_home = self.tmp / "config"
        excluded = {
            "CHITTY_ROOT",
            "CHITTY_ACTOR",
            "CLAUDE_CODE_SESSION_ID",
            "PI_CODING_AGENT",
            "CHITTY_PI_SESSION_ID",
            "PI_SESSION_ID",
            "CODEX_THREAD_ID",
            "CODEX_SESSION_ID",
            "ANTIGRAVITY_CONVERSATION_ID",
        }
        environ = {k: v for k, v in os.environ.items() if k not in excluded}
        environ["HOME"] = str(self.tmp / "home")
        environ["XDG_CONFIG_HOME"] = str(self.config_home)
        environ["XDG_DATA_HOME"] = str(self.tmp / "data")
        environ["GIT_CONFIG_COUNT"] = "1"
        environ["GIT_CONFIG_KEY_0"] = "init.defaultBranch"
        environ["GIT_CONFIG_VALUE_0"] = "main"
        patcher = mock.patch.dict(os.environ, environ, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
