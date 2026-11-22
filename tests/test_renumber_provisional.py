import os
from unittest import mock

from chitty.errors import ChittyError
from chitty.store import Repo
from tests.support import RepoTestCase
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestRenumberOutsideGit(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.old = self.root / "chitty/tasks/TASK-AAAAAA--alpha.md"
        self.old.parent.mkdir(parents=True)
        self.old.write_text(
            "---\ntitle: Alpha\nstatus: todo\ncreated: 2026-01-01\n"
            "provisional: true\n---\n\n## Description\n\nFixture.\n"
        )
        patcher = mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"})
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_without_autocommit(self):
        changes = Repo.open(self.root).renumber_provisional()
        self.assertEqual([str(change.task.id) for change in changes], ["TASK-1"])
        self.assertTrue((self.old.parent / "TASK-1--alpha.md").is_file())
        self.assertFalse(self.old.exists())
        self.assertFalse((self.root / ".git").exists())

    def test_autocommit_requires_git_without_changes(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        before = {
            p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()
        }
        with self.assertRaises(ChittyError) as caught:
            Repo.open(self.root).renumber_provisional()
        self.assertIn("requires", str(caught.exception))
        self.assertIn("to be in a Git work tree", str(caught.exception))
        self.assertEqual(
            before,
            {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()},
        )
        self.assertFalse((self.root / ".git").exists())


class TestPrepareRenumbering(RepoTestCase):
    git = SourceCopyErrorChecks.git
    init_git = SourceCopyErrorChecks.init_git
    commit = SourceCopyErrorChecks.commit

    def fixture(self):
        self.init_git()

        def put(name, title, extra="", body="Fixture."):
            path = self.root / "chitty" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"---\ntitle: {title}\nstatus: todo\ncreated: 2026-01-01\n"
                f"{extra}---\n\n## Description\n\n{body}\n"
            )

        put("tasks/archive/TASK-AAAAAA--alpha.md", "Alpha", "provisional: true\n")
        put("tasks/TASK-BAAAAA--beta.md", "Beta", "provisional: true\ndepends_on: [TASK-AAAAAA]\n")
        put(
            "tasks/TASK-3--after-task-aaaaaa.md",
            "After TASK-AAAAAA",
            "depends_on: [TASK-BAAAAA]\n",
            "TASK-AAAAAA TASK-BAAAAA TASK-4\n\n## History\n\n"
            "- 2026-01-01T00:00:00Z tester: TASK-AAAAAA",
        )
        put("human/HUMAN-1--old-name.md", "Human one")
        self.commit()

    def test_prepare(self):
        self.fixture()
        before = {p: p.read_bytes() for p in (self.root / "chitty").rglob("*") if p.is_file()}
        repo = Repo.open(self.root)
        mapping, writable = repo._plan_provisional_renumbering()
        self.assertEqual(
            {str(k): str(v) for k, v in mapping.items()},
            {"TASK-AAAAAA": "TASK-5", "TASK-BAAAAA": "TASK-6"},
        )
        with mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"}):
            result = repo._prepare_renumbering(mapping, writable)
        self.assertEqual(len(result), 3)
        entries = {str(old.id): (old, task, path) for old, task, path in result}
        self.assertEqual(set(entries), {"TASK-AAAAAA", "TASK-BAAAAA", "TASK-3"})
        for old_id, expected in [
            ("TASK-AAAAAA", "tasks/archive/TASK-5--alpha.md"),
            ("TASK-BAAAAA", "tasks/TASK-6--beta.md"),
            ("TASK-3", "tasks/TASK-3--after-task-5.md"),
        ]:
            old, task, path = entries[old_id]
            self.assertEqual(path, self.root / "chitty" / expected)
            if old_id != "TASK-3":
                self.assertIsNone(task.frontmatter.provisional)
                self.assertEqual(task.frontmatter.moved_from, old_id)
                history = task.section("History") or ""
                self.assertTrue(
                    history.rstrip().splitlines()[-1].endswith(f"renumbered from {old_id}")
                )
        self.assertEqual(entries["TASK-BAAAAA"][1].frontmatter.depends_on, ["TASK-5"])
        old, task, _ = entries["TASK-3"]
        self.assertEqual(task.frontmatter.depends_on, ["TASK-6"])
        self.assertIn("TASK-5 TASK-6 TASK-4", task.section("Description") or "")
        self.assertEqual(task.section("History"), old.task.section("History"))
        self.assertEqual(
            before, {p: p.read_bytes() for p in (self.root / "chitty").rglob("*") if p.is_file()}
        )

    def test_failed_commit_restores_transaction(self):
        self.fixture()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.commit()
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)

        def snapshot():
            files = {p: p.read_bytes() for p in (self.root / "chitty").rglob("*") if p.is_file()}
            return (
                files,
                self.git("rev-parse", "HEAD"),
                self.git("ls-files", "-s"),
                self.git("status", "--porcelain"),
            )

        before = snapshot()
        with (
            mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"}),
            self.assertRaisesRegex(ChittyError, "autocommit failed"),
        ):
            Repo.open(self.root).renumber_provisional()
        self.assertEqual(snapshot(), before)

    def test_transaction(self):
        self.fixture()
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.commit()
        repo = Repo.open(self.root)
        human = self.root / "chitty/human/HUMAN-1--old-name.md"
        human_before = human.read_bytes()
        mapping, writable = repo._plan_provisional_renumbering()
        with mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"}):
            prepared = repo._prepare_renumbering(mapping, writable)
            count = int(self.git("rev-list", "--count", "HEAD"))
            changes = repo.renumber_provisional()
        self.assertEqual({str(c.task.id) for c in changes}, {"TASK-5", "TASK-6"})
        self.assertEqual(int(self.git("rev-list", "--count", "HEAD")), count + 1)
        message = self.git("show", "-s", "--format=%B", "HEAD")
        for task_id in ("TASK-3", "TASK-5", "TASK-6"):
            self.assertIn(f"Task: {task_id}", message)
        names = self.git("show", "--name-status", "--format=", "--no-renames", "HEAD")
        for old, task, path in prepared:
            self.assertFalse(old.path.exists())
            self.assertEqual(path.read_text(), task.render())
            self.assertIn(f"D\t{old.path.relative_to(self.root)}", names)
            self.assertIn(f"A\t{path.relative_to(self.root)}", names)
        self.assertEqual(human.read_bytes(), human_before)
        head = self.git("rev-parse", "HEAD")
        before = {p: p.read_bytes() for p in (self.root / "chitty").rglob("*") if p.is_file()}
        self.assertEqual(repo.renumber_provisional(), ())
        self.assertEqual(self.git("rev-parse", "HEAD"), head)
        self.assertEqual(before, {p: p.read_bytes() for p in before})
