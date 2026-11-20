import unittest
from pathlib import PurePosixPath

from hypothesis import given
from hypothesis import strategies as st

from chitty.run import _has_work

segment = st.text(
    alphabet="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-.é", min_size=1
).filter(lambda value: value not in {".", ".."})
rest = st.lists(segment, min_size=1, max_size=3)
ticket = st.lists(segment, min_size=1, max_size=3).map(
    lambda parts: (PurePosixPath("chitty", *parts), False)
)
work = st.one_of(
    st.sampled_from(["chitty.toml", "chitty", "AGENTS.md"]).map(PurePosixPath),
    rest.map(lambda parts: PurePosixPath("chitty-notes", *parts)),
    rest.map(lambda parts: PurePosixPath("x", "chitty", *parts)),
    rest.map(lambda parts: PurePosixPath("src", *parts)),
).map(lambda path: (path, True))


class TestBranchWorkProperty(unittest.TestCase):
    @given(st.lists(st.one_of(ticket, work), max_size=20))
    def test_has_work(self, entries):
        paths = [path for path, _ in entries]
        expected = any(is_work for _, is_work in entries)
        self.assertEqual(_has_work(paths), expected)
        self.assertEqual(_has_work(list(reversed(paths))), expected)
