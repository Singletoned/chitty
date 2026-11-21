from chitty.errors import ChittyError, ProvisionalOffMain
from chitty.store import Repo
from tests.support import RepoTestCase
from tests.test_provisional_preflight import TestProvisionalPreflight


class TestProvisionalPreflightErrors(RepoTestCase):
    git = TestProvisionalPreflight.git
    init_git = TestProvisionalPreflight.init_git
    commit = TestProvisionalPreflight.commit
    file = TestProvisionalPreflight.file

    def setUp(self):
        super().setUp()
        self.init_git()
        self.file("tasks", "TASK-AAAAAA", provisional=True)
        self.commit()
        config = self.root / "chitty.toml"
        config.write_text(
            "".join(
                line
                for line in config.read_text().splitlines(keepends=True)
                if not line.startswith("chitty_version")
            )
        )
        self.commit()

    def snapshot(self):
        return (
            self.git("rev-parse", "HEAD"),
            (self.root / ".git/index").read_bytes(),
            {p: p.read_bytes() for p in (self.root / "chitty").rglob("*.md")},
            (self.root / "chitty.toml").read_bytes(),
        )

    def check_error(self, expected, *parts):
        before = self.snapshot()
        with self.assertRaises(expected) as caught:
            Repo.open(self.root)._plan_provisional_renumbering()
        for part in parts:
            self.assertIn(str(part), str(caught.exception))
        self.assertEqual(before, self.snapshot())
        return str(caught.exception)

    def test_feature(self):
        self.git("switch", "-c", "feature")
        self.check_error(ProvisionalOffMain, "feature")

    def test_detached(self):
        self.git("checkout", "--detach")
        self.check_error(ProvisionalOffMain, "detached HEAD")

    def test_malformed(self):
        path = self.root / "chitty/tasks/TASK-BAAAAA--bad.md"
        path.write_text("not a ticket")
        self.commit()
        self.assertTrue(self.check_error(ChittyError, path).startswith(str(path)))

    def test_duplicate(self):
        first = self.root / "chitty/tasks/TASK-AAAAAA--example.md"
        second = self.file("tasks/archive", "TASK-AAAAAA", provisional=True)
        self.commit()
        self.check_error(ChittyError, first, second)
