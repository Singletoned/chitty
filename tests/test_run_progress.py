"""`chitty run` says when the check has passed and the agent has started."""

from tests.test_review_merge import ReviewMergeTestCase


class TestRunProgress(ReviewMergeTestCase):
    def test_passing_check_announces_the_agent(self):
        self.branch_for_review()

        result = self.run_cli("run", "--mode", "review")

        check = result.stderr.index(f"Running check in {self.worktree}...")
        agent = result.stderr.index("Check passed; review agent is working on TASK-1...")
        self.assertLess(check, agent)

    def test_failing_check_does_not_announce_the_agent(self):
        self.branch_for_review()
        (self.logs / "fail_landing_check").write_text("fail")
        (self.root / "main-late.txt").write_text("make the check fail\n")
        self.git("add", "main-late.txt")
        self.git("commit", "--quiet", "-m", "fail the check")

        result = self.run_cli("run", "--mode", "review")

        self.assertIn("TASK-1: review → error", result.stdout)
        self.assertIn("Running check in", result.stderr)
        self.assertNotIn("agent is working", result.stderr)
