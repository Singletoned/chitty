import unittest

from hypothesis import given
from hypothesis import strategies as st

from chitty.git import Commit, commits_missing_trailer
from chitty.ids import TaskId
from chitty.store import Edit, Repo
from tests.test_review_merge import ReviewMergeTestCase


class TestCommitTrailers(unittest.TestCase):
    @given(
        st.lists(
            st.tuples(
                st.booleans(),
                st.lists(
                    st.lists(
                        st.tuples(
                            st.sampled_from(
                                ("Task: TASK-1", "Task: TASK-2", "Other: value", "text")
                            ),
                            st.sampled_from(("", " ", "  ", "\t")),
                            st.sampled_from(("", " ", "  ", "\t")),
                        ),
                        max_size=3,
                    ),
                    max_size=4,
                ),
            ),
            max_size=20,
        )
    )
    def test_missing_trailers(self, samples):
        commits = []
        expected = []
        for index, (chitty, paragraphs) in enumerate(samples):
            subject = "chitty: generated" if chitty else "Fix"
            message = subject
            for paragraph in paragraphs:
                message += "\n\n" + "\n".join(
                    f"{before}{line}{after}" for line, before, after in paragraph
                )
            message += "\n\n" * (index % 3)
            commit = Commit(str(index), message)
            commits.append(commit)
            last_paragraph = paragraphs
            while last_paragraph and not any(line.strip() for line, _, _ in last_paragraph[-1]):
                last_paragraph = last_paragraph[:-1]
            has_trailer = bool(last_paragraph) and any(
                line.strip() == "Task: TASK-1" for line, _, _ in last_paragraph[-1]
            )
            if not chitty and not has_trailer:
                expected.append(commit)
        self.assertEqual(commits_missing_trailer(commits, TaskId.parse("TASK-1")), expected)

    def test_examples(self):
        messages = (
            ("Task: TASK-1", True),
            ("Fix\n\nTask: TASK-1", False),
            ("Fix\n\nTask: TASK-1\n\nMore text", True),
            ("Fix\n\nTask: TASK-10", True),
        )
        for message, missing in messages:
            with self.subTest(message=message):
                result = commits_missing_trailer([Commit("sha", message)], TaskId.parse("TASK-1"))
                self.assertEqual(bool(result), missing)


class TestReviewTrailerGate(ReviewMergeTestCase):
    def test_review_entry_requires_trailer(self):
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", "doing")
        (self.root / "x").write_text("x\n")
        self.git("add", "x")
        self.git("commit", "--quiet", "-m", "Add x")
        sha = self.git("rev-parse", "--short", "HEAD").strip()
        result = self.run_cli("edit", "1", "-s", "review", exit_code=1)
        self.assertIn(sha, result.stderr)
        self.assertIn("Add x", result.stderr)
        repo = Repo.open(self.root)
        self.assertEqual(repo.find(repo.resolve("1")).task.frontmatter.status, "doing")
        self.git("commit", "--amend", "--quiet", "-m", "Add x\n\nTask: TASK-1")
        self.git("switch", "--quiet", "main")
        (self.root / "main-change").write_text("main\n")
        self.git("add", "main-change")
        self.git("commit", "--quiet", "-m", "main change")
        self.git("switch", "--quiet", "task-1")
        self.git("merge", "--quiet", "--no-edit", "main")
        (self.root / "chitty-commit").write_text("chitty\n")
        self.git("add", "chitty-commit")
        self.git("commit", "--quiet", "-m", "chitty: generated commit")
        self.run_cli("edit", "1", "-s", "review")

    def test_skip_current_version_bypasses_gate(self):
        self.git("switch", "--quiet", "-c", "task-1")
        (self.root / "untrailed").write_text("work\n")
        self.git("add", "untrailed")
        self.git("commit", "--quiet", "-m", "No trailer")
        repo = Repo.open(self.root)
        repo.edit(repo.resolve("1"), Edit(status="review", skip_current_version=True))
        updated = Repo.open(self.root)
        self.assertEqual(updated.find(updated.resolve("1")).task.frontmatter.status, "review")

    def test_review_to_done_does_not_gate(self):
        self.git("switch", "--quiet", "-c", "task-1")
        self.run_cli("edit", "1", "-s", "doing")
        repo = Repo.open(self.root)
        repo.edit(repo.resolve("1"), Edit(status="review", skip_current_version=True))
        (self.root / "extra").write_text("extra\n")
        self.git("add", "extra")
        self.git("commit", "--quiet", "-m", "No trailer")
        repo = Repo.open(self.root)
        repo.edit(
            repo.resolve("1"),
            Edit(
                status="done",
                note="Reviewed: no trailer gate applies on completion.",
                override_review_independence=True,
            ),
        )
