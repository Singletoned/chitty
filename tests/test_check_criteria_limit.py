import os
import shutil
from datetime import date

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.check import MAX_CRITERIA, check
from chitty.model import STATUSES
from chitty.store import Repo
from tests import examples
from tests.support import RepoTestCase


class TestCriteriaLimit(RepoTestCase):
    @settings(max_examples=examples(40), deadline=None)
    @given(
        st.lists(
            st.tuples(
                st.sampled_from(STATUSES),
                st.lists(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1), max_size=10),
                st.booleans(),
            ),
            min_size=1,
            max_size=12,
        )
    )
    def test_warning_paths_and_messages_match_property(self, examples):
        os.environ["CHITTY_ACTOR"] = "test-agent"
        for directory in (self.root / "chitty").glob("*"):
            if directory.is_dir():
                shutil.rmtree(directory)
            else:
                directory.unlink()
        repo = Repo.open(self.root)
        context = repo.context("tasks")
        expected = {}
        for index, (status, criteria, archived) in enumerate(examples, start=1):
            task = repo.add(
                context,
                f"Ticket {index}",
                "Description.",
                criteria,
                {"status": "review" if status == "done" else status},
                date(2026, 1, 1),
            ).task
            path = task.path
            if status == "done":
                path.write_text(path.read_text().replace("status: review", "status: done"))
            if archived:
                archived_path = context.archive_directory / path.name
                archived_path.parent.mkdir(parents=True, exist_ok=True)
                path.rename(archived_path)
                path = archived_path
            if status in {"planning", "todo"} and len(criteria) > MAX_CRITERIA:
                expected[path] = f"{len(criteria)} acceptance criteria; split tickets above 5"

        problems = check(repo, repo.contexts(), [])
        actual = [
            (problem.path, problem.message)
            for problem in problems
            if problem.severity == "warning"
            and "acceptance criteria; split tickets above" in problem.message
        ]
        self.assertCountEqual(actual, expected.items())
