from pathlib import Path

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from tests.support import RepoTestCase
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestProvisionalPreflight(RepoTestCase):
    git = SourceCopyErrorChecks.git
    init_git = SourceCopyErrorChecks.init_git
    commit = SourceCopyErrorChecks.commit

    def file(self, location: str, task_id: str, text: str = "Fixture.", *, provisional=False):
        path = self.root / "chitty" / location / f"{task_id}--example.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        flag = "provisional: true\n" if provisional else ""
        path.write_text(
            f"---\ntitle: example\nstatus: todo\ncreated: 2026-01-01\n{flag}---\n"
            f"\n## Description\n\n{text}\n"
        )
        return path

    def base(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text() + "random_ids = true\n")
        self.init_git()
        files = {
            self.file("tasks", "TASK-3"),
            self.file("tasks", "TASK-BAAAAA", provisional=True),
            self.file("tasks/archive", "TASK-AAAAAA", provisional=True),
            self.file("human", "HUMAN-AAAAAA", provisional=True),
        }
        self.file("other/archive", "TASK-CAAAAA", provisional=True)
        self.commit()
        return files

    def snapshot(self):
        return (
            self.git("rev-parse", "HEAD"),
            (self.root / ".git/index").read_bytes(),
            {p: p.read_bytes() for p in (self.root / "chitty").rglob("*.md")},
        )

    def check_plan(self, files: set[Path], first: int):
        before = self.snapshot()
        mapping, writable = Repo.open(self.root)._plan_provisional_renumbering()
        self.assertEqual(
            [(str(old), str(new)) for old, new in mapping.items()],
            [("TASK-AAAAAA", f"TASK-{first}"), ("TASK-BAAAAA", f"TASK-{first + 1}")],
        )
        self.assertCountEqual([t.path for t in writable], files)
        self.assertEqual(self.snapshot(), before)

    def test_base(self):
        self.check_plan(self.base(), 4)

    def test_archive_number(self):
        files = self.base()
        files.add(self.file("tasks/archive", "TASK-4"))
        self.commit()
        self.check_plan(files, 5)

    def test_unconfigured_number(self):
        files = self.base()
        self.file("other", "TASK-4")
        self.commit()
        self.check_plan(files, 5)

    def test_unconfigured_archive_mention(self):
        files = self.base()
        self.file("other/archive", "TASK-CAAAAA", "Mentions TASK-4.", provisional=True)
        self.commit()
        self.check_plan(files, 5)

    def own_branch(self, task_id: str, *, on_disk: bool):
        if on_disk:
            self.file("tasks", task_id)
            self.commit()
        branch = task_id.lower()
        self.git("switch", "-c", branch)
        self.file("tasks", task_id, "Branch version.")
        self.commit()
        self.git("switch", "main")
        self.assertEqual(Repo.open(self.root).find(TaskId.parse(task_id)).branch, branch)

    def test_branch_selected_number(self):
        files = self.base()
        self.own_branch("TASK-4", on_disk=True)
        self.check_plan(files, 5)

    def test_branch_only_number(self):
        files = self.base()
        self.own_branch("TASK-4", on_disk=False)
        self.check_plan(files, 5)

    def test_stale_disk_mention(self):
        files = self.base()
        self.own_branch("TASK-3", on_disk=True)
        files.remove(self.file("tasks", "TASK-3", "Mentions TASK-4."))
        self.check_plan(files, 5)

    def test_deleted_number(self):
        files = self.base()
        config = self.root / "chitty.toml"
        config.write_text('archive = "delete"\n' + config.read_text())
        self.file("tasks", "TASK-4")
        self.commit()
        self.git("rm", "chitty/tasks/TASK-4--example.md")
        self.commit()
        self.check_plan(files, 5)

    def test_conflict(self):
        self.base()
        self.own_branch("TASK-3", on_disk=True)
        self.file("tasks", "TASK-3", "Main version.")
        self.commit()
        repo = Repo.open(self.root)
        pattern = r"TASK-3.*changed on both"
        with self.assertRaisesRegex(ChittyError, pattern):
            repo.source_of(TaskId.parse("TASK-3"))
        before = self.snapshot()
        with self.assertRaisesRegex(ChittyError, pattern):
            repo._plan_provisional_renumbering()
        self.assertEqual(self.snapshot(), before)

    def test_standalone(self):
        self.assertEqual(Repo.open(self.root)._plan_provisional_renumbering(), ({}, ()))
        path = self.file("tasks", "TASK-AAAAAA", provisional=True)
        before = path.read_bytes()
        mapping, writable = Repo.open(self.root)._plan_provisional_renumbering()
        self.assertEqual(mapping, {TaskId.parse("TASK-AAAAAA"): TaskId.parse("TASK-1")})
        self.assertEqual([t.path for t in writable], [path])
        self.assertEqual(path.read_bytes(), before)
