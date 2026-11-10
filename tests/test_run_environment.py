import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from chitty.ids import TaskId
from chitty.run import _landing_check, _run_check, _setup
from chitty.store import NextAction


class TestCommandEnvironment(unittest.TestCase):
    def test_setup_strips_shared_environment_variables(self):
        self.assert_clean_env(_setup, "true")

    def test_landing_check_strips_shared_environment_variables(self):
        self.assert_clean_env(_landing_check, "true")

    def test_run_check_strips_shared_environment_variables(self):
        with tempfile.TemporaryDirectory() as temporary:
            recorded = Path(temporary) / "environment"
            script = Path(temporary) / "record.py"
            script.write_text(
                "import json, os, sys\n"
                "json.dump({key: os.environ.get(key) for key in "
                "('VIRTUAL_ENV', 'UV_PROJECT_ENVIRONMENT')}, "
                "open(sys.argv[1], 'w'))\n"
            )
            environment = os.environ.copy()
            environment["VIRTUAL_ENV"] = "/shared/venv"
            environment["UV_PROJECT_ENVIRONMENT"] = "/shared/project"
            with patch.dict(os.environ, environment, clear=True):
                _run_check(
                    Mock(),
                    Path(temporary),
                    NextAction("work", TaskId("TASK", 1)),
                    f"{sys.executable} {script} {recorded}",
                )
            self.assertEqual(
                recorded.read_text(),
                '{"VIRTUAL_ENV": null, "UV_PROJECT_ENVIRONMENT": null}',
            )

    def assert_clean_env(self, command, *args):
        with tempfile.TemporaryDirectory() as temporary:
            recorded = Path(temporary) / "environment"
            script = Path(temporary) / "record.py"
            script.write_text(
                "import json, os, sys\n"
                "json.dump({key: os.environ.get(key) for key in "
                "('VIRTUAL_ENV', 'UV_PROJECT_ENVIRONMENT')}, "
                "open(sys.argv[1], 'w'))\n"
            )
            environment = os.environ.copy()
            environment["VIRTUAL_ENV"] = "/shared/venv"
            environment["UV_PROJECT_ENVIRONMENT"] = "/shared/project"
            with patch.dict(os.environ, environment, clear=True):
                command(f"{sys.executable} {script} {recorded}", Path(temporary))
            self.assertEqual(
                recorded.read_text(), '{"VIRTUAL_ENV": null, "UV_PROJECT_ENVIRONMENT": null}'
            )
