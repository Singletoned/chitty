import unittest
from functools import partial
from pathlib import PurePosixPath

from hypothesis import find, given, settings
from hypothesis import strategies as st

from chitty.check import unfinished_landed
from chitty.git import TrailerCommit
from chitty.ids import TaskId
from chitty.model import STATUSES

DIRECTORIES = tuple(map(PurePosixPath, ("chitty/tasks", "chitty/human", "chitty/backlog")))


@st.composite
def cases(draw):
    numbers = draw(st.lists(st.integers(1, 12), min_size=2, max_size=5, unique=True))
    ids = [TaskId("TASK", n) for n in numbers]
    values = draw(
        st.lists(
            st.one_of(st.none(), st.sampled_from(STATUSES)), min_size=len(ids), max_size=len(ids)
        )
    )
    statuses = {task: value for task, value in zip(ids, values) if value is not None}
    shas = draw(st.lists(st.integers(0, 2**160 - 1), min_size=1, max_size=8, unique=True))
    commits = []
    for sha in shas:
        subject = draw(st.text(alphabet="abc :", max_size=8))
        if draw(st.booleans()):
            subject = "chitty: " + subject
        selected = draw(st.lists(st.sampled_from(ids), unique=True))
        if draw(st.booleans()):
            selected.append(TaskId("TASK", draw(st.integers(100, 103))))
        names = st.text(alphabet="abc", min_size=1, max_size=3)
        paths = draw(
            st.lists(
                st.tuples(
                    st.sampled_from(
                        (
                            "chitty/tasks",
                            "chitty/human/archive",
                            "chitty/backlog",
                            "chitty/tasksX",
                            "src",
                        )
                    ),
                    names,
                ),
                max_size=3,
            )
        )
        commits.append(
            TrailerCommit(
                f"{sha:040x}",
                subject,
                tuple(selected),
                tuple(
                    PurePosixPath(f"{base}/{name}.{'py' if base == 'src' else 'md'}")
                    for base, name in paths
                ),
            )
        )
    return commits, statuses


def landed_mismatch(function, commits, statuses):
    expected = {}
    for commit in commits:
        if commit.subject.startswith("chitty: ") or not any(
            all(not path.is_relative_to(d) for d in DIRECTORIES) for path in commit.paths
        ):
            continue
        for task in commit.task_ids:
            if task in statuses and statuses[task] != "done":
                expected.setdefault(task, commit.sha)
    actual = function(commits, statuses, DIRECTORIES)
    return None if actual == expected else f"expected {expected}, got {actual}"


def mismatch_case(function, case):
    return landed_mismatch(function, *case) is not None


def mutant(commits, statuses, directories, mode):
    result = {}
    for commit in commits:
        if mode != "subject" and commit.subject.startswith("chitty: "):
            continue
        if mode == "paths":
            work = True
        elif mode == "prefix":
            work = any(
                all(not str(p).startswith(str(d)) for d in directories) for p in commit.paths
            )
        else:
            work = any(all(not p.is_relative_to(d) for d in directories) for p in commit.paths)
        if work:
            for task in commit.task_ids:
                if task in statuses and statuses[task] != "done":
                    result.setdefault(task, commit.sha)
    return result


class UnfinishedLandedTests(unittest.TestCase):
    @given(cases())
    def test_property(self, case):
        self.assertIsNone(landed_mismatch(unfinished_landed, *case))

    def test_mutants(self):
        for mode in ("subject", "paths", "prefix"):
            with self.subTest(mode=mode):
                function = partial(mutant, mode=mode)

                example = find(
                    cases(),
                    partial(mismatch_case, function),
                    settings=settings(max_examples=200, deadline=None, database=None),
                )
                self.assertIsNotNone(landed_mismatch(function, *example))
