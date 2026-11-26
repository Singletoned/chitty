import subprocess

from tests.test_cli import CliTestCase


class TestListBlockers(CliTestCase):
    def test_blockers_are_visible_across_list_filters(self):
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        tickets = [
            ("Blocker one", "planning", None),
            ("Dependent two", "todo", None),
            ("Dependent three", "planning", None),
            ("Done four", "done", None),
            ("No dependent five", "planning", None),
            ("Owned six", "doing", "agent"),
            ("Dependent seven", "todo", None),
            ("Backlog eight", "backlog", None),
            ("Blocked nine", "blocked", None),
        ]
        for title, status, owner in tickets:
            command = ["add", title, "-d", "Description."]
            if owner:
                command.extend(("--owner", owner))
            self.run_cli(*command)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "seed list blocker fixture")
        dependencies = {2: [1], 3: [1, 2], 4: [5], 7: [6], 8: [9]}
        for number, (title, status, _) in enumerate(tickets, 1):
            path = self.root / f"chitty/tasks/TASK-{number}--{title.lower().replace(' ', '-')}.md"
            text = path.read_text().replace("status: todo", f"status: {status}")
            if number in dependencies:
                refs = "".join(f"  - TASK-{ref}\n" for ref in dependencies[number])
                text = text.replace("created:", f"depends_on:\n{refs}created:")
            path.write_text(text)
        self.git("add", ".")
        self.git("commit", "--quiet", "-m", "add blocker fixture relationships")

        lines = self.run_cli("list", "--all").stdout.splitlines()
        expected = [
            "TASK-8  💤 bklog  🔗  Backlog eight",
            "TASK-1  📝 plnng  🚧  Blocker one",
            "TASK-3  📝 plnng  🔗  Dependent three",
            "TASK-5  📝 plnng      No dependent five",
            "TASK-2  📋 todo   🔗  Dependent two",
            "TASK-7  📋 todo   🔗  Dependent seven",
            "TASK-6  🔨 doing  👤  Owned six",
            "TASK-9  ⛔ blckd  🚧  Blocked nine",
            "TASK-4  ✅ done       Done four",
        ]
        self.assertEqual(lines, expected)
        for args in (("list", "-s", "planning"), ("list", "--search", "Blocker one")):
            self.assertIn("🚧", self.run_cli(*args).stdout)
        task = next(item for item in self.json("list") if item["id"] == "TASK-1")
        self.assertIsNone(task["skipped"])

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True, text=True)
