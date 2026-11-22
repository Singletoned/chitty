import unittest
from pathlib import PurePosixPath

from hypothesis import find, given, settings
from hypothesis import strategies as st

from chitty.git import BranchCommit, SquashPlan, squash_plan

DIRS = (PurePosixPath("chitty/tasks"), PurePosixPath("chitty/human"))
names = st.text(alphabet="abc", min_size=1, max_size=3)
paths = st.tuples(
    st.sampled_from(("chitty/tasks", "chitty/human", "chitty/tasksX", "src")), names
).map(lambda pair: PurePosixPath(pair[0]) / (pair[1] + (".py" if pair[0] == "src" else ".md")))
rows = st.lists(
    st.tuples(st.booleans(), st.text(max_size=5), st.lists(paths, max_size=3)), max_size=8
)


def make_commits(rows):
    return [
        BranchCommit(str(i), ("chitty: " if prefix else "impl: ") + subject, tuple(paths))
        for i, (prefix, subject, paths) in enumerate(rows)
    ]


def oracle(commits, prefix_path=False, skip_impl=False, ignore_empty=False):
    keep, squashed = [], []
    for commit in commits:
        if not commit.paths:
            if ignore_empty:
                continue
            return None
        inside = [
            any(str(p).startswith(str(d)) if prefix_path else p.is_relative_to(d) for d in DIRS)
            for p in commit.paths
        ]
        if commit.subject.startswith("chitty: ") and all(inside):
            squashed.append(commit.sha)
        else:
            if any(inside) and not skip_impl:
                return None
            keep.append(commit.sha)
    return SquashPlan(tuple(keep), tuple(squashed)) if len(squashed) >= 2 else None


class TestSquashPlan(unittest.TestCase):
    @given(rows)
    def test_property(self, drawn):
        commits = make_commits(drawn)
        self.assertEqual(squash_plan(commits, DIRS), oracle(commits))

    def test_empty_commit(self):
        p = PurePosixPath("chitty/tasks/a.md")
        commits = [
            BranchCommit("1", "chitty: a", (p,)),
            BranchCommit("2", "chitty: b", (p,)),
            BranchCommit("3", "chitty: c", ()),
        ]
        self.assertIsNone(squash_plan(commits, DIRS))

    def test_mutants(self):
        for option in ("prefix_path", "skip_impl", "ignore_empty"):
            with self.subTest(option=option):
                example = find(
                    rows,
                    lambda drawn, option=option: (
                        oracle(make_commits(drawn)) != oracle(make_commits(drawn), **{option: True})
                    ),
                    settings=settings(max_examples=10000, deadline=None),
                )
                commits = make_commits(example)
                self.assertNotEqual(squash_plan(commits, DIRS), oracle(commits, **{option: True}))
