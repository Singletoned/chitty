import unittest
from pathlib import PurePosixPath

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.git import TrailerCommit, parse_trailer_log
from chitty.ids import TaskId

sha = st.text(alphabet="0123456789abcdef", min_size=40, max_size=40)
subject = st.text(alphabet=st.characters(blacklist_categories=("C",)), max_size=20).filter(
    lambda value: value == value.strip() and value.isprintable() or value == ""
)
part = st.text(
    alphabet=st.characters(blacklist_characters="/\0\x1e", blacklist_categories=("Cs",)),
    min_size=1,
    max_size=10,
).filter(lambda x: x not in (".", ".."))
path = st.one_of(
    st.lists(part, min_size=1, max_size=3).map(lambda parts: PurePosixPath("/".join(parts))),
    st.sampled_from([PurePosixPath("\nleading"), PurePosixPath("a\x1f\r\n é'\"")]),
)
ids = st.tuples(st.sampled_from(["TASK", "HUMAN"]), st.integers(1, 10000)).map(lambda v: TaskId(*v))
commit = st.builds(
    TrailerCommit,
    sha,
    subject,
    st.lists(ids, max_size=3).map(tuple),
    st.lists(path, max_size=3).map(tuple),
)


def render(commits, junk):
    return "".join(
        "\x1e"
        + c.sha
        + "\x1f"
        + c.subject
        + "\x1f"
        + ",".join([*(str(i) for i in c.task_ids), *junk])
        + "\x1f\0"
        + ("\n" + "".join(str(p) + "\0" for p in c.paths) if c.paths else "")
        for c in commits
    )


class TrailerTests(unittest.TestCase):
    @given(
        st.lists(commit, max_size=5),
        st.lists(st.sampled_from(["x", "TASK-", "TASK-1-2", "1"]), max_size=2),
    )
    def test_round_trip(self, commits, junk):
        self.assertEqual(parse_trailer_log(render(commits, junk)), commits)

    @given(sha, subject)
    def test_malformed(self, digest, title):
        c = TrailerCommit(digest, title, (), (PurePosixPath("ab"),))
        text = render([c], [])
        cases = [
            text.replace(title + "\x1f", title + "\x1fX\x1f", 1),
            text.replace("ab\0", "a\x1eb\0"),
            "junk" + text,
            text + "\0",
            text.replace(digest, digest[:-1]),
            text.replace(digest, digest[:-1] + "g"),
            text[:-1],
        ]
        for case in cases:
            with self.assertRaises(ChittyError):
                parse_trailer_log(case)

    @given(st.lists(commit, min_size=1, max_size=5))
    def test_without_z(self, commits):
        with self.assertRaises(ChittyError):
            parse_trailer_log(render(commits, []).replace("\0", "\n"))
