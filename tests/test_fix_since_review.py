import os
import subprocess
import time
import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.store import has_fix_since
from tests.test_leave_doing_clean import TestLeaveDoingClean


class TestHasFixSince(unittest.TestCase):
    @given(
        st.integers(),
        st.lists(
            st.tuples(st.integers(), st.one_of(st.text(), st.text().map(lambda s: "chitty: " + s)))
        ),
    )
    def test_exactly_later_non_bookkeeping(self, failed_at, commits):
        expected = any(t > failed_at and not s.startswith("chitty: ") for t, s in commits)
        self.assertEqual(has_fix_since(failed_at, commits), expected)


class TestFixSinceReview(TestLeaveDoingClean):
    def test_failed_review_requires_new_commit_even_after_rebase(self):
        self.make_worktree()
        self.git("commit", "--allow-empty", "-m", "old fix", cwd=self.worktree)
        self.run_cli("edit", "TASK-1", "-s", "review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        self.run_cli("edit", "TASK-1", "-s", "doing", "--note", "Review failed (work): fix it")
        os.environ["CHITTY_ACTOR"] = "worker"
        history = self.json("show", "TASK-1")["history"]
        failed_at = [line.split()[1] for line in history.splitlines() if "review → doing" in line][
            -1
        ]
        head = self.git("rev-parse", "HEAD", cwd=self.worktree)
        ticket = self.run_cli("show", "TASK-1").output
        result = self.run_cli("edit", "TASK-1", "-s", "review", exit_code=1)
        self.assertIn(
            f"cannot move TASK-1 to review: no commit since the failed review at {failed_at}; "
            "commit the fix first",
            result.output,
        )
        self.assertEqual(head, self.git("rev-parse", "HEAD", cwd=self.worktree))
        self.assertEqual(ticket, self.run_cli("show", "TASK-1").output)
        env = dict(os.environ, GIT_AUTHOR_DATE=f"@{int(time.time()) + 5} +0000")
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "main change"],
            cwd=self.root,
            env=env,
            check=True,
            capture_output=True,
        )
        self.git("rebase", "main", cwd=self.worktree)
        self.run_cli("edit", "TASK-1", "-s", "review", exit_code=1)
        env = dict(os.environ, GIT_AUTHOR_DATE=f"@{int(time.time()) + 5} +0000")
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "fix"],
            cwd=self.worktree,
            env=env,
            check=True,
            capture_output=True,
        )
        self.run_cli("edit", "TASK-1", "-s", "review")
