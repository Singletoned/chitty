import os
from datetime import date

from click.testing import CliRunner
from hypothesis import given
from hypothesis import strategies as st

from chitty.cli import cli
from chitty.model import STATUSES, parse
from chitty.store import Repo, guide
from tests.support import RepoTestCase


class TestColdReadGuide(RepoTestCase):
    def setUp(self):
        super().setUp()
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        os.environ["CHITTY_ACTOR"] = "test-agent"
        repo = Repo.open(self.root)
        self.path = repo.add(
            repo.context("tasks"),
            "Ticket",
            "Description",
            [],
            {"status": "cold-read"},
            date(2026, 1, 1),
        ).task.path

    def test_names_the_ticket_first(self):
        result = CliRunner().invoke(cli, ["guide", "cold-read", "TASK-1"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            result.stdout,
            "Work only on Chitty ticket TASK-1.\n\n"
            + guide("cold-read", directory=self.root, workflow="runner"),
        )

    def test_outside_repository_refuses_ticket(self):
        os.chdir(self.tmp)
        result = CliRunner().invoke(cli, ["guide", "cold-read", "TASK-1"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stdout, "")
        self.assertTrue(result.stderr)

    def test_missing_ticket_is_refused(self):
        result = CliRunner().invoke(cli, ["guide", "cold-read", "TASK-2"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("TASK-2", result.stderr)

    @given(status=st.sampled_from(STATUSES))
    def test_ticket_status(self, status):
        self.path.write_text(parse(self.path.read_text()).with_field("status", status).render())
        result = CliRunner().invoke(cli, ["guide", "cold-read", "TASK-1"], catch_exceptions=False)
        if status == "cold-read":
            self.assertEqual(result.exit_code, 0, result.output)
            self.assertEqual(
                result.stdout,
                "Work only on Chitty ticket TASK-1.\n\n"
                + guide("cold-read", directory=self.root, workflow="runner"),
            )
        else:
            self.assertEqual(result.exit_code, 1, result.output)
            self.assertEqual(result.stdout, "")
            self.assertIn(f"TASK-1 is {status} in this checkout, not cold-read", result.stderr)
