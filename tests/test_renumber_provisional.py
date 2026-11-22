import os
from unittest import mock

from chitty.store import Repo
from tests.support import RepoTestCase
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestPrepareRenumbering(RepoTestCase):
    git = SourceCopyErrorChecks.git
    init_git = SourceCopyErrorChecks.init_git
    commit = SourceCopyErrorChecks.commit

    def test_prepare(self):
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
