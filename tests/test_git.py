import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty import git
from chitty.errors import ChittyError
from tests import examples
from tests.support import RepoTestCase

# Standard output for non-zero statuses: `true`, padded `true`, or any text.
STDOUTS = st.one_of(st.sampled_from(("true", " \ttrue ")), st.text())


class TestRepositoryAnswer(RepoTestCase):
    command = ("git", "rev-parse", "--is-inside-work-tree")
    not_repository = "not a git repository"

    @settings(max_examples=examples(30), deadline=None)
    @given(st.text())
    def test_success_requires_exact_true_output(self, stderr):
        self.assertTrue(git.repository_answer(self.command, self.root, 0, " \ttrue\n", stderr))
        for stdout in ("false", "True", "TRUE", "truex", "xtrue", "true false", ""):
            self.assertFalse(git.repository_answer(self.command, self.root, 0, stdout, stderr))

    @settings(max_examples=examples(30), deadline=None)
    @given(st.text().filter(lambda text: text.strip() != "true"), st.text())
    def test_success_other_output_is_false(self, stdout, stderr):
        self.assertFalse(git.repository_answer(self.command, self.root, 0, stdout, stderr))

    def assert_error_context(self, directory, stderr, code, stdout):
        with self.assertRaises(ChittyError) as raised:
            git.repository_answer(self.command, directory, code, stdout, stderr)
        message = str(raised.exception)
        self.assertIn("`git rev-parse --is-inside-work-tree`", message)
        self.assertIn(str(directory), message)
        self.assertIn(stderr.strip(), message)

    @settings(max_examples=examples(50), deadline=None)
    @given(
        st.integers(min_value=-64, max_value=255).filter(lambda code: code != 0),
        st.text(),
        st.text(),
        STDOUTS,
        st.text(),
    )
    def test_phrase_only_classifies_status_128(self, code, before, after, stdout, directory_name):
        stderr = before + self.not_repository + after
        directory = self.root / directory_name
        if code == 128:
            self.assertFalse(git.repository_answer(self.command, directory, code, stdout, stderr))
        else:
            self.assert_error_context(directory, stderr, code, stdout)

    @settings(max_examples=examples(50), deadline=None)
    @given(st.text(), st.text(), STDOUTS, st.text())
    def test_status_128_phrase_always_means_not_a_repository(
        self, before, after, stdout, directory_name
    ):
        stderr = before + self.not_repository + after
        answer = git.repository_answer(
            self.command, self.root / directory_name, 128, stdout, stderr
        )
        self.assertFalse(answer)

    @settings(max_examples=examples(30), deadline=None)
    @given(
        st.sampled_from(("Not a git repository", "NOT A GIT REPOSITORY")),
        STDOUTS,
        st.text(),
    )
    def test_repository_phrase_is_case_sensitive(self, stderr, stdout, directory_name):
        self.assert_error_context(self.root / directory_name, stderr, 128, stdout)

    @settings(max_examples=examples(100), deadline=None)
    @given(
        st.integers(min_value=-64, max_value=255).filter(lambda code: code != 0),
        st.text().filter(lambda text: "not a git repository" not in text),
        STDOUTS,
        st.text(),
    )
    def test_other_failures_raise_with_context(self, code, stderr, stdout, directory_name):
        self.assert_error_context(self.root / directory_name, stderr, code, stdout)

    def test_status_128_without_repository_phrase_raises(self):
        self.assert_error_context(self.root, "", 128, "true")

    @settings(max_examples=examples(100), deadline=None)
    @given(st.integers(), st.text(), st.text())
    def test_arbitrary_results_return_bool_or_raise_chitty_error(self, code, stdout, stderr):
        try:
            result = git.repository_answer(self.command, self.root, code, stdout, stderr)
        except ChittyError:
            return
        self.assertIs(type(result), bool)


