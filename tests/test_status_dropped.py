from chitty.model import STATUSES, parse
from tests.test_cli import CliTestCase


class TestDroppedStatus(CliTestCase):
    def add_ticket(self, title: str):
        self.run_cli("add", title, "-d", "x")
        return next((self.root / "chitty" / "tasks").glob(f"TASK-*--{title.lower()}.md"))

    def test_edit_to_dropped(self):
        path = self.add_ticket("Alpha")
        self.run_cli("edit", "TASK-1", "-s", "dropped")
        self.assertIn("status: dropped\n", path.read_text())

    def test_edit_from_dropped_to_todo(self):
        path = self.add_ticket("Alpha")
        path.write_text(path.read_text().replace("status: todo\n", "status: dropped\n"))
        self.run_cli("edit", "TASK-1", "-s", "todo")
        self.assertIn("status: todo\n", path.read_text())

    def test_list_dropped(self):
        path = self.add_ticket("Alpha")
        path.write_text(path.read_text().replace("status: todo\n", "status: dropped\n"))
        self.assertNotIn("TASK-1", self.run_cli("list").stdout)
        listed = self.run_cli("list", "-s", "dropped").stdout
        self.assertIn("TASK-1", listed)
        self.assertIn("🚫", listed)
        self.assertIn("drop", listed)

    def test_status_round_trip(self):
        path = self.add_ticket("Alpha")
        original = path.read_text()
        for status in ("dropped", *STATUSES):
            with self.subTest(status=status):
                text = original.replace("status: todo\n", f"status: {status}\n")
                self.assertEqual(parse(text).render(), text)

    def test_dropped_dependency_remains_unmet(self):
        first = self.add_ticket("Alpha")
        first.write_text(first.read_text().replace("status: todo\n", "status: dropped\n"))
        second = self.add_ticket("Beta")
        second.write_text(second.read_text().replace("created:", "depends_on: [TASK-1]\ncreated:"))
        self.add_ticket("Gamma")
        self.assertEqual(self.run_cli("next", "--mode", "work").stdout, "work TASK-3\n")
