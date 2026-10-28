import json
import os
import tomllib
from datetime import date

from click.testing import CliRunner, Result

from chitty.cli import _complete_context, _complete_task_id, cli
from chitty.config import CHITTY_VERSION
from chitty.store import _add_missing_settings, guide
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


class TestSetupVersion(CliTestCase):
    def test_warns_for_missing_older_and_newer_setup_versions(self):
        config = self.root / "chitty.toml"
        original = config.read_text()
        cases = (
            (None, "re-run `chitty init`"),
            ("0.0.0", "re-run `chitty init`"),
            ("99.0.0", "upgrade chitty"),
        )
        line = f'chitty_version = "{CHITTY_VERSION}"\n'
        for recorded, warning in cases:
            with self.subTest(recorded=recorded):
                replacement = "" if recorded is None else f'chitty_version = "{recorded}"\n'
                config.write_text(original.replace(line, replacement))
                result = self.run_cli("list")
                self.assertIn(warning, result.stderr)
        config.write_text(original)
        self.assertNotIn("warning:", self.run_cli("list").stderr)


class TestInit(CliTestCase):
    def test_init(self):
        target = self.tmp / "fresh"
        target.mkdir()
        (target / "AGENTS.md").write_text("# Agents\n\nBe nice.\n")
        os.chdir(target)
        self.run_cli("init")
        config = (target / "chitty.toml").read_text()
        self.assertIn('prefix = "TASK"', config)
        self.assertIn('# autoformat = "taidy format" # run on every written task file', config)
        self.assertIn(
            'archive = "move" # or "delete"; retain completed files or delete them', config
        )
        self.assertNotIn("  #", config)
        self.assertIn(f'chitty_version = "{CHITTY_VERSION}"', config)
        self.assertIn("review = true", config)
        self.assertTrue((target / "chitty" / "tasks").is_dir())
        agents = (target / "AGENTS.md").read_text()
        self.assertTrue(agents.startswith("# Agents\n\nBe nice.\n\n## Chitty\n"))
        self.assertIn("Task: <ID>", agents)
        self.assertIn("Task: TASK-12", agents)
        self.assertIn("git log --grep <ID>", agents)
        self.assertIn("Put paths, globs, commands, IDs and code in backticks", agents)
        result = self.run_cli("init")
        self.assertEqual(result.stdout, "already up to date\n")
        (target / "chitty.toml").unlink()
        self.run_cli("init")
        refreshed_agents = (target / "AGENTS.md").read_text()
        self.assertEqual(refreshed_agents, agents)
        self.assertEqual(self.json("add", "First", "-d", "x")["id"], "TASK-1")

    def test_init_refreshes_guide_after_default_prefix_changes(self):
        target = self.tmp / "fresh"
        target.mkdir()
        os.chdir(target)
        self.run_cli("init")
        config = target / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace('prefix = "TASK"', 'prefix = "CIRCUIT"')
            .replace(f'chitty_version = "{CHITTY_VERSION}"', 'chitty_version = "0.0.0"')
        )

        agents_path = target / "AGENTS.md"
        agents_path.write_text(guide().replace("Task: <ID>", "Task: CIRCUIT-N"))
        self.run_cli("init")

        agents = agents_path.read_text()
        self.assertEqual(agents, guide())
        self.assertIn(f'chitty_version = "{CHITTY_VERSION}"', config.read_text())
        self.assertIn("Put paths, globs, commands, IDs and code in backticks", agents)

    def test_init_leaves_unrelated_pyproject_untouched(self):
        target = self.tmp / "python-project"
        target.mkdir()
        pyproject = target / "pyproject.toml"
        original = "[project]\nname = 'other'\n"
        pyproject.write_text(original)
        os.chdir(target)

        self.run_cli("init")

        self.assertEqual(pyproject.read_text(), original)
        self.assertTrue((target / "chitty.toml").exists())

    def test_init_adds_missing_pyproject_settings_from_parsed_config(self):
        (self.root / "chitty.toml").unlink()
        config = self.root / "pyproject.toml"
        config.write_text(
            "[tool.chitty]\nformat = 1\ndefault_context = 'tasks'\nautocommit = false\n"
            "# archive = 'delete'\n\n[tool.chitty.contexts.tasks]\nprefix = 'TASK'\n"
        )

        self.run_cli("init")

        settings = tomllib.loads(config.read_text())["tool"]["chitty"]
        self.assertEqual(settings["project"], self.root.name)
        self.assertEqual(settings["archive"], "move")
        self.assertTrue(settings["review"])
        self.assertNotIn("  #", config.read_text())

    def test_init_inserts_pyproject_settings_before_later_tables(self):
        (self.root / "chitty.toml").unlink()
        config = self.root / "pyproject.toml"
        config.write_text(
            "[tool.chitty]\nformat = 1\ndefault_context = 'tasks'\nautocommit = false\n"
            "\n[tool.other]\nvalue = true\n\n[tool.chitty.contexts.tasks]\nprefix = 'TASK'\n"
        )

        self.run_cli("init")

        self.assertEqual(
            tomllib.loads(config.read_text())["tool"]["chitty"]["project"], self.root.name
        )
        self.assertTrue((self.root / "chitty/tasks").is_dir())

    def test_init_derives_a_valid_project_name(self):
        target = self.tmp / "My Project._"
        target.mkdir()
        os.chdir(target)

        self.run_cli("init")

        self.assertEqual(
            tomllib.loads((target / "chitty.toml").read_text())["project"], "my-project"
        )

    def test_init_rejects_an_empty_derived_project_name(self):
        target = self.tmp / "..."
        target.mkdir()
        os.chdir(target)

        result = self.run_cli("init", exit_code=1)

        self.assertIn('project = "name"', result.stderr)
        self.assertFalse((target / "chitty.toml").exists())

    def test_init_escapes_added_project_settings(self):
        config = _add_missing_settings("", {}, False, 'name"with\\escape')

        self.assertEqual(tomllib.loads(config)["project"], 'name"with\\escape')

    def test_init_rejects_removed_prefix_option(self):
        result = self.run_cli("init", "--prefix", "HUMAN", exit_code=2)

        self.assertIn("No such option '--prefix'", result.stderr)

    def test_init_preserves_custom_context_prefixes(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace('prefix = "TASK"', 'prefix = "CIRCUIT"')
            .replace(f'chitty_version = "{CHITTY_VERSION}"', 'chitty_version = "0.0.0"')
        )

        self.run_cli("init")

        self.assertIn('prefix = "CIRCUIT"', config.read_text())
        self.assertEqual(self.json("add", "Default", "-d", "x")["id"], "CIRCUIT-1")
        self.assertEqual(self.json("add", "Human", "-c", "human", "-d", "x")["id"], "HUMAN-1")