class TestIsRepository(RepoTestCase):
    @settings(max_examples=examples(30), deadline=None)
    @given(
        depth=st.integers(min_value=1, max_value=4),
        marker=st.one_of(st.none(), st.integers(min_value=0, max_value=4)),
        kind=st.sampled_from(("directory", "file", "symlink")),
    )
    def test_missing_git_distinguishes_repository_markers(
        self, depth: int, marker: int | None, kind: str
    ):
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary).resolve()
            self.assertFalse(any(os.path.lexists(parent / ".git") for parent in base.parents))
            directories = [base]
            for _ in range(depth):
                child = directories[-1] / "nested"
                child.mkdir()
                directories.append(child)
            if marker is not None:
                level = min(marker, depth)
                marker_path = directories[level] / ".git"
                if kind == "directory":
                    marker_path.mkdir()
                elif kind == "file":
                    marker_path.touch()
                else:
                    marker_path.symlink_to(base / "missing-target")
            empty_path = base / "empty-path"
            empty_path.mkdir()
            with mock.patch.dict(os.environ, {"PATH": str(empty_path)}):
                if marker is None:
                    self.assertFalse(git.is_repository(directories[-1]))
                else:
                    with self.assertRaises(ChittyError) as raised:
                        git.is_repository(directories[-1])
                    message = str(raised.exception)
                    self.assertIn("`git`", message)
                    self.assertIn("PATH", message)
                    self.assertIn(str(directories[min(int(marker), depth)] / ".git"), message)

    def test_invalid_directories_raise_with_or_without_git(self):
        path = self.tmp / "missing"
        regular_file = self.tmp / "file"
        regular_file.touch()
        empty_path = self.tmp / "empty-path"
        empty_path.mkdir()
        for git_path in (os.environ["PATH"], str(empty_path)):
            with mock.patch.dict(os.environ, {"PATH": git_path}):
                for invalid in (path, regular_file):
                    with self.assertRaisesRegex(ChittyError, str(invalid.resolve())):
                        git.is_repository(invalid)

    def test_repository_detection_without_missing_git(self):
        self.git_init()
        nested = self.root / "nested"
        nested.mkdir()
        self.assertTrue(git.is_repository(self.root))
        self.assertTrue(git.is_repository(nested))
        self.assertFalse(git.is_repository(self.root / ".git"))
        with tempfile.TemporaryDirectory() as temporary:
            self.assertFalse(git.is_repository(Path(temporary)))

    def test_invalid_repository_format_raises(self):
        self.git_init()
        config = self.root / ".git" / "config"
        config.write_text(
            config.read_text().replace(
                "repositoryformatversion = 0", "repositoryformatversion = 99"
            )
        )
        with self.assertRaisesRegex(ChittyError, "found 99"):
            git.is_repository(self.root)

    def test_not_repository_detection_uses_c_locale(self):
        fake_bin = self.tmp / "fake-bin"
        fake_bin.mkdir()
        fake_git = fake_bin / "git"
        fake_git.write_text(
            "#!/bin/sh\n"
            'if [ "$LC_ALL" = C ]; then\n'
            '  echo "fatal: not a git repository" >&2\n'
            "else\n"
            '  echo "Schwerwiegend: Kein Git-Repository" >&2\n'
            "fi\n"
            "exit 128\n"
        )
        fake_git.chmod(0o755)
        with (
            tempfile.TemporaryDirectory() as temporary,
            mock.patch.dict(os.environ, {"PATH": str(fake_bin), "LANG": "de_DE.UTF-8"}),
        ):
            os.environ.pop("LC_ALL", None)
            self.assertFalse(git.is_repository(Path(temporary)))

    def git_init(self):
        subprocess.run(["git", "init", "--quiet"], cwd=self.root, check=True)


class TestWorktreeForBranch(RepoTestCase):
    def test_non_repository_surfaces_git_failure(self):
        with self.assertRaisesRegex(ChittyError, "git worktree list"):
            git.worktree_for_branch(self.root, "task-1")


class TestRebaseOnto(RepoTestCase):
    def setUp(self):
        super().setUp()
        self._git("init", "--quiet", "-b", "main")
        self._git("config", "user.email", "test@example.com")
        self._git("config", "user.name", "Test")
        (self.root / "shared.txt").write_text("base\n")
        self._commit("base")
        self._git("checkout", "-b", "task-1")

    def _git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        )
        return result.stdout

    def _commit(self, message: str) -> None:
        self._git("add", "--all")
        self._git("commit", "--quiet", "-m", message)

    def test_clean_rebase_returns_empty(self):
        (self.root / "branch.txt").write_text("branch\n")
        self._commit("branch change")
        self._git("checkout", "main")
        (self.root / "main.txt").write_text("main\n")
        self._commit("main change")
        self._git("checkout", "task-1")

        self.assertEqual(git.rebase_onto(self.root, "main"), [])
        self.assertFalse(git.rebase_in_progress(self.root))
        self.assertTrue(git.is_ancestor(self.root, "main", "task-1"))

    def test_conflicting_rebase_preserves_paths_containing_spaces(self):
        (self.root / "shared.txt").rename(self.root / "shared file.txt")
        self._commit("rename shared file")
        path = self.root / "shared file.txt"
        path.write_text("branch\n")
        self._commit("branch change")
        self._git("checkout", "main")
        (self.root / "shared file.txt").write_text("main\n")
        self._commit("main change")
        self._git("checkout", "task-1")

        self.assertEqual(git.rebase_onto(self.root, "main"), ["shared file.txt"])
        self.assertTrue(git.rebase_in_progress(self.root))
        self.assertEqual(
            self._git("diff", "--name-only", "--diff-filter=U").splitlines(),
            ["shared file.txt"],
        )


