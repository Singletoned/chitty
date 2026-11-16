import os
import sys

from chitty.errors import ChittyError
from chitty.store import Repo, ticket_action
from tests.test_review_merge import ReviewMergeTestCase


class TestRunReturnToPlanning(ReviewMergeTestCase):
    def return_from(self, source):
        self.run_cli("edit", "1", "--ac", "Contract", "--owner", "worker")
        self.git("switch", "--quiet", "-c", "task-1")
        (self.root / "work.txt").write_text("Partial implementation\n")
        self.git("add", "work.txt")
        self.git("commit", "--quiet", "-m", "partial implementation")
        self.run_cli("edit", "1", "-s", "doing")
        if source == "review":
            self.run_cli("edit", "1", "-s", "review")
        self.git("switch", "--quiet", "main")
        main_head = self.git("rev-parse", "main")
        log = self.logs / "return.log"
        fake = self.tmp / "bin" / "fake"
        fake.write_text(
            f"#!{sys.executable}\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            f"with Path({str(log)!r}).open('a') as stream:\n"
            "    stream.write(sys.argv[1] + '\\n')\n"
            "subprocess.run(['chitty', 'edit', sys.argv[2], '-s', 'planning', '--note',\n"
            "    'Review failed (design): contract missing; planning must choose it.\\n'\n"
            "    '1: fail - missing contract'], check=True)\n"
        )
        result = self.run_cli("run", "--ticket", "TASK-1")
        self.assertEqual(result.stdout, f"TASK-1: {source} → planning\n")
        self.assertEqual(log.read_text(), f"{'review' if source == 'review' else 'work'}\n")
        self.assertEqual(self.git("rev-parse", "main"), main_head)
        self.assertTrue((self.worktree / ".git").exists())
        self.assertEqual((self.worktree / "work.txt").read_text(), "Partial implementation\n")
        self.git("show-ref", "--verify", "refs/heads/task-1")
        self.assertEqual(len(self.git("worktree", "list", "--porcelain").split("worktree ")) - 1, 2)
        repo = Repo.open(self.root)
        stored = repo.find(repo.resolve("1"))
        self.assertEqual(stored.task.frontmatter.status, "planning")
        self.assertIsNone(stored.task.frontmatter.owner)
        self.assertIn("TASK-1", self.run_cli("list", "-s", "planning").stdout)
        self.run_cli("next", exit_code=3)
        with self.assertRaisesRegex(ChittyError, "status is planning"):
            ticket_action(repo, repo.resolve("1"))
        # The returned ticket remains on its branch and can be planned there.
        os.chdir(self.worktree)
        self.run_cli("edit", "1", "--description", "Contract decided in planning.")
        self.assertEqual(self.git("rev-parse", "main"), main_head)

    def test_worker_return_stops_without_landing_or_losing_work(self):
        self.return_from("doing")

    def test_reviewer_return_stops_without_landing_or_losing_work(self):
        self.return_from("review")
