"""`chitty guide` under each workflow."""

import os
import unittest

from click.testing import CliRunner

from chitty.cli import cli
from chitty.store import ROLE_NAMES, guide, managed_guide
from tests.support import CONFIG, RepoTestCase


class GuideWorkflowTestCase(RepoTestCase):
    def setUp(self):
        super().setUp()
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)

    def write_workflow(self, workflow: str) -> None:
        config = self.root / "chitty.toml"
        config.write_text(CONFIG.replace('workflow = "runner"', f'workflow = "{workflow}"'))

    def invoke(self, *args: str):
        return CliRunner().invoke(cli, list(args), catch_exceptions=False)


class TestRoleGuidesUnderTickets(GuideWorkflowTestCase):
    def setUp(self):
        super().setUp()
        self.write_workflow("tickets")

    def test_each_role_guide_is_refused(self):
        for role in ROLE_NAMES:
            with self.subTest(role=role):
                result = self.invoke("guide", role)
                self.assertEqual(result.exit_code, 1)
                self.assertEqual(result.stdout, "")
                self.assertIn(
                    f'chitty guide {role} needs workflow = "runner" in the Chitty config',
                    result.stderr,
                )

    def test_general_guide_and_help(self):
        self.assertEqual(self.invoke("guide").stdout, managed_guide("tickets"))
        help_text = self.invoke("guide", "--help").stdout
        for role in ROLE_NAMES:
            self.assertNotIn(role, help_text)
        self.assertIn("chitty guide", help_text)


class TestRoleGuidesRunnerCompatibility(GuideWorkflowTestCase):
    def test_runner_guides(self):
        for role in ROLE_NAMES:
            with self.subTest(role=role):
                self.assertEqual(
                    self.invoke("guide", role).stdout, guide(role, directory=self.root)
                )
                if role not in {"plan", "setup"}:
                    self.assertEqual(
                        self.invoke("guide", role, "TASK-1").stdout,
                        guide(role, "TASK-1", directory=self.root),
                    )

    def test_outside_repository_and_broken_config(self):
        previous = os.getcwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, previous)
        self.assertEqual(self.invoke("guide", "work").stdout, guide("work", directory=self.tmp))
        self.assertIn("chitty guide work TASK-12", self.invoke("guide", "--help").stdout)
        os.chdir(self.root)
        self.write_workflow("bogus")
        broken = self.invoke("guide", "work")
        self.assertEqual(broken.exit_code, 1)
        self.assertIn("workflow", broken.stderr)
        help_text = self.invoke("guide", "--help").stdout
        self.assertIn("chitty guide work TASK-12", help_text)


if __name__ == "__main__":
    unittest.main()
