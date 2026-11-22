import os
import string
import subprocess
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tests.test_cli import CliTestCase


def git_refuses(name: str) -> bool:
    """Whether `git add` refuses a path component named `name`.

    Git's `core.protectNTFS` and `core.protectHFS` treat `.GIT`, `.Git` and
    `.git.` as `.git`, so `git add` fails with `invalid path`.
    """
    return name.rstrip(".").lower() == ".git"


# Names a hidden-entry strategy can draw, some of which git refuses.
GIT_NAME_CASES = [".GIT", ".Git", ".git.", ".gIt..", ".gitx", ".git~1", ".github"]


class TestHiddenEntries(CliTestCase):
    def test_git_refuses_matches_git(self):
        for name in GIT_NAME_CASES:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                subprocess.run(["git", "init", "-q", temp], check=True)
                (Path(temp) / name).mkdir()
                (Path(temp) / name / "file").write_text("x")
                added = subprocess.run(
                    ["git", "add", f"{name}/file"], check=False, cwd=temp, capture_output=True
                )
                self.assertEqual(added.returncode != 0, git_refuses(name))

    def test_non_hidden_file_remains_an_error(self):
        self.run_cli("add", "One", "-d", "x")
        (self.root / "chitty/tasks/notes.txt").write_text("x")
        self.assertIn("must end with .md", self.run_cli("list", exit_code=1).output)
        self.assertIn("must end with .md", self.run_cli("check", exit_code=1).output)

    @settings(max_examples=25, deadline=None)
    @given(
        entries=st.lists(
            st.tuples(
                st.one_of(
                    st.sampled_from([".gitkeep", ".DS_Store"]),
                    st.text(
                        alphabet=string.ascii_letters + string.digits + "-_.",
                        min_size=1,
                        max_size=200,
                    )
                    .map(lambda x: "." + x)
                    .filter(lambda x: x != ".." and not git_refuses(x)),
                ),
                st.sampled_from(["tasks", "human", "tasks/archive", "human/archive"]),
                st.booleans(),
                st.booleans(),
            ),
            min_size=1,
            max_size=4,
            unique_by=lambda entry: (entry[0], entry[1]),
        ),
        contexts=st.lists(st.sampled_from(["tasks", "human"]), min_size=1, max_size=3),
        archive=st.booleans(),
    )
    def test_hidden_entries(self, entries, contexts, archive):
        with tempfile.TemporaryDirectory() as temp:
            old = Path.cwd()
            os.chdir(temp)
            try:
                Path("chitty.toml").write_text((self.root / "chitty.toml").read_text())
                subprocess.run(["git", "init", "-q"], check=True)
                subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)
                subprocess.run(["git", "config", "user.name", "Test"], check=True)
                counts = {"tasks": 0, "human": 0}
                tickets = []
                for context in contexts:
                    counts[context] += 1
                    ticket = f"{'TASK' if context == 'tasks' else 'HUMAN'}-{counts[context]}"
                    self.run_cli("add", "One", "-d", "x", "-c", context)
                    tickets.append(ticket)
                    if context == "human" and archive:
                        self.run_cli("archive", ticket)
                subprocess.run(["git", "add", "."], check=True)
                subprocess.run(["git", "commit", "-qm", "initial"], check=True)
                before = self.run_cli("list", "--all", "--json").stdout
                shows = {ticket: self.run_cli("show", ticket).stdout for ticket in tickets}
                for name, location, directory, committed in entries:
                    path = Path("chitty") / location / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    if directory:
                        path.mkdir()
                        (path / "file").write_text("x")
                    else:
                        path.touch()
                    if committed:
                        subprocess.run(["git", "add", "-f", str(path)], check=True)
                        subprocess.run(["git", "commit", "-qm", "hidden"], check=True)
                self.assertEqual(self.run_cli("list", "--all", "--json").stdout, before)
                for ticket, show in shows.items():
                    self.assertEqual(self.run_cli("show", ticket).stdout, show)
                self.run_cli("check")
                result = self.run_cli("add", "Two", "-d", "x")
                self.assertIn(f"TASK-{counts['tasks'] + 1}", result.stdout)
            finally:
                os.chdir(old)
