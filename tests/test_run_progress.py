"""`chitty run` says when the check has passed and the agent has started."""

from tests.test_review_merge import ReviewMergeTestCase


class TestRunProgress(ReviewMergeTestCase):
    def test_passing_check_announces_the_agent(self):
        self.branch_for_review()

        result = self.run_cli("run", "--mode", "review")

        check = result.stderr.splitlines().index("TASK-1: running check in .worktrees/task-1...")
        agent = result.stderr.splitlines().index(
            "Check passed; review agent is working on TASK-1..."
        )
        self.assertLess(check, agent)

    def test_failing_check_does_not_announce_the_agent(self):
        self.branch_for_review()
        (self.logs / "fail_landing_check").write_text("fail")
        (self.root / "main-late.txt").write_text("make the check fail\n")
        self.git("add", "main-late.txt")
        self.git("commit", "--quiet", "-m", "fail the check")

        result = self.run_cli("run", "--mode", "review")

        self.assertIn("TASK-1: review → error", result.stdout)
        self.assertIn("running check in", result.stderr)
        self.assertNotIn("agent is working", result.stderr)

    def test_review_log_path_is_relative(self):
        self.branch_for_review()
        result = self.run_cli("run", "--mode", "review")
        self.assertTrue(
            any(
                line.startswith("log: .git/chitty/run/TASK-1-")
                for line in result.stderr.splitlines()
            )
        )
