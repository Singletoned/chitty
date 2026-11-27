import os
import string
import subprocess
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from unittest.mock import patch

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.git import _git, squash_bookkeeping
from chitty.ids import TaskId
from tests import examples

DIRECTORIES = (PurePosixPath("chitty/tasks"), PurePosixPath("chitty/human"))
TASK = TaskId.parse("TASK-1")
letters = st.text(string.ascii_letters + string.digits + " ", max_size=20)
names = st.text(string.ascii_lowercase + string.digits, min_size=1, max_size=20)
subjects = st.text(string.printable[:95], min_size=1, max_size=20).filter(lambda s: bool(s.strip()))
authors = st.text(string.ascii_letters + string.digits, min_size=1, max_size=20)


class SquashGitTest(unittest.TestCase):
    def setup_repo(self, tmp):
        main = Path(tmp) / "main"
        main.mkdir()
        self.git(main, "init", "-b", "main")
        self.git(main, "config", "user.name", "Test")
        self.git(main, "config", "user.email", "test@example.com")
        self.put(main, "chitty/tasks/TASK-1--t.md", "initial")
        self.put(main, "src/a.py", "initial")
        self.git(main, "add", ".")
        self.git(main, "commit", "-m", "initial")
        branch = Path(tmp) / "branch"
        self.git(main, "worktree", "add", "-b", "task-1", str(branch))
        return main, branch

    def git(self, root, *args, env=None):
        return subprocess.run(
            ["git", *args], cwd=root, env=env, text=True, capture_output=True, check=True
        ).stdout.strip()

    def put(self, root, path, text):
        file = root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text)

    def commit(self, root, subject, index, author="Test"):
        self.git(root, "add", "-A")
        env = os.environ | {
            "GIT_AUTHOR_NAME": author,
            "GIT_AUTHOR_EMAIL": "author@example.com",
            "GIT_AUTHOR_DATE": f"2020-01-01T00:00:{index:02d}+00:00",
        }
        self.git(root, "-c", "commit.cleanup=verbatim", "commit", "-m", subject, env=env)

    def squash(self, root):
        return squash_bookkeeping(root, "main", "task-1", TASK, DIRECTORIES)

    @settings(max_examples=examples(20), deadline=None)
    @given(
        st.lists(
            st.tuples(st.booleans(), st.booleans(), letters, names, subjects, authors),
            min_size=2,
            max_size=6,
        )
    )
    def test_histories(self, draws):
        with tempfile.TemporaryDirectory() as tmp:
            _, root = self.setup_repo(tmp)
            ticket = "chitty/tasks/TASK-1--t.md"
            expected = []
            count = 0
            for i, (book, rename, text, name, subject, author) in enumerate(draws):
                if book:
                    count += 1
                    if rename:
                        new = f"chitty/tasks/TASK-1--{name}{i}.md"
                        (root / ticket).rename(root / new)
                        ticket = new
                    self.put(root, ticket, f"{text} {i}")
                    self.commit(root, "chitty: edit TASK-1", i, author)
                else:
                    self.put(root, f"src/{name}{i}.py", f"{text} {i}")
                    self.commit(root, subject.strip(), i, author)
                    expected.append(
                        (
                            self.git(root, "show", "-s", "--format=%s%n%an%n%aI", "HEAD"),
                            self.git(root, "rev-parse", "HEAD:src"),
                        )
                    )
            old = self.git(root, "rev-parse", "HEAD")
            tree = self.git(root, "rev-parse", "HEAD^{tree}")
            self.assertEqual(self.squash(root), count if count >= 2 else 0)
            self.assertEqual(self.git(root, "rev-parse", "HEAD^{tree}"), tree)
            if count < 2:
                self.assertEqual(self.git(root, "rev-parse", "HEAD"), old)
                return
            shas = self.git(root, "rev-list", "--reverse", "main..HEAD").splitlines()
            self.assertEqual(len(shas), len(expected) + 1)
            for sha, (metadata, src_tree) in zip(shas, expected):
                self.assertEqual(
                    self.git(root, "show", "-s", "--format=%s%n%an%n%aI", sha), metadata
                )
                self.assertEqual(self.git(root, "rev-parse", f"{sha}:src"), src_tree)
            self.assertEqual(
                self.git(root, "show", "-s", "--format=%B", "HEAD"),
                f"chitty: land TASK-1\n\nSquashed {count} Chitty bookkeeping commits."
                "\n\nTask: TASK-1",
            )
            paths = self.git(
                root, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
            ).splitlines()
            self.assertTrue(all(p.startswith("chitty/tasks/") for p in paths))

    def test_not_rebased(self):
        with tempfile.TemporaryDirectory() as tmp:
            main, root = self.setup_repo(tmp)
            old = self.git(root, "rev-parse", "HEAD")
            self.put(main, "src/b.py", "change")
            self.commit(main, "main change", 1)
            with self.assertRaisesRegex(ChittyError, "rebase.*main"):
                self.squash(root)
            self.assertEqual(self.git(root, "rev-parse", "HEAD"), old)

    def test_mixed_commit(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, root = self.setup_repo(tmp)
            for i in range(2):
                self.put(root, "chitty/tasks/TASK-1--t.md", str(i))
                self.commit(root, "chitty: edit TASK-1", i)
            self.put(root, "chitty/tasks/TASK-1--t.md", "mixed")
            self.put(root, "src/a.py", "mixed")
            self.commit(root, "implementation", 2)
            old = self.git(root, "rev-parse", "HEAD")
            self.assertEqual(self.squash(root), 0)
            self.assertEqual(self.git(root, "rev-parse", "HEAD"), old)

    def test_restore_failure_rolls_back(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, root = self.setup_repo(tmp)
            for i in range(2):
                self.put(root, "chitty/tasks/TASK-1--t.md", str(i))
                self.commit(root, "chitty: edit TASK-1", i)
            self.put(root, "src/a.py", "implementation")
            self.commit(root, "implementation", 2)
            old = self.git(root, "rev-parse", "HEAD")

            def fail_restore(path, *args):
                if "restore" in args:
                    raise ChittyError("injected")
                return _git(path, *args)

            with (
                patch("chitty.git._git", side_effect=fail_restore),
                self.assertRaisesRegex(ChittyError, "restore"),
            ):
                self.squash(root)
            self.assertEqual(self.git(root, "rev-parse", "HEAD"), old)
            self.assertEqual(self.git(root, "status", "--porcelain"), "")
