import json
import os
from datetime import date

from click.testing import CliRunner, Result

from chitty.cli import cli
from tests.support import RepoTestCase


class CliTestCase(RepoTestCase):
    def setUp(self):
        super().setUp()
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)

    def run_cli(self, *args: str, exit_code: int = 0) -> Result:
        result = CliRunner().invoke(cli, list(args), catch_exceptions=False)
        self.assertEqual(result.exit_code, exit_code, result.output)
        return result

    def json(self, *args: str):
        return json.loads(self.run_cli(*args, "--json").stdout)


class TestInit(CliTestCase):
    def test_init(self):
        target = self.tmp / "fresh"
        target.mkdir()
        (target / "AGENTS.md").write_text("# Agents\n\nBe nice.\n")
        os.chdir(target)
        self.run_cli("init", "--prefix", "CHIT")
        self.assertIn('prefix = "CHIT"', (target / "chitty.toml").read_text())
        self.assertTrue((target / "chitty" / "tasks").is_dir())
        agents = (target / "AGENTS.md").read_text()
        self.assertTrue(agents.startswith("# Agents\n\nBe nice.\n\n## Chitty\n"))
        result = self.run_cli("init", exit_code=1)
        self.assertIn("already exists", result.stderr)
        (target / "chitty.toml").unlink()
        self.run_cli("init")
        self.assertEqual((target / "AGENTS.md").read_text(), agents)
        self.assertEqual(self.json("add", "First", "-d", "x")["id"], "TASK-1")

    def test_init_rejects_clashing_prefix(self):
        os.chdir(self.tmp)
        result = self.run_cli("init", "--prefix", "HUMAN", exit_code=1)
        self.assertIn("used by more than one context", result.stderr)
        self.assertFalse((self.tmp / "chitty.toml").exists())


class TestAddShowList(CliTestCase):
    def test_add_and_show(self):
        self.run_cli("add", "Rotate password", "-c", "human", "-d", "Prod DB.")
        result = self.run_cli(
            "add",
            "Add search",
            "-d",
            "Search things.",
            "--ac",
            "Matches title",
            "--ac",
            "Case-insensitive",
            "-l",
            "cli",
            "-p",
            "high",
            "--owner",
            "no",
            "--depends-on",
            "HUMAN-1",
        )
        path = self.root / "chitty/tasks/TASK-1--add-search.md"
        self.assertEqual(result.stdout, f"added TASK-1 {path}\n")
        self.assertIn('owner: "no"\n', path.read_text())
        shown = self.run_cli("show", "1").stdout
        self.assertIn("TASK-1\ntitle: Add search\nstatus: todo\nlabels: cli\n", shown)
        self.assertIn("depends_on: HUMAN-1\n", shown)
        self.assertIn(f"created: {date.today().isoformat()}\n", shown)
        self.assertIn(
            "## Acceptance Criteria\n\n1. [ ] Matches title\n2. [ ] Case-insensitive", shown
        )
        data = self.json("show", "TASK-1")
        self.assertEqual(data["owner"], "no")
        self.assertEqual(data["acceptance_criteria"][1]["index"], 2)
        self.assertEqual(self.run_cli("path", "1").stdout, f"{path}\n")

    def test_add_errors(self):
        result = self.run_cli("add", "X", "-d", "x", "--depends-on", "HUMAN-4", exit_code=1)
        self.assertIn("no task HUMAN-4", result.stderr)
        result = self.run_cli("add", "X", "-d", "x", "-c", "nope", exit_code=1)
        self.assertIn("no context 'nope'", result.stderr)
        self.run_cli("add", "X", exit_code=2)

    def test_list(self):
        self.run_cli("add", "Add search to the task list", "-d", "x", "-l", "search", "-l", "cli")
        self.run_cli("add", "Fix login", "-d", "Broken on Safari")
        for n in range(3, 11):
            self.run_cli("add", f"Task {n}", "-d", "x")
        self.run_cli("edit", "1", "-s", "doing")
        self.run_cli("archive", "10")
        lines = self.run_cli("list").stdout.splitlines()
        self.assertEqual(lines[0], "TASK-1  doing   Add search to the task list  [cli,search]")
        self.assertEqual(lines[1], "TASK-2  todo    Fix login")
        self.assertEqual(len(lines), 9)
        self.assertEqual(
            self.run_cli("list", "--archived").stdout, "TASK-10  todo    Task 10  (archived)\n"
        )
        self.assertEqual(len(self.json("list", "--all")), 10)
        self.assertEqual([t["id"] for t in self.json("list", "-s", "doing")], ["TASK-1"])
        self.assertEqual([t["id"] for t in self.json("list", "--search", "SAFARI")], ["TASK-2"])
        self.assertEqual(
            [t["id"] for t in self.json("list", "-l", "cli", "-l", "search")], ["TASK-1"]
        )
        self.assertEqual(self.json("list", "-c", "human"), [])
        self.run_cli("list", "--archived", "--all", exit_code=2)


