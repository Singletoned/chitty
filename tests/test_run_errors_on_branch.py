"""Runner failures are recorded on their ticket branch, not on main."""

import re
import stat
import sys

from tests.test_review_merge import ReviewMergeTestCase
from tests.test_run_claims_on_main import TestRunClaimsOnMain


class TestRunErrorsOnBranch(TestRunClaimsOnMain):
    def make_doing_branch(self) -> None:
        self.run_cli("edit", "TASK-1", "-s", "doing")
        self.git("branch", "task-1", "main")

    def set_setup_failure_on_main(self) -> str:
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('setup = "true"', 'setup = "false"'))
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "fail setup")
        return self.git("rev-parse", "main").strip()

    def test_work_setup_failure_is_only_recorded_on_branch(self):
        self.make_doing_branch()
        before = self.set_setup_failure_on_main()

        self.run_cli("run", "--ticket", "TASK-1")

        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        self.assert_branch_error("setup", "setup exited with status 1")
        self.assert_main_error_visible()
        self.assertIn("status: doing", self.main_ticket())

    def test_agent_failure_keeps_error_and_message_on_branch(self):
        self.make_doing_branch()
        fake = self.root / "bin" / "fake"
        fake.write_text("#!" + sys.executable + "\nraise SystemExit(7)\n")
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        before = self.git("rev-parse", "main").strip()

        result = self.run_cli("run", "--ticket", "TASK-1")

        self.assertEqual(self.git("rev-parse", "main").strip(), before)
        self.assert_branch_error("agent", "7")
        self.assert_main_error_visible()
        self.assertIn("status: doing", self.main_ticket())
        self.assertIn("doing → error", result.stdout)

    def assert_branch_error(self, phase: str, message: str) -> None:
        ticket = next((self.root / ".worktrees/task-1/chitty/tasks").glob("*.md"))
        text = ticket.read_text()
        self.assertIn("status: error", text)
        self.assertIn(f"Runner error ({phase})", text)
        self.assertIn(message, text)

    def main_ticket(self) -> str:
        return self.git("show", "main:chitty/tasks/TASK-1--claim-me.md")

    def assert_main_error_visible(self) -> None:
        from chitty.store import Repo, next_action

        self.assertEqual(self.json("show", "TASK-1")["status"], "error")
        self.assertEqual(str(next_action(Repo.open(self.root), modes=("errors",)).id), "TASK-1")


class TestReviewSetupErrorOnBranch(ReviewMergeTestCase):
    def test_review_setup_failure_keeps_main_unchanged(self):
        self.run_cli("edit", "TASK-1", "-s", "doing")
        self.run_cli("edit", "TASK-1", "-s", "review")
        self.git("switch", "--quiet", "-c", "task-1")
        (self.root / "work.txt").write_text("work\n")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "work")
        self.git("switch", "--quiet", "main")
        config = self.root / "chitty.toml"
        config.write_text(
            re.sub(r"^setup = .*", 'setup = "false"', config.read_text(), flags=re.MULTILINE)
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "fail review setup")
        main_head = self.git("rev-parse", "main").strip()
        main_status = self.git("show", "main:chitty/tasks/TASK-1--review-me.md")

        self.run_cli("run", "--mode", "review")

        self.assertEqual(self.git("rev-parse", "main").strip(), main_head)
        self.assertIn("status: review", main_status)
        self.assertEqual(self.ticket().frontmatter.status, "error")
        self.assertEqual(self.json("show", "TASK-1")["status"], "error")
        from chitty.store import Repo, next_action

        self.assertEqual(str(next_action(Repo.open(self.root), modes=("errors",)).id), "TASK-1")
        self.assertIn("Runner error (setup)", self.ticket().section("Notes") or "")