class TestBranchTipFiles(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        )
        return result.stdout

    def commit(self, message: str) -> str:
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)
        return self.git("rev-parse", "HEAD").strip()

    def test_branch_tips_keep_full_refs_distinct(self):
        (self.root / "base").write_text("base")
        self.commit("base")
        self.git("branch", "origin/task-5")
        self.git("checkout", "-b", "task-5")
        (self.root / "different").write_text("different")
        remote = self.commit("different tip")
        local = self.git("rev-parse", "refs/heads/origin/task-5").strip()
        self.git("update-ref", "refs/remotes/origin/task-5", remote)
        self.git("symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/task-5")
        tips = git.branch_tips(self.root)
        self.assertEqual(tips["refs/heads/origin/task-5"], local)
        self.assertEqual(tips["refs/remotes/origin/task-5"], remote)
        self.assertNotEqual(tips["refs/heads/origin/task-5"], tips["refs/remotes/origin/task-5"])
        self.assertNotIn("refs/remotes/origin/HEAD", tips)

    def test_ref_resolution_and_ancestry(self):
        (self.root / "one").write_text("one")
        first = self.commit("one")
        self.git("checkout", "-b", "worker")
        (self.root / "two").write_text("two")
        second = self.commit("two")
        self.assertTrue(git.is_ancestor(self.root, first, second))
        self.assertTrue(git.is_ancestor(self.root, first, first))
        self.assertFalse(git.is_ancestor(self.root, second, first))
        self.assertEqual(git.ref_commit(self.root, "worker"), second)
        self.assertIsNone(git.ref_commit(self.root, "missing"))
        self.git("checkout", "--orphan", "unborn")
        self.assertIsNone(git.ref_commit(self.root, "unborn"))
        self.git("checkout", "worker")
        self.git("tag", "-a", "annotated", "-m", "tag")
        self.assertEqual(git.ref_commit(self.root, "annotated"), second)
        with self.assertRaises(ChittyError):
            git.is_ancestor(self.root, "unknown", second)

    @settings(max_examples=examples(8), deadline=None)
    @given(
        st.dictionaries(
            st.tuples(
                st.sampled_from(("chitty/tasks", "chitty/tasks/archive")),
                st.integers(min_value=0, max_value=20),
            ),
            st.text(alphabet="abcé", min_size=1, max_size=12),
            min_size=1,
            max_size=8,
        )
    )
    def test_files_at_preserves_odd_paths_and_content(self, tree):
        shutil.rmtree(self.root / ".git", ignore_errors=True)
        shutil.rmtree(self.root / "chitty", ignore_errors=True)
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        expected = {}
        for (directory, index), content in tree.items():
            filename = f'{index}"quote\ttab\nnewline-é[x].md'
            path = Path(directory) / filename
            (self.root / path).parent.mkdir(parents=True, exist_ok=True)
            (self.root / path).write_text(content)
            expected[path] = content
        self.commit("tickets")
        self.assertEqual(dict(git.files_at(self.root, "main", [Path("chitty/tasks")])), expected)

    def test_files_at_rejects_non_utf8(self):
        path = Path("chitty/tasks/TASK-1.md")
        (self.root / path).parent.mkdir(parents=True, exist_ok=True)
        (self.root / path).write_bytes(b"\xff")
        self.commit("invalid utf8")
        with self.assertRaisesRegex(ChittyError, str(path)):
            git.files_at(self.root, "main", [Path("chitty/tasks")])

    def test_changed_since_split_literal_path_and_unrelated_history(self):
        path = Path("ticket[x].md")
        (self.root / path).write_text("base")
        self.commit("base")
        self.git("checkout", "-b", "against")
        (self.root / path).write_text("against")
        self.commit("against change")
        self.git("checkout", "-b", "ref", "main")
        self.assertFalse(git.changed_since_split(self.root, "ref", "against", [path]))
        (self.root / path).write_text("ref")
        self.commit("ref change")
        self.assertTrue(git.changed_since_split(self.root, "ref", "against", [path]))
        self.git("checkout", "--orphan", "other")
        self.git("rm", "-rf", ".")
        (self.root / "other").write_text("other")
        self.commit("unrelated")
        with self.assertRaisesRegex(ChittyError, "unrelated histories"):
            git.changed_since_split(self.root, "other", "main", [path])
