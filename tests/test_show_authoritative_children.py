import json
from unittest.mock import patch

from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Repo
from tests.test_cli import CliTestCase
from tests.test_source_copy_errors import SourceCopyErrorChecks


class ShowAuthoritativeChildren(CliTestCase):
    git = SourceCopyErrorChecks.git
    init_git = SourceCopyErrorChecks.init_git
    commit = SourceCopyErrorChecks.commit

    def ticket(self, context: str, task_id: str, parent: str = ""):
        path = self.root / "chitty" / context / f"{task_id}--example.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            "---\ntitle: example\nstatus: todo\ncreated: 2026-01-01\n"
            f"{f'parent: {parent}\n' if parent else ''}---\n"
            "\n## Description\n\nFixture.\n"
        )
        return path

    def fixture(self, conflict: bool) -> str:
        self.init_git()
        unreadable = self.ticket("tasks", "TASK-1")
        selected = self.ticket("tasks", "TASK-2")
        self.ticket("tasks", "TASK-10", "TASK-2")
        self.ticket("tasks", "TASK-3", "task-2")
        self.ticket("human", "HUMAN-1", "TASK-2")
        self.commit()
        self.git("switch", "-c", "task-2")
        selected.write_text(selected.read_text().replace("title: example", "title: branch parent"))
        self.commit()
        self.git("switch", "main")
        self.git("switch", "-c", "task-1")
        unreadable.write_text(
            unreadable.read_text().replace("title: example", "title: branch")
            if conflict
            else "not frontmatter\n"
        )
        self.commit()
        self.git("switch", "main")
        if conflict:
            unreadable.write_text(unreadable.read_text().replace("title: example", "title: main"))
            self.commit()
        selected.write_text("not frontmatter\n")
        self.ticket("unconfigured", "MISC-1").write_text("not frontmatter\n")
        repo = Repo.open(self.root)
        self.assertEqual(repo.find(TaskId.parse("TASK-2")).branch, "task-2")
        match = "changed on both" if conflict else "task-1:chitty/tasks/TASK-1--example.md:"
        with self.assertRaises(ChittyError) as failure:
            repo.find(TaskId.parse("TASK-1"))
        self.assertIn(match, str(failure.exception))
        return str(failure.exception)

    def check_show(self, conflict: bool):
        error = self.fixture(conflict)
        original_parse = Repo._parse_source_copy
        original_resolve = Repo._source_files

        def parse(repo, task_id, ref, copies):
            self.assertNotEqual(str(task_id), "MISC-1")
            return original_parse(repo, task_id, ref, copies)

        def resolve(repo, task_id):
            self.assertEqual(str(task_id), "TASK-2")
            return original_resolve(repo, task_id)

        with patch.object(Repo, "_parse_source_copy", parse):
            plain = self.run_cli("show", "TASK-2")
        self.assertIn("title: branch parent", plain.stdout.splitlines())
        self.assertIn("children: TASK-3, TASK-10, HUMAN-1", plain.stdout.splitlines())
        self.assertIn("TASK-1", plain.stderr)
        self.assertIn(error, plain.stderr)
        self.assertIn("incomplete", plain.stderr)
        self.assertNotIn("MISC-1", plain.stderr)
        self.assertNotIn("TASK-2", plain.stderr)

        with patch.object(Repo, "_source_files", resolve):
            output = self.run_cli("show", "TASK-2", "--json")
        data = json.loads(output.stdout)
        self.assertEqual(data["title"], "branch parent")
        self.assertNotIn("children", data)
        self.assertEqual(output.stderr, "")

        for flags in ((), ("--json",)):
            with self.subTest(flags=flags):
                failed = self.run_cli("show", "TASK-1", *flags, exit_code=1)
                self.assertIn(error, failed.stderr)
                self.assertNotIn("incomplete", failed.stderr)

    def test_changed_on_both_candidate(self):
        self.check_show(conflict=True)

    def test_malformed_candidate(self):
        self.check_show(conflict=False)