class TestImport(CliTestCase):
    def test_import_rejects_generated_parent_missing_from_source(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-7.1.md").write_text(
            "---\nid: TASK-7.1\ntitle: Orphan subtask\nstatus: To Do\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )

        with self.assertRaisesRegex(ValueError, "parent TASK-7: no such task"):
            self.run_cli("import", "backlog-md")

        self.assertEqual(list((self.root / "chitty/tasks").glob("*.md")), [])

    def test_import_archives_completed_tasks_when_archive_policy_is_move(self):
        legacy = self.root / "backlog/completed"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Completed\nstatus: Done\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )

        self.run_cli("import", "backlog-md", "--keep-source")

        archived = self.root / "chitty/tasks/archive/TASK-1--completed.md"
        self.assertTrue(archived.exists())
        self.assertIn("done → archived", archived.read_text())
        self.assertEqual(list((self.root / "chitty/tasks").glob("*.md")), [])

    def test_import_omits_archived_tasks_when_archive_policy_is_delete(self):
        (self.root / "chitty.toml").write_text(
            (self.root / "chitty.toml")
            .read_text()
            .replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        legacy = self.root / "backlog/completed"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Completed\nstatus: Done\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )

        self.run_cli("import", "backlog-md", "--keep-source")

        self.assertEqual(list((self.root / "chitty/tasks").glob("*.md")), [])

    def test_import_strips_references_to_deleted_archived_tasks(self):
        (self.root / "chitty.toml").write_text(
            (self.root / "chitty.toml")
            .read_text()
            .replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        tasks = self.root / "backlog/tasks"
        tasks.mkdir(parents=True)
        (tasks / "task-2.md").write_text(
            "---\nid: TASK-2\ntitle: Dependent\nstatus: To Do\n"
            "created_date: '2026-10-20'\ndependencies:\n  - TASK-1\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )
        completed = self.root / "backlog/completed"
        completed.mkdir()
        (completed / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Completed\nstatus: Done\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )

        self.run_cli("import", "backlog-md", "--keep-source")

        self.assertEqual(self.json("show", "2")["depends_on"], [])

    def test_import_removes_a_marker_delimited_backlog_block_after_init(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )
        agents = self.root / "AGENTS.md"
        agents.write_text(
            "# Agents\n\n<!-- BACKLOG.MD GUIDELINES START -->\n<CRITICAL_INSTRUCTION>\n"
            "## Backlog.md Workflow\n\nOld instructions.\n</CRITICAL_INSTRUCTION>\n"
            "<!-- BACKLOG.MD GUIDELINES END -->\n"
        )
        self.run_cli("init")

        self.run_cli("import", "backlog-md", "--keep-source")

        updated = agents.read_text()
        self.assertNotIn("BACKLOG.MD", updated)
        self.assertNotIn("Backlog.md Workflow", updated)
        self.assertEqual(updated.count("## Chitty"), 1)

    def test_import_requires_a_source_policy_for_untracked_files(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        source = legacy / "task-1.md"
        source.write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )

        result = self.run_cli("import", "backlog-md", exit_code=1)

        self.assertIn(str(source), result.stderr)
        self.assertIn("--remove-source", result.stderr)
        self.assertIn("--keep-source", result.stderr)
        self.assertTrue(source.exists())
        self.assertFalse(list((self.root / "chitty/tasks").glob("*.md")))

    def test_import_remove_source_deletes_untracked_tasks_but_not_other_files(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        source = legacy / "task-1.md"
        source.write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )
        note = self.root / "backlog/README.md"
        note.write_text("Keep me.\n")

        self.run_cli("import", "backlog-md", "--remove-source")

        self.assertFalse(source.exists())
        self.assertTrue(note.exists())

    def test_import_removes_config_and_summarizes_declared_statuses(self):
        legacy = self.root / "backlog"
        tasks = legacy / "tasks"
        tasks.mkdir(parents=True)
        (tasks / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: Backburner\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )
        config = legacy / "config.yml"
        config.write_text("statuses:\n  - Backburner\n")
        docs = legacy / "docs"
        docs.mkdir()

        result = self.run_cli("import", "backlog-md", "--remove-source")

        self.assertIn("1 tasks: Backburner -> backlog", result.stdout)
        self.assertNotIn("unknown status", result.stdout)
        self.assertFalse(config.exists())
        self.assertTrue(docs.exists())
        task = self.json("show", "1")
        self.assertEqual(task["status"], "backlog")

    def test_import_rejects_conflicting_source_policies(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )

        result = self.run_cli(
            "import", "backlog-md", "--remove-source", "--keep-source", exit_code=1
        )

        self.assertIn("cannot be used together", result.stderr)

    def test_import_backlog_md_converts_tasks_and_replaces_agent_block(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )
        (self.root / "backlog/docs").mkdir()
        (self.root / "AGENTS.md").write_text("## Backlog.md Workflow\n\nOld instructions.\n")

        result = self.run_cli("import", "backlog-md", "--keep-source")

        self.assertIn("left non-task directory", result.stdout)
        self.assertEqual(self.json("show", "1")["title"], "Legacy")
        self.assertIn("## Chitty", (self.root / "AGENTS.md").read_text())
        self.assertTrue((self.root / "backlog").exists())
        refusal = self.run_cli("import", "backlog-md", exit_code=1)
        self.assertIn("already contains tasks", refusal.stderr)


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
        self.assertEqual(data["history"], f"- {date.today().isoformat()} → todo")
        self.assertIn("## History\n\n", shown)
        self.assertEqual(self.run_cli("path", "1").stdout, f"{path}\n")

    def test_add_backlog_uses_a_default_description(self):
        self.run_cli("add", "Explore sync", "-s", "backlog")

        task = self.json("show", "1")
        self.assertEqual(task["status"], "backlog")
        self.assertEqual(task["description"], "This ticket needs refining.")
        self.run_cli("add", "Needs detail", "-s", "todo", exit_code=2)

    def test_add_errors(self):
        result = self.run_cli("add", "X", "-d", "x", "--depends-on", "HUMAN-4", exit_code=1)
        self.assertIn("no task HUMAN-4", result.stderr)
        result = self.run_cli("add", "X", "-d", "x", "-c", "nope", exit_code=1)
        self.assertIn("no context 'nope'", result.stderr)
        self.run_cli("add", "X", exit_code=2)

    def test_dynamic_completion_lists_contexts_and_active_ids_first(self):
        self.run_cli("add", "Task", "-d", "x")
        self.run_cli("add", "Human", "-c", "human", "-d", "x")
        self.run_cli("archive", "HUMAN-1")

        self.assertEqual(
            [item.value for item in _complete_context(None, None, "")], ["tasks", "human"]
        )
        self.assertEqual(
            [item.value for item in _complete_task_id(None, None, "")], ["TASK-1", "HUMAN-1"]
        )

    def test_dynamic_completion_outside_a_repo_is_silent(self):
        previous = os.getcwd()
        os.chdir(self.tmp)
        self.addCleanup(os.chdir, previous)

        self.assertEqual(_complete_context(None, None, ""), [])
        self.assertEqual(_complete_task_id(None, None, ""), [])

    def test_list_defaults_to_active_tasks_in_all_contexts(self):
        self.run_cli("add", "Backlog", "-s", "backlog")
        self.run_cli("add", "Done", "-d", "x")
        self.run_cli("edit", "2", "-s", "review")
        self.run_cli("edit", "2", "-s", "done")
        self.run_cli("add", "Human todo", "-c", "human", "-d", "x")
        self.run_cli("add", "Human doing", "-c", "human", "-d", "x")
        self.run_cli("edit", "HUMAN-2", "-s", "doing")

        self.assertEqual([task["id"] for task in self.json("list")], ["HUMAN-1", "HUMAN-2"])
        self.assertEqual([task["id"] for task in self.json("list", "-s", "backlog")], ["TASK-1"])
        self.assertEqual([task["id"] for task in self.json("list", "-s", "done")], ["TASK-2"])
        self.assertEqual(
            [task["id"] for task in self.json("list", "-c", "human", "-c", "tasks")],
            ["HUMAN-1", "HUMAN-2"],
        )

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
        self.run_cli("edit", "2", "-s", "review")
        self.run_cli("edit", "2", "-s", "done")
        self.assertEqual(len(self.json("list", "--all")), 9)
        self.run_cli("list", "--archived", exit_code=2)
        self.assertEqual([t["id"] for t in self.json("list", "-s", "doing")], ["TASK-1"])
        self.assertEqual(
            [t["id"] for t in self.json("list", "--search", "SAFARI", "-s", "done")], ["TASK-2"]
        )
        self.assertEqual(
            [t["id"] for t in self.json("list", "-l", "cli", "-l", "search")], ["TASK-1"]
        )
        empty = self.run_cli("list", "-c", "human")
        self.assertEqual(empty.stdout, "")
        self.assertIn("no tasks: contexts=human; statuses=todo,doing,blocked,review", empty.stderr)
        self.assertEqual(self.json("list", "-c", "human"), [])
        help_text = self.run_cli("list", "--help").stdout
        self.assertNotIn("--archived", help_text)
        self.assertIn("Every status (never archived tasks).", help_text)
        self.assertIn("todo, doing, blocked, and review", help_text)

    def test_parent_groups_tasks(self):
        self.run_cli("add", "Parent", "-d", "x")
        self.run_cli("add", "Child", "-d", "x", "--parent", "1")

        self.assertEqual(self.json("show", "2")["parent"], "TASK-1")
        self.assertIn("TASK-2", self.run_cli("show", "1").stdout)
        self.assertEqual(
            [task["id"] for task in self.json("list", "--parent", "1", "--all")], ["TASK-2"]
        )


class TestBlockedStatus(CliTestCase):
    def test_blocked_requires_note_and_is_listed_by_default(self):
        self.run_cli("add", "Wait", "-d", "x")
        failed = self.run_cli("edit", "1", "-s", "blocked", exit_code=1)
        self.assertIn("requires --note", failed.stderr)
        self.run_cli("edit", "1", "-s", "blocked", "--note", "Need a decision.")
        self.assertEqual(self.json("list")[0]["status"], "blocked")


class TestReviewStatus(CliTestCase):
    def test_review_is_listed_and_required_before_done_by_default(self):
        refused = self.run_cli("add", "Done immediately", "-d", "x", "-s", "done", exit_code=1)
        self.assertIn("requires -s review first", refused.stderr)
        self.run_cli("add", "Review me", "-d", "x", "--ac", "Unfinished")
        refused = self.run_cli("edit", "1", "-s", "done", exit_code=1)
        self.assertIn("requires -s review first", refused.stderr)
        self.run_cli("edit", "1", "-s", "review")
        self.assertEqual([task["id"] for task in self.json("list")], ["TASK-1"])
        self.assertEqual(self.json("list")[0]["status"], "review")
        self.assertFalse(self.json("show", "1")["acceptance_criteria"][0]["checked"])
        refused = self.run_cli("edit", "1", "-s", "doing", exit_code=1)
        self.assertIn("review → doing requires --note", refused.stderr)
        self.run_cli("edit", "1", "-s", "doing", "--note", "Review found a problem.")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli("edit", "1", "-s", "done", "--note", "Reviewed: ready.")
        self.assertEqual(self.json("show", "1")["status"], "done")

    def test_review_can_be_disabled(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", "autocommit = false\nreview = false")
        )
        self.run_cli("add", "Done directly", "-d", "x")
        self.run_cli("edit", "1", "-s", "done")


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
        self.assertEqual(
            data["history"],
            f"- {date.today().isoformat()} → todo\n- {date.today().isoformat()} todo → doing",
        )
        self.path = self.root / "chitty/tasks/TASK-1--renamed.md"
        self.assertTrue(self.path.exists())
        self.run_cli(
            "edit", "1", "-p", "", "--owner", "", "--plan", "", "--rm-depends-on", "HUMAN-1"
        )
        text = self.path.read_text()
        for gone in ("priority", "owner", "## Plan", "depends_on"):
            self.assertNotIn(gone, text)

    def test_edit_appends_repeated_notes_in_order(self):
        self.run_cli("edit", "1", "--note", "First.", "--note", "Second.")

        self.assertEqual(self.json("show", "1")["notes"], "First.\n\nSecond.")

    def test_note_appends_a_note(self):
        self.run_cli("note", "1", "Started work.")

        self.assertEqual(self.json("show", "1")["notes"], "Started work.")

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
        path.write_text(path.read_text().replace("status: todo", "status: unknown"))
        result = self.run_cli("check", exit_code=1)
        self.assertIn(f"{path}: status:", result.stdout)
        self.assertIn("1 problem(s)", result.stderr)
        result = self.run_cli("check", "--json", str(path), exit_code=1)
        self.assertEqual(json.loads(result.stdout)[0]["path"], str(path))
        path.write_text(path.read_text().replace("status: unknown", "status: todo"))
        path.write_text(path.read_text().replace("## History", "## History\n\nnot a history line"))
        result = self.run_cli("check", exit_code=1)
        self.assertIn("History' may only contain", result.stdout)

    def test_warning_does_not_fail_check(self):
        self.run_cli("add", "Glob", "-d", "static/photos/*.jpg")

        result = self.run_cli("check")

        self.assertIn("warning:", result.stdout)
        warning = json.loads(self.run_cli("check", "--json").stdout)[0]
        self.assertEqual(warning["severity"], "warning")


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

    def test_delete_mode_removes_dependency_references(self):
        self.run_cli("add", "Done", "-d", "x")
        self.run_cli("add", "Dependent", "-d", "x", "--depends-on", "1")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli("edit", "1", "-s", "done")

        result = self.run_cli("archive", "1")

        self.assertIn("deleted TASK-1", result.stdout)
        self.assertIn("removed dependency reference", result.stdout)
        self.assertEqual(self.json("show", "2")["depends_on"], [])

    def test_archive_all_done_tasks(self):
        self.run_cli("add", "Task done", "-d", "x")
        self.run_cli("add", "Human done", "-c", "human", "-d", "x")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli("edit", "1", "-s", "done")
        self.run_cli("edit", "HUMAN-1", "-s", "review")
        self.run_cli("edit", "HUMAN-1", "-s", "done")

        result = self.run_cli("archive")

        self.assertEqual(result.stdout.splitlines(), ["archived TASK-1", "archived HUMAN-1"])
        self.assertEqual([task["id"] for task in self.json("archive")], [])
        self.assertTrue(self.json("show", "1")["archived"])
        self.assertTrue(self.json("show", "HUMAN-1")["archived"])

    def test_archive_restore(self):
        self.run_cli("add", "One", "-d", "x")
        self.assertTrue(self.json("archive", "1")["archived"])
        self.assertEqual(self.json("show", "1")["archived"], True)
        self.assertIn("(archived)", self.run_cli("show", "1").stdout)
        self.assertNotIn("restore", self.run_cli("--help").stdout)
        self.run_cli("add", "Two", "-d", "x")
        self.assertEqual(self.json("show", "2")["id"], "TASK-2")


class TestIgnoredUserContexts(CliTestCase):
    def test_contexts_file_warns_and_cannot_target_another_repo(self):
        path = self.config_home / "chitty" / "contexts.toml"
        path.parent.mkdir(parents=True)
        path.write_text("[contexts.notes]\nrepo = '/tmp/notes'\n")
        result = self.run_cli("add", "Idea", "-d", "x", "-c", "notes", exit_code=1)
        self.assertIn("contexts.toml is ignored", result.stderr)
        self.assertIn("no context 'notes'", result.stderr)


class TestGuide(CliTestCase):
    def test_prints_the_agent_guide_outside_any_repo(self):
        os.chdir(self.tmp)
        self.assertEqual(self.run_cli("guide").stdout, guide())

    def test_help_points_agents_at_it(self):
        self.assertIn("chitty guide", self.run_cli("--help").stdout)
