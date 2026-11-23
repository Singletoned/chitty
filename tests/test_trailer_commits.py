import subprocess
import unittest
from pathlib import PurePosixPath

from hypothesis import given
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.git import TRAILER_LOG_OPTIONS, TrailerCommit, parse_trailer_log, trailer_commits
from chitty.ids import TaskId
from tests.support import RepoTestCase

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


class GitTrailerTests(RepoTestCase):
    def git(self, *args, input=None):
        return subprocess.run(
            ["git", *args], cwd=self.root, input=input, capture_output=True, check=True
        ).stdout

    def setUp(self):
        super().setUp()
        self.git("init")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        (self.root / "src").mkdir()
        (self.root / "src/a.py").write_text("a")
        (self.root / "src/b\rc.py").write_text("b")
        self.git("add", "src")
        self.git("commit", "-m", "Add ü", "-m", "Task: TASK-1\nTask: TASK-2")
        first = self.git("rev-parse", "HEAD").decode().strip()
        path = 'chitty/tasks/TASK-1 ü "q".md'
        (self.root / path).parent.mkdir(parents=True)
        (self.root / path).write_text("ticket")
        self.git("add", path)
        self.git("commit", "-m", "Ticket")
        second = self.git("rev-parse", "HEAD").decode().strip()
        self.git("commit", "--allow-empty", "-m", "chitty: edit TASK-1")
        third = self.git("rev-parse", "HEAD").decode().strip()
        self.expected = [
            TrailerCommit(third, "chitty: edit TASK-1", (), ()),
            TrailerCommit(second, "Ticket", (), (PurePosixPath(path),)),
            TrailerCommit(
                first,
                "Add ü",
                (TaskId.parse("TASK-1"), TaskId.parse("TASK-2")),
                (PurePosixPath("src/a.py"), PurePosixPath("src/b\rc.py")),
            ),
        ]

    def test_log(self):
        self.assertEqual(
            self.git("log", "main", *TRAILER_LOG_OPTIONS), render(self.expected, []).encode()
        )
        self.assertEqual(trailer_commits(self.root, "main"), self.expected)

    def test_config(self):
        for key, value in [
            ("log.showSignature", "true"),
            ("i18n.logOutputEncoding", "ISO-8859-1"),
            ("log.showRoot", "false"),
        ]:
            self.git("config", key, value)
        self.assertEqual(trailer_commits(self.root, "main"), self.expected)

    def test_invalid_utf8(self):
        blob = self.git("hash-object", "-w", "--stdin", input=b"data").strip()
        tree = self.git("mktree", input=b"100644 blob " + blob + b"\tbad\xff\n").strip().decode()
        commit = self.git("commit-tree", tree, "-p", "main", "-m", "bad").strip().decode()
        with self.assertRaises(ChittyError):
            trailer_commits(self.root, commit)

    def test_unknown_ref(self):
        with self.assertRaises(ChittyError) as caught:
            trailer_commits(self.root, "nope")
        self.assertIn("git log", str(caught.exception))
        self.assertIn(str(self.root), str(caught.exception))


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
