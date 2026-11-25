import tempfile
from pathlib import Path
from unittest.mock import patch

from hypothesis import example, given, settings
from hypothesis import strategies as st

from chitty import git
from chitty.errors import ChittyError
from chitty.store import Repo
from tests import examples, test_source_copy
from tests.support import CONFIG, RepoTestCase


class TestRefSnapshot(RepoTestCase):
    git = test_source_copy.TestSourceCopy.git
    init_git = test_source_copy.TestSourceCopy.init_git
    commit = test_source_copy.TestSourceCopy.commit
    file = test_source_copy.TestSourceCopy.file

    def results(self):
        repo = Repo.open(self.root)
        ids = repo.ticket_ids()
        results = {}
        for task_id in ids:
            try:
                source = repo.source_of(task_id)
                copy = repo.source_copy(task_id)
                results[str(task_id)] = (
                    source,
                    None if copy is None else copy.task.frontmatter.title,
                )
            except ChittyError as error:
                results[str(task_id)] = str(error)
        return ids, results

    @settings(max_examples=examples(25), deadline=None)
    @example([(False, True, False, "delete")])
    @example([(True, True, False, "move")])
    @example([(True, True, True, "delete")])
    @given(
        st.lists(
            st.tuples(
                st.booleans(),
                st.booleans(),
                st.booleans(),
                st.sampled_from(["none", "delete", "move"]),
            ),
            min_size=1,
            max_size=3,
        )
    )
    def test_ref_snapshot(self, cases):
        with tempfile.TemporaryDirectory(dir=self.tmp) as directory:
            self.root = Path(directory)
            (self.root / "chitty.toml").write_text(CONFIG)
            self.init_git()
            for number, (on_main, _, _, _) in enumerate(cases, 1):
                if on_main:
                    self.file(number)
            self.commit()
            moves = {}
            for number, (on_main, branch_changes, _, action) in enumerate(cases, 1):
                self.git("checkout", "-b", f"task-{number}", "main")
                if branch_changes:
                    self.file(number, "branch")
                else:
                    (self.root / f"other-{number}").write_text("branch")
                self.commit()
                original = self.git("rev-parse", "HEAD")
                if action == "move":
                    self.file(number, "moved")
                    self.commit()
                    moves[number] = self.git("rev-parse", "HEAD")
                    self.git("reset", "--hard", original)
                self.git("checkout", "main")
            for number, (on_main, _, main_changes, _) in enumerate(cases, 1):
                if on_main and main_changes:
                    self.file(number, "main changed")
            self.commit()
            expected = self.results()
            branch_tips = git.branch_tips
            first = True

            def mutate(root):
                nonlocal first
                tips = branch_tips(root)
                if first:
                    first = False
                    for number, (_, _, _, action) in enumerate(cases, 1):
                        ref = f"refs/heads/task-{number}"
                        if action == "delete":
                            self.git("update-ref", "-d", ref)
                        elif action == "move":
                            self.git("update-ref", ref, moves[number])
                return tips

            with patch.object(git, "branch_tips", mutate):
                self.assertEqual(self.results(), expected)
