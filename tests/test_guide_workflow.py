"""`chitty guide` under each workflow."""

import os
import re
import tempfile
import unittest
from pathlib import Path

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

    def test_direct_guide_refuses_non_runner_workflows(self):
        from chitty.errors import ChittyError

        for workflow in ("tickets", "bogus", "", "Runner"):
            with self.subTest(workflow=workflow), self.assertRaises(ChittyError):
                guide("work", directory=self.root, workflow=workflow)

    def test_each_role_guide_is_refused(self):
        for role in ROLE_NAMES:
            for args in ((role,), (role, "TASK-1")):
                with self.subTest(args=args):
                    self.assert_refused(role, args)

    def assert_refused(self, role, args):
        result = self.invoke("guide", *args)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn(
            f'chitty guide {role} needs workflow = "runner" in the Chitty config',
            result.stderr,
        )

    def test_general_guide_and_help(self):
        result = self.invoke("guide")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, managed_guide("tickets"))
        help_result = self.invoke("guide", "--help")
        self.assertEqual(help_result.exit_code, 0)
        help_text = help_result.stdout
        for role in ROLE_NAMES:
            self.assertIsNone(re.search(rf"\b{re.escape(role)}\b", help_text, re.IGNORECASE))
        self.assertIn("chitty guide", help_text)


class TestRoleGuidesRunnerCompatibility(GuideWorkflowTestCase):
    def test_runner_guides(self):
        self.assert_compatibility()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                self.assert_compatibility()
            finally:
                os.chdir(self.root)

    def assert_compatibility(self):
        roles = Path(__file__).resolve().parents[1] / "src/chitty/roles"
        signals = (roles / "property-signals.md").read_text().rstrip()
        for role in ROLE_NAMES:
            text = (roles / f"{role}.md").read_text().replace("<!-- property-signals -->", signals)
            cases: list[tuple[str, ...]] = [()]
            if role not in {"plan", "setup"}:
                cases.append(("TASK-1",))
            for args in cases:
                with self.subTest(role=role, args=args):
                    result = self.invoke("guide", role, *args)
                    expected = ("Work only on Chitty ticket TASK-1.\n\n" if args else "") + text
                    self.assertEqual(
                        (result.exit_code, result.stderr, result.stdout), (0, "", expected)
                    )
        help_result = self.invoke("guide", "--help")
        self.assertEqual(help_result.exit_code, 0)
        self.assert_runner_help(help_result.stdout)

    def assert_runner_help(self, help_text):
        command = cli.commands["guide"]
        assert command.help is not None
        expected = " ".join(command.help.replace("\b", "").split())
        self.assertIn(expected, " ".join(help_text.split()))

    def test_outside_repository_and_broken_config(self):
        previous = os.getcwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, previous)
        self.assertEqual(
            self.invoke("guide", "work").stdout,
            guide("work", directory=self.tmp, workflow="runner"),
        )
        self.assertIn("chitty guide work TASK-12", self.invoke("guide", "--help").stdout)
        os.chdir(self.root)
        self.write_workflow("bogus")
        broken = self.invoke("guide", "work")
        self.assertEqual(broken.exit_code, 1)
        self.assertIn("workflow", broken.stderr)
        help_result = self.invoke("guide", "--help")
        self.assertEqual(help_result.exit_code, 0)
        self.assert_runner_help(help_result.stdout)


if __name__ == "__main__":
    unittest.main()