class TestEdit(CliTestCase):
    def setUp(self):
        super().setUp()
        self.run_cli("add", "Blocker", "-c", "human", "-d", "x")
        self.run_cli("add", "Task", "-d", "Describe.", "--ac", "One", "--ac", "Two", "-l", "a")
        self.path = self.root / "chitty/tasks/TASK-1--task.md"

    def test_edit_everything(self):
        self.run_cli(
            "edit",
            "1",
            "--title",
            "Renamed",
            "-s",
            "doing",
            "--add-label",
            "b",
            "--rm-label",
            "a",
            "-p",
            "low",
            "--owner",
            "claude",
            "--depends-on",
            "HUMAN-1",
            "-d",
            "New description.",
            "--ac",
            "Three",
            "--check",
            "1",
            "--rm-ac",
            "2",
            "--plan",
            "Do it.",
            "--note",
            "Noted.",
        )
        data = self.json("show", "1")
        self.assertEqual(data["title"], "Renamed")
        self.assertEqual(data["labels"], ["b"])
        self.assertEqual(data["priority"], "low")
        self.assertEqual(data["depends_on"], ["HUMAN-1"])
        self.assertEqual(
            [(c["checked"], c["text"]) for c in data["acceptance_criteria"]],
            [(True, "One"), (False, "Three")],
        )
        self.assertEqual((data["plan"], data["notes"]), ("Do it.", "Noted."))
        self.assertTrue(self.path.exists(), "slug is not updated when the title changes")
        self.run_cli(
            "edit", "1", "-p", "", "--owner", "", "--plan", "", "--rm-depends-on", "HUMAN-1"
        )
        text = self.path.read_text()
        for gone in ("priority", "owner", "## Plan", "depends_on"):
            self.assertNotIn(gone, text)

    def test_unchanged_edit_does_not_write(self):
        before = self.path.read_text()
        self.assertEqual(self.run_cli("edit", "1", "-s", "todo").stdout, "unchanged TASK-1\n")
        self.assertEqual(self.path.read_text(), before)

    def test_files(self):
        plan = self.tmp / "plan.md"
        plan.write_text("Step one.\n\nStep two.\n")
        self.run_cli("edit", "1", "--plan-file", str(plan))
        self.assertEqual(self.json("show", "1")["plan"], "Step one.\n\nStep two.")
        result = CliRunner().invoke(cli, ["edit", "1", "--description-file", "-"], input="Piped.\n")
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(self.json("show", "1")["description"], "Piped.")

    def test_errors(self):
        cases = {
            ("edit", "1"): "nothing to change",
            ("edit", "1", "--check", "3"): "there are 2",
            ("edit", "1", "--rm-label", "zzz"): "no label 'zzz'",
            ("edit", "1", "-p", "urgent"): "low, medium, high",
            ("edit", "1", "-d", ""): "'## Description' section is required",
            ("edit", "1", "--plan", "x", "--plan-file", "-"): "not both",
            ("edit", "9", "-s", "done"): "no task TASK-9",
            ("edit", "1", "--depends-on", "TASK-9"): "no task TASK-9",
            ("edit", "1", "--plan", "# Heading"): "'#' headings",
        }
        for args, message in cases.items():
            with self.subTest(args=args):
                result = CliRunner().invoke(cli, list(args), catch_exceptions=False)
                self.assertNotEqual(result.exit_code, 0)
                self.assertIn(message, result.stderr)


