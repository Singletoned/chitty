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
    autocommit = false

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
        environ = {k: v for k, v in os.environ.items() if k != "CHITTY_ROOT"}
        environ["XDG_CONFIG_HOME"] = str(self.config_home)
        environ["XDG_DATA_HOME"] = str(self.tmp / "data")
        patcher = mock.patch.dict(os.environ, environ, clear=True)
        patcher.start()
        self.addCleanup(patcher.stop)
