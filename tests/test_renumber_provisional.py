import json
import os
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.store import Repo
from tests import examples
from tests.support import CONFIG, RepoTestCase
from tests.test_cli import CliTestCase
from tests.test_source_copy_errors import SourceCopyErrorChecks


def build_provisional_repo(root: Path, provisional: int) -> None:
    (root / "chitty.toml").write_text(CONFIG.replace("autocommit = false", "autocommit = true"))

    def git(*args):
        subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)

    git("init", "-b", "main")
    git("config", "user.name", "Tester")
    git("config", "user.email", "tester@example.com")
    run_cli = CliTestCase().run_cli
    run_cli("add", "Numbered", "-d", "Fixture.")
    git("switch", "-c", "feature")
    for i in range(provisional):
        run_cli("add", f"P{i}", "-d", "Fixture.")
    git("switch", "main")
    git("merge", "feature")


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
        mapping, writable = repo._plan_provisional_renumbering(None)
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
        mapping, writable = repo._plan_provisional_renumbering(None)
        with (
            mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"}),
            mock.patch("chitty.store.datetime") as clock,
        ):
            clock.now.return_value = datetime(2026, 1, 1, tzinfo=UTC)
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


class TestCliProvisionalRenumbering(CliTestCase):
    def git(self, *args):
        import subprocess

        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout

    def fixture(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Tester")
        self.git("config", "user.email", "tester@example.com")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")
        self.git("switch", "-c", "feature")
        self.run_cli("add", "One", "-d", "Fixture.")
        self.run_cli("add", "Two", "-d", "Fixture.")
        self.git("switch", "main")
        self.git("merge", "feature")

    @settings(max_examples=examples(5), deadline=None)
    @given(provisional=st.integers(min_value=0, max_value=3))
    def test_renumber_is_idempotent(self, provisional):
        root = Path(tempfile.mkdtemp(dir=self.tmp))
        previous = Path.cwd()
        try:
            os.chdir(root)
            build_provisional_repo(root, provisional)
            first = self.run_cli("renumber")
            lines = first.stdout.splitlines()
            self.assertEqual(len(lines), provisional)
            self.assertTrue(all(line.startswith("renumbered ") for line in lines))
            head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True)
            before = {p: p.read_bytes() for p in (root / "chitty").rglob("*") if p.is_file()}
            second = self.run_cli("renumber")
            self.assertEqual(second.stderr.strip(), "nothing to renumber")
            self.assertEqual(subprocess.check_output(["git", "rev-parse", "HEAD"], text=True), head)
            self.assertEqual(
                before, {p: p.read_bytes() for p in (root / "chitty").rglob("*") if p.is_file()}
            )
        finally:
            os.chdir(previous)

    def test_mentions_are_skipped_but_do_not_raise_start(self):
        build_provisional_repo(self.root, 1)
        numbered = next((self.root / "chitty/tasks").glob("TASK-1--*.md"))
        numbered.write_text(numbered.read_text().replace("Fixture.", "TASK-9999 and TASK-2."))
        self.git("add", str(numbered))
        self.git("commit", "-m", "Mention unused numbers")
        result = self.run_cli("renumber", "--json")
        self.assertEqual([item["id"] for item in json.loads(result.stdout)], ["TASK-3"])

    def test_branch_containing_main_renumbers_and_commits(self):
        self.fixture()
        self.git("switch", "-c", "fresh")
        before = self.git("rev-parse", "HEAD")
        result = self.run_cli("renumber")
        self.assertEqual(len(result.stdout.splitlines()), 2)
        self.assertNotEqual(before, self.git("rev-parse", "HEAD"))
        self.assertIn("chitty: renumber", self.git("log", "-1", "--format=%s"))
        self.assertEqual(self.git("branch", "--show-current").strip(), "fresh")

    def test_main(self):
        self.fixture()
        old = sorted(p.name.split("--")[0] for p in (self.root / "chitty/tasks").glob("TASK-*.md"))
        result = self.run_cli("renumber")
        lines = result.stdout.splitlines()
        self.assertEqual(len(lines), 2)
        for i, old_id in enumerate(old, 1):
            self.assertRegex(
                lines[i - 1], rf"^renumbered {old_id} -> TASK-{i} /.*TASK-{i}--.*\.md$"
            )
        self.assertEqual(self.run_cli("renumber").stderr.strip(), "nothing to renumber")

    def test_json(self):
        self.fixture()
        old = sorted(p.name.split("--")[0] for p in (self.root / "chitty/tasks").glob("TASK-*.md"))
        result = self.run_cli("renumber", "--json")
        items = json.loads(result.stdout)
        self.assertEqual(len(items), 2)
        self.assertEqual([item["id"] for item in items], ["TASK-1", "TASK-2"])
        self.assertEqual([item["moved_from"] for item in items], old)
        result = self.run_cli("renumber", "--json")
        self.assertEqual(json.loads(result.stdout), [])
        self.assertEqual(result.stderr.strip(), "nothing to renumber")
        self.git("switch", "feature")
        result = self.run_cli("renumber", "--json")
        self.assertEqual(json.loads(result.stdout), [])
        self.assertEqual(result.stderr.strip(), "rebase onto main first; nothing changed")

    def test_outside_git(self):
        for ident, title in [("AAAAAA", "Alpha"), ("BAAAAA", "Beta")]:
            path = self.root / f"chitty/tasks/TASK-{ident}--{title.lower()}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                f"---\ntitle: {title}\nstatus: todo\ncreated: 2026-01-01\n"
                "provisional: true\n---\n\n## Description\n\nFixture.\n"
            )
        result = self.run_cli("renumber")
        self.assertEqual(len(result.stdout.splitlines()), 2)
        self.assertTrue(all(line.startswith("renumbered ") for line in result.stdout.splitlines()))

    def test_outside_git_after_prefix_change(self):
        for _ in range(3):
            self.run_cli("add", "Old", "-d", "Text.")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('prefix = "TASK"', 'prefix = "TK"'))
        provisional = self.root / "chitty/tasks/TK-AAAAAA--alpha.md"
        provisional.write_text(
            "---\ntitle: Alpha\nstatus: todo\ncreated: 2026-01-01\n"
            "provisional: true\n---\n\n## Description\n\nFixture.\n"
        )
        result = self.run_cli("renumber")
        self.assertIn("TK-AAAAAA -> TK-1 ", result.stdout)
        self.assertTrue((provisional.parent / "TK-1--alpha.md").is_file())
        self.assertFalse((self.root / ".git").exists())

    def test_off_main(self):
        self.fixture()
        (self.root / "advance").write_text("advance")
        self.git("add", "advance")
        self.git("commit", "-m", "advance main")
        for args in [("switch", "feature"), ("switch", "--detach")]:
            self.git(*args)
            before = {p: p.read_bytes() for p in (self.root / "chitty").rglob("*.md")}
            status = self.git("status", "--porcelain")
            result = self.run_cli("renumber")
            self.assertEqual(result.stderr.strip(), "rebase onto main first; nothing changed")
            self.assertEqual(
                before, {p: p.read_bytes() for p in (self.root / "chitty").rglob("*.md")}
            )
            self.assertEqual(status, self.git("status", "--porcelain"))

    def test_invalid_config(self):
        self.fixture()
        (self.root / "chitty.toml").write_text("bad = [\n")
        self.assertIn("invalid TOML", self.run_cli("renumber", exit_code=1).stderr)