class TestCheck(CliTestCase):
    def test_check(self):
        self.run_cli("add", "One", "-d", "x")
        self.assertEqual(self.run_cli("check").stdout, "")
        path = self.root / "chitty/tasks/TASK-1--one.md"
        path.write_text(path.read_text().replace("status: todo", "status: blocked"))
        result = self.run_cli("check", exit_code=1)
        self.assertIn(f"{path}: status:", result.stdout)
        self.assertIn("1 problem(s)", result.stderr)
        result = self.run_cli("check", "--json", str(path), exit_code=1)
        self.assertEqual(json.loads(result.stdout)[0]["path"], str(path))


class TestMoveArchive(CliTestCase):
    def test_move(self):
        self.run_cli("add", "Needs a person", "-d", "x")
        self.run_cli("add", "Blocked", "-d", "x", "--depends-on", "1")
        result = self.run_cli("move", "1", "human")
        moved = self.root / "chitty/human/HUMAN-1--needs-a-person.md"
        blocked = self.root / "chitty/tasks/TASK-2--blocked.md"
        self.assertEqual(result.stdout, f"moved HUMAN-1 {moved}\nrewrote reference in {blocked}\n")
        self.assertEqual(self.json("show", "TASK-2")["depends_on"], ["HUMAN-1"])
        self.assertEqual(self.json("show", "HUMAN-1")["moved_from"], "TASK-1")
        self.assertIn(
            "already in context", self.run_cli("move", "HUMAN-1", "human", exit_code=1).stderr
        )

    def test_archive_restore(self):
        self.run_cli("add", "One", "-d", "x")
        self.assertTrue(self.json("archive", "1")["archived"])
        self.assertEqual(self.json("show", "1")["archived"], True)
        self.assertIn("(archived)", self.run_cli("show", "1").stdout)
        self.run_cli("restore", "1")
        self.assertIn("not archived", self.run_cli("restore", "1", exit_code=1).stderr)


class TestUserContexts(CliTestCase):
    def setUp(self):
        super().setUp()
        self.other = self.tmp / "notes"
        self.other.mkdir()
        os.chdir(self.other)
        self.run_cli("init", "--prefix", "NOTE")
        os.chdir(self.root)
        self.write_user_contexts(f'[contexts.notes]\nrepo = "{self.other}"\n')

    def write_user_contexts(self, text):
        path = self.config_home / "chitty" / "contexts.toml"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def test_add_to_user_context(self):
        data = self.json("add", "Idea", "-d", "x", "-c", "notes")
        self.assertEqual(data["id"], "NOTE-1")
        self.assertTrue((self.other / "chitty/tasks/NOTE-1--idea.md").exists())
        self.assertEqual(self.json("list"), [])
        self.assertIn(
            "no task NOTE-9",
            self.run_cli(
                "add", "X", "-d", "x", "-c", "notes", "--depends-on", "NOTE-9", exit_code=1
            ).stderr,
        )
        self.assertEqual(
            self.json("add", "Y", "-d", "x", "-c", "notes", "--depends-on", "1")["depends_on"],
            ["NOTE-1"],
        )

    def test_works_outside_any_repo(self):
        os.chdir(self.tmp)
        self.assertEqual(self.json("add", "Idea", "-d", "x", "-c", "notes")["id"], "NOTE-1")
        self.assertIn("chitty init", self.run_cli("add", "Idea", "-d", "x", exit_code=1).stderr)

    def test_only_add_accepts_user_contexts(self):
        self.assertIn("no context 'notes'", self.run_cli("list", "-c", "notes", exit_code=1).stderr)

    def test_shadowing_is_an_error(self):
        self.write_user_contexts(f'[contexts.human]\nrepo = "{self.other}"\n')
        result = self.run_cli("add", "X", "-d", "x", "-c", "human", exit_code=1)
        self.assertIn("defined in both", result.stderr)

    def test_unknown_names_both_files(self):
        result = self.run_cli("add", "X", "-d", "x", "-c", "nope", exit_code=1)
        self.assertIn("chitty.toml", result.stderr)
        self.assertIn("contexts.toml", result.stderr)
