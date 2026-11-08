import hashlib
import json
import os
import subprocess
import tomllib
from datetime import date
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner, Result

from chitty.cli import _complete_context, _complete_task_id, cli
from chitty.config import CHITTY_VERSION
from chitty.store import _add_missing_settings, guide
from tests.support import RepoTestCase

LEGACY_MANAGED_GUIDE = """## Chitty

Tasks live in `chitty/`. Use the `chitty` CLI (or MCP tools); do not hand-edit
task files. `chitty --help` is the full command reference.

On a ticket branch, never edit `chitty.toml` or Chitty's block in `AGENTS.md`, or run `chitty init`.

- Put paths, globs, commands, IDs and code in backticks in titles, descriptions,
  criteria and notes.
- Work on one task per session. Start with `chitty inbox --pull`, then `chitty show <ID>`.
- Backlog tasks need refinement; promote them to `todo` before taking them on.
- Writing or refining tickets? Run `chitty guide plan` first: it says how to write\
 them and cold-read them.
- Use a task's optional `parent` field to group flat task IDs under one goal.
- Unless your own instructions say otherwise, create a branch and worktree at
  `.worktrees/` in the repository root from the main branch for each new ticket; never
  implement in the main checkout. Resume the existing worktree for a `doing`
  ticket. Run the repository's setup command in a new worktree before coding so
  it creates that worktree's environment. Commit the `doing` claim on its
  branch before implementation starts, and use `autocommit = true` or commit
  after every Chitty write so other branches can see task state. Run ticket
  writes from the branch holding its latest committed version; Chitty refuses
  to route a write across branches and tells you where to run it.
- Before writing code, write your approach with `chitty edit <ID> --plan` and
  set `-s doing`. Wait for approval if the human asked for it.
- Tick a criterion only after verifying it: `chitty edit <ID> --check N`
  (numbers are shown by `chitty show`). Re-check every criterion before setting
  `-s review`.
- Record anything surprising with `--note`. When work is ready, set `-s review`.
  Never review a ticket you worked on: review promptly in the ticket's branch
  worktree, rather than at merge-request time. Review every criterion; list
  every failure in one note and `--uncheck` each failed criterion. Pass it with
  `-s done --note "Reviewed: ..."`; fail it with `-s doing --note "reason"`.
  On a pass, merge the branch into the main branch, then remove the branch and its
  worktree. Create new tickets for out-of-scope findings. The third failed
  review sets `blocked` and owner `human` instead; leave it for a person to
  unblock.
- Set `-s done` when every criterion is ticked and the work is verified; write
  `--summary` with the handoff, verification, and follow-ups. Run `chitty fix`
  to apply safe repairs; it fails loudly when a problem remains.
- Before preparing a merge request, run `chitty archive` with no ID to process
  completed tasks in one batch. The default moves them to `archive/`; with
  `archive = "delete"`, Git history retains the record instead.
- End commits for task work with `Task: <ID>` lines using the ticket's own ID
  (for example, `Task: TASK-12`) so `git log --grep <ID>` finds a ticket's
  code. This is a convention; no hook enforces it.
- When a question has a sensible default that is cheap to change later, choose
  it and carry on instead of blocking. Record the choice and why with `--note`
  for the reviewer, and comment the code where the default applies, saying how
  and why it was chosen. Block only when the choice is costly to reverse or
  needs a person.
- When work cannot proceed, set `-s blocked --note "reason"` and move on; do
  not pick up blocked work. If a person must act outside the repo, add a
  `-c human` task and depend on it. Leave `human` tasks in `todo` for people;
  never pick them up or block them.
- Found unrelated work on a ticket's branch? Use plain `chitty add`, which files
  it as `BACKLOG` for the planning session. A person planning should do this from
  the main checkout to get normal numbers. Use `-c human` if a person must act.
  Suggest work for another project without touching its checkout using
  `chitty suggest PROJECT "title" -d "why"`. Don't do it in this session.
"""


class CliTestCase(RepoTestCase):
    def setUp(self):
        super().setUp()
        os.environ["CHITTY_ACTOR"] = "test-agent"
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
            ("0.1.9", "re-run `chitty init`"),
            ("0.1.100", "upgrade chitty"),
            ("1.0rc1", "recorded version cannot be read"),
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
    def test_stale_setup_allows_reads_but_blocks_writes_without_autocommit(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                f'chitty_version = "{CHITTY_VERSION}"', 'chitty_version = "0.0.0"'
            )
        )

        self.run_cli("list")
        result = self.run_cli("add", "Blocked", "-d", "x", exit_code=1)

        self.assertIn("run `chitty init`", result.stderr)

    def test_newer_unknown_config_key_keeps_json_reads_valid(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                f'chitty_version = "{CHITTY_VERSION}"',
                'chitty_version = "99.0.0"\nnew_setting = "supported later"',
            )
        )

        result = self.run_cli("list", "--json")

        self.assertEqual(json.loads(result.stdout), [])
        self.assertIn("new_setting", result.stderr)

    def test_init_refuses_newer_config_without_changing_it(self):
        config = self.root / "chitty.toml"
        original = config.read_text().replace(
            f'chitty_version = "{CHITTY_VERSION}"',
            'chitty_version = "99.0.0"\nnew_setting = "supported later"',
        )
        config.write_text(original)

        result = self.run_cli("init", exit_code=1)

        self.assertIn("needs Chitty 99.0.0 or later", result.stderr)
        self.assertEqual(config.read_text(), original)

    def test_newer_setup_blocks_writes(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace(
                f'chitty_version = "{CHITTY_VERSION}"', 'chitty_version = "99.0.0"'
            )
        )

        result = self.run_cli("add", "Blocked", "-d", "x", exit_code=1)

        self.assertIn("needs Chitty 99.0.0 or later", result.stderr)

    def test_init_writes_main_branch_for_new_non_main_repository(self):
        target = self.tmp / "fresh"
        target.mkdir()
        os.chdir(target)
        with patch("chitty.store.git.current_branch", return_value="master"):
            self.run_cli("init")
        config = (target / "chitty.toml").read_text()
        self.assertIn('main_branch = "master"', config)
        self.assertEqual(config.count("main_branch"), 1)

    def test_init_does_not_add_main_branch_to_existing_config(self):
        config = self.root / "chitty.toml"
        with patch("chitty.store.git.current_branch", return_value="master"):
            self.run_cli("init")
        self.assertNotIn("main_branch", config.read_text())

    def test_init_does_not_write_main_branch_on_main_or_detached_head(self):
        for name, branch in (("main", "main"), ("detached", None)):
            with self.subTest(name=name):
                target = self.tmp / name
                target.mkdir()
                os.chdir(target)
                with patch("chitty.store.git.current_branch", return_value=branch):
                    self.run_cli("init")
                self.assertNotIn("main_branch", (target / "chitty.toml").read_text())

    def test_init_does_not_write_main_branch_outside_git(self):
        target = self.tmp / "outside-git"
        target.mkdir()
        os.chdir(target)

        self.run_cli("init")

        self.assertNotIn("main_branch", (target / "chitty.toml").read_text())

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
            '# setup = "make install" # run in every ticket worktree before the agent starts',
            config,
        )
        self.assertIn(
            '# check = "make check" # validate the ticket worktree before the agent starts',
            config,
        )
        self.assertIn('# agent_command = "pi --no-extensions', config)
        self.assertIn(
            'archive = "move" # or "delete"; retain completed files or delete them', config
        )
        self.assertNotIn("  #", config)
        self.assertIn(f'chitty_version = "{CHITTY_VERSION}"', config)
        self.assertNotIn("main_branch", config)
        self.assertIn("review = true", config)
        self.assertIn('[contexts.human]\nprefix = "HUMAN"\nreview = false', config)
        self.assertTrue((target / "chitty" / "tasks").is_dir())
        agents = (target / "AGENTS.md").read_text()
        self.assertTrue(
            agents.startswith(
                "# Agents\n\nBe nice.\n\n<!-- chitty:begin - managed by `chitty init`; "
                "edits here are replaced -->\n\n## Chitty\n"
            )
        )
        self.assertIn("chitty guide work", agents)
        self.assertIn("chitty guide review", agents)
        self.assertIn("chitty guide plan", agents)
        self.assertIn("Run `chitty --help` for the command reference.", agents)
        result = self.run_cli("init")
        self.assertEqual(result.stdout, "already up to date\n")
        (target / "chitty.toml").unlink()
        self.run_cli("init")
        refreshed_agents = (target / "AGENTS.md").read_text()
        self.assertEqual(refreshed_agents, agents)
        self.assertEqual(self.json("add", "First", "-d", "x")["id"], "TASK-1")

    def test_init_marks_and_migrates_the_managed_guide(self):
        agents = self.root / "AGENTS.md"
        self.run_cli("init")
        marked = agents.read_text()
        self.assertIn(
            "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->\n\n",
            marked,
        )
        self.assertIn("\n\n<!-- chitty:end -->\n", marked)
        self.assertNotIn("chitty:begin", guide())

        agents.write_text("# Before\n\n" + LEGACY_MANAGED_GUIDE + "\n## After\n\nKeep this.\n")
        result = self.run_cli("init")
        migrated = agents.read_text()
        self.assertIn("migrated Chitty guide markers", result.stderr)
        self.assertIn("\n<!-- chitty:end -->\n\n## After\n", migrated)
        self.assertIn("Keep this.\n", migrated)

    def test_init_replaces_only_a_marked_guide(self):
        agents = self.root / "AGENTS.md"
        self.run_cli("init")
        original = agents.read_text()
        agents.write_text("Before\n\n" + original + "\nAfter\n\nUnheaded text\n")
        marked_guide = "A backslash: \\ path\n\n" + guide().rstrip("\n")
        with patch("chitty.store.guide", return_value=marked_guide):
            self.run_cli("init")
            updated = agents.read_text()
            self.assertTrue(updated.startswith("Before\n\n"))
            self.assertTrue(updated.endswith("After\n\nUnheaded text\n"))
            self.assertEqual(updated.count("chitty:begin"), 1)
            self.assertEqual(updated.count("chitty:end"), 1)
            self.assertIn("A backslash: \\ path", updated)
            self.assertEqual(self.run_cli("init").stdout, "already up to date\n")
            self.assertEqual(agents.read_text(), updated)

        prettier = Path(__file__).resolve().parent.parent / "node_modules" / ".bin" / "prettier"
        if not prettier.exists():
            raise AssertionError(f"{prettier} is missing: run `make install`")
        subprocess.run(
            [str(prettier), "--no-config", "--write", str(agents)],
            check=True,
            capture_output=True,
        )
        self.assertEqual(agents.read_text(), updated)

    def test_init_rejects_damaged_guide_markers(self):
        agents = self.root / "AGENTS.md"
        for content in (
            "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->\n",
            "<!-- chitty:end -->\n",
            (
                "<!-- chitty:end -->\n"
                "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->\n"
            ),
            (
                "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->\n"
                "<!-- chitty:end -->\n"
                "<!-- chitty:begin - managed by `chitty init`; edits here are replaced -->\n"
                "<!-- chitty:end -->\n"
            ),
        ):
            agents.write_text(content)
            result = self.run_cli("init", exit_code=1)
            self.assertIn("AGENTS.md", result.stderr)
            self.assertEqual(agents.read_text(), content)

    def test_stale_writes_warn_and_skip_damaged_guide_upgrade(self):
        agents = self.root / "AGENTS.md"
        agents.write_text("<!-- chitty:end -->\n")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(f'chitty_version = "{CHITTY_VERSION}"', 'chitty_version = "0.0.0"')
            .replace("autocommit = false", "autocommit = true")
        )
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        result = self.run_cli("add", "Allowed", "-d", "x")
        self.assertIn("skipping repository setup upgrade", result.stderr)
        self.assertIn(
            "Allowed", (self.root / "chitty" / "tasks" / "TASK-1--allowed.md").read_text()
        )
        self.assertIn('chitty_version = "0.0.0"', config.read_text())

    def test_init_adds_missing_human_review_setting(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace('check = "true"\n', "")
            .replace('agent_command = "pi --chitty-{mode} {id}"\n', "")
        )

        self.run_cli("init")
        settings = tomllib.loads(config.read_text())
        self.assertFalse(settings["contexts"]["human"]["review"])
        self.assertIn('# setup = "make install"', config.read_text())
        self.assertIn('# check = "make check"', config.read_text())
        self.assertIn('# agent_command = "pi --no-extensions', config.read_text())
        self.assertIsNone(settings.get("setup"))
        self.assertIsNone(settings.get("agent_command"))
        self.assertEqual(self.run_cli("init").stdout, "already up to date\n")

    def test_init_replaces_a_tracked_pi_extension(self):
        agent = self.tmp / "pi-agent"
        extension = agent / "extensions" / "chitty.ts"
        extension.parent.mkdir(parents=True)
        previous_source = b"previous Chitty extension"
        extension.write_bytes(previous_source)
        (agent / "chitty-extension.sha256").write_text(
            hashlib.sha256(previous_source).hexdigest() + "\n"
        )
        os.environ["PI_CODING_AGENT_DIR"] = str(agent)

        self.run_cli("init")

        self.assertNotEqual(extension.read_bytes(), previous_source)

    def test_init_keeps_a_newer_pi_extension_and_finishes_setup(self):
        agent = self.tmp / "pi-agent"
        agent.mkdir()
        os.environ["PI_CODING_AGENT_DIR"] = str(agent)
        self.run_cli("init")
        extension = agent / "extensions" / "chitty.ts"
        original = extension.read_bytes()
        (agent / "chitty-extension.sha256").write_text(
            hashlib.sha256(original).hexdigest() + "\n99.0.0\n"
        )

        result = self.run_cli("init")

        self.assertIn(CHITTY_VERSION, result.stderr)
        self.assertIn("99.0.0", result.stderr)
        self.assertEqual(extension.read_bytes(), original)
        self.assertTrue((self.root / "AGENTS.md").exists())

    def test_init_failure_leaves_setup_files_unchanged(self):
        config = self.root / "chitty.toml"
        original_config = config.read_text().replace(
            f'chitty_version = "{CHITTY_VERSION}"', 'chitty_version = "0.0.0"'
        )
        config.write_text(original_config)
        agents = self.root / "AGENTS.md"
        original_agents = "# Existing guide\n"
        agents.write_text(original_agents)
        agent = self.tmp / "pi-agent"
        extension = agent / "extensions" / "chitty.ts"
        extension.parent.mkdir(parents=True)
        extension.write_text("local edits")
        os.environ["PI_CODING_AGENT_DIR"] = str(agent)

        result = self.run_cli("init", exit_code=1)

        self.assertIn(str(extension), result.stderr)
        self.assertEqual(config.read_text(), original_config)
        self.assertEqual(agents.read_text(), original_agents)

    def test_init_refuses_a_linked_worktree_without_changes(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.run_cli("init")
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")
        worktree = self.tmp / "worktree"
        self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
        self.addCleanup(
            subprocess.run,
            ["git", "worktree", "remove", "--force", str(worktree)],
            cwd=self.root,
            check=True,
        )
        config = worktree / "chitty.toml"
        agents = worktree / "AGENTS.md"
        original_config = config.read_bytes()
        original_agents = agents.read_bytes()

        previous = Path.cwd()
        os.chdir(worktree)
        try:
            result = self.run_cli("init", exit_code=1)
        finally:
            os.chdir(previous)

        self.assertIn(str(self.root), result.stderr)
        self.assertEqual(config.read_bytes(), original_config)
        self.assertEqual(agents.read_bytes(), original_agents)

    def test_init_installs_pi_extension_from_subdirectory_and_outside_git(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        agent = self.tmp / "pi-agent"
        extension = agent / "extensions" / "chitty.ts"
        extension.parent.mkdir(parents=True)
        os.environ["PI_CODING_AGENT_DIR"] = str(agent)

        for directory in (self.root / "subdirectory", self.tmp / "outside-git"):
            with self.subTest(directory=directory):
                directory.mkdir()
                previous_extension = directory.name.encode()
                extension.write_bytes(previous_extension)
                (agent / "chitty-extension.sha256").write_text(
                    hashlib.sha256(previous_extension).hexdigest() + "\n"
                )
                previous = Path.cwd()
                os.chdir(directory)
                try:
                    self.run_cli("init")
                finally:
                    os.chdir(previous)
                self.assertNotEqual(extension.read_bytes(), previous_extension)

    def test_init_adds_worktrees_to_gitignore(self):
        target = self.tmp / "worktrees"
        target.mkdir()
        (target / ".gitignore").write_text(".env\n")
        os.chdir(target)

        self.run_cli("init")

        self.assertEqual((target / ".gitignore").read_text(), ".env\n.worktrees/\n")
        self.run_cli("init")
        self.assertEqual((target / ".gitignore").read_text(), ".env\n.worktrees/\n")

    def test_init_autocommit_commits_only_setup_files_and_is_idempotent(self):
        target = self.tmp / "autocommit"
        target.mkdir()
        os.chdir(target)
        subprocess.run(["git", "init", "--quiet"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=target, check=True)
        subprocess.run(["git", "config", "user.name", "Test"], cwd=target, check=True)
        self.run_cli("init", "--autocommit")

        config = tomllib.loads((target / "chitty.toml").read_text())
        self.assertTrue(config["autocommit"])
        committed = subprocess.run(
            ["git", "show", "--name-only", "--format=", "HEAD"],
            cwd=target,
            capture_output=True,
            check=True,
            text=True,
        ).stdout.splitlines()
        self.assertEqual(committed, [".gitignore", "AGENTS.md", "CLAUDE.md", "chitty.toml"])
        self.assertEqual(
            subprocess.run(
                ["git", "log", "-1", "--format=%B"],
                cwd=target,
                capture_output=True,
                check=True,
                text=True,
            ).stdout.strip(),
            "chitty: initialize and enable autocommit",
        )
        self.assertTrue((target / "CLAUDE.md").is_symlink())
        self.assertEqual((target / "CLAUDE.md").readlink(), Path("AGENTS.md"))
        self.assertEqual(self.git_status(target), "")

        commits = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            cwd=target,
            capture_output=True,
            check=True,
            text=True,
        ).stdout
        self.assertEqual(self.run_cli("init", "--autocommit").stdout, "already up to date\n")
        self.assertEqual(
            subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=target,
                capture_output=True,
                check=True,
                text=True,
            ).stdout,
            commits,
        )

    def test_init_autocommit_refuses_a_dirty_working_tree(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "initial")
        config = self.root / "chitty.toml"
        original = config.read_text() + "# user change\n"
        config.write_text(original)

        result = self.run_cli("init", "--autocommit", exit_code=1)

        self.assertIn("working tree is dirty", result.stderr)
        self.assertEqual(config.read_text(), original)
        self.assertFalse((self.root / "AGENTS.md").exists())

    def test_init_autocommit_enables_a_commented_setting(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", "autocommit = false # off")
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "initial")

        self.run_cli("init", "--autocommit")

        self.assertIn("autocommit = true # off", config.read_text())

    def test_init_autocommit_failure_is_loud(self):
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        config = self.root / "chitty.toml"
        original = config.read_text()
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "initial")
        hook = self.root / ".git/hooks/pre-commit"
        hook.write_text("#!/bin/sh\necho nope >&2\nexit 1\n")
        hook.chmod(0o755)

        result = self.run_cli("init", "--autocommit", exit_code=1)

        self.assertIn("autocommit failed", result.stderr)
        self.assertIn("nope", result.stderr)
        self.assertEqual(config.read_text(), original)
        self.assertFalse((self.root / "AGENTS.md").exists())
        self.assertFalse((self.root / "CLAUDE.md").exists())

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, check=True, text=True
        ).stdout

    @staticmethod
    def git_status(directory: Path) -> str:
        return subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=directory,
            capture_output=True,
            check=True,
            text=True,
        ).stdout

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
        self.assertTrue(agents.startswith("<!-- chitty:begin"))
        self.assertTrue(agents.endswith("<!-- chitty:end -->\n"))
        self.assertIn("chitty guide work", agents)
        self.assertIn(f'chitty_version = "{CHITTY_VERSION}"', config.read_text())
        self.assertIn("Put paths, commands, IDs, and code in backticks", agents)

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
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.commit()

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        )
        return result.stdout

    def commit(self):
        self.git("add", "--all")
        self.git("commit", "--quiet", "--allow-empty", "-m", "setup")

    def test_import_rejects_generated_parent_missing_from_source(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-7.1.md").write_text(
            "---\nid: TASK-7.1\ntitle: Orphan subtask\nstatus: To Do\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )

        self.commit()
        with self.assertRaisesRegex(ValueError, "parent TASK-7: no such task"):
            self.run_cli("import", "backlog-md")

        self.assertEqual(list((self.root / "chitty/tasks").glob("*.md")), [])

    def test_import_keeps_source_creation_and_records_the_importing_actor(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )
        self.commit()

        self.run_cli("import", "backlog-md", "--keep-source")

        self.assertRegex(
            self.json("show", "1")["history"],
            r"^- 2026-10-20 → todo\n- [0-9-]{10}T[0-9:]{8}Z test-agent: imported task$",
        )

    def test_import_archives_completed_tasks_when_archive_policy_is_move(self):
        legacy = self.root / "backlog/completed"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Completed\nstatus: Done\n"
            "created_date: '2026-10-20'\n---\n\n## Description\n\nLegacy description.\n"
        )
        self.commit()

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
        self.commit()

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
        self.commit()

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
        self.commit()

        self.run_cli("import", "backlog-md", "--keep-source")

        updated = agents.read_text()
        self.assertNotIn("BACKLOG.MD", updated)
        self.assertNotIn("Backlog.md Workflow", updated)
        self.assertEqual(updated.count("## Chitty"), 1)

    def write_legacy_task(self) -> Path:
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        source = legacy / "task-1.md"
        source.write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )
        return source

    def test_import_refuses_untracked_files(self):
        source = self.write_legacy_task()

        result = self.run_cli("import", "backlog-md", exit_code=1)

        self.assertIn("working tree is dirty", result.stderr)
        self.assertIn("backlog/", result.stderr)
        self.assertTrue(source.exists())
        self.assertFalse((self.root / "chitty").exists())

    def test_import_refuses_modified_files_outside_the_backlog(self):
        source = self.write_legacy_task()
        self.commit()
        (self.root / "chitty.toml").write_text((self.root / "chitty.toml").read_text() + "\n")

        result = self.run_cli("import", "backlog-md", exit_code=1)

        self.assertIn("working tree is dirty", result.stderr)
        self.assertIn("chitty.toml", result.stderr)
        self.assertTrue(source.exists())
        self.assertFalse((self.root / "chitty").exists())

    def test_import_refuses_outside_a_git_repository(self):
        self.write_legacy_task()
        subprocess.run(["rm", "-rf", str(self.root / ".git")], check=True)

        result = self.run_cli("import", "backlog-md", exit_code=1)

        self.assertIn("cannot confirm a clean Git working tree", result.stderr)
        self.assertIn("not a git repository", result.stderr)
        self.assertFalse((self.root / "chitty").exists())

    def test_import_removes_tracked_tasks_but_not_other_files(self):
        source = self.write_legacy_task()
        note = self.root / "backlog/README.md"
        note.write_text("Keep me.\n")
        self.commit()

        self.run_cli("import", "backlog-md")

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
        self.commit()

        result = self.run_cli("import", "backlog-md")

        self.assertIn("1 tasks: Backburner -> backlog", result.stdout)
        self.assertNotIn("unknown status", result.stdout)
        self.assertFalse(config.exists())
        self.assertTrue(docs.exists())
        task = self.json("show", "1")
        self.assertEqual(task["status"], "backlog")

    def test_import_backlog_md_converts_tasks_and_replaces_agent_block(self):
        legacy = self.root / "backlog/tasks"
        legacy.mkdir(parents=True)
        (legacy / "task-1.md").write_text(
            "---\nid: TASK-1\ntitle: Legacy\nstatus: To Do\ncreated_date: '2026-10-20'\n---\n\n"
            "## Description\n\nLegacy description.\n"
        )
        (self.root / "backlog/docs").mkdir()
        (self.root / "AGENTS.md").write_text("## Backlog.md Workflow\n\nOld instructions.\n")
        self.commit()

        result = self.run_cli("import", "backlog-md", "--keep-source")

        self.assertIn("left non-task directory", result.stdout)
        self.assertEqual(self.json("show", "1")["title"], "Legacy")
        self.assertIn("## Chitty", (self.root / "AGENTS.md").read_text())
        self.assertTrue((self.root / "backlog").exists())
        refusal = self.run_cli("import", "backlog-md", exit_code=1)
        self.assertIn("already contains tasks", refusal.stderr)


class TestInbox(CliTestCase):
    def test_inbox_lists_and_pulls_suggestions(self):
        self.run_cli("init")
        self.run_cli("suggest", self.root.name, "Waiting", "-d", "Inbox description")

        listed = self.run_cli("inbox")

        self.assertIn(f"{self.root.name}  {date.today().isoformat()}  Waiting", listed.stdout)
        self.assertIn("chitty inbox --pull", listed.stderr)
        self.assertEqual(self.json("inbox")[0]["title"], "Waiting")
        os.environ["CHITTY_ACTOR"] = "test-agent"
        pulled = self.run_cli("inbox", "--pull")
        self.assertIn("actor test-agent", pulled.stdout)
        self.assertIn("pulled TASK-1", pulled.stdout)
        empty = self.run_cli("inbox")
        self.assertEqual(empty.stdout, "")
        self.assertIn("no suggestions waiting", empty.stderr)

    def test_inbox_without_a_project_name_is_actionable(self):
        self.run_cli("init")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace(f'project = "{self.root.name}"\n', ""))

        result = self.run_cli("inbox", exit_code=1)

        self.assertIn("this repository has no project name", result.stderr)

    def test_pull_only_explains_the_migration(self):
        self.run_cli("init")
        self.run_cli("suggest", self.root.name, "Waiting", "-d", "Inbox description")

        result = self.run_cli("pull", exit_code=2)

        self.assertIn("chitty inbox --pull", result.stderr)
        self.assertIn("chitty init", result.stderr)
        self.assertEqual(self.json("inbox")[0]["title"], "Waiting")


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
        self.assertRegex(
            data["history"],
            rf"^- {date.today().isoformat()}T\d{{2}}:\d{{2}}:\d{{2}}Z test-agent → todo$",
        )
        self.assertIn("## History\n\n", shown)
        self.assertEqual(self.run_cli("path", "1").stdout, f"{path}\n")

    def test_add_note_file_reads_backticks_from_stdin(self):
        result = CliRunner().invoke(
            cli,
            ["add", "Piped note", "-d", "x", "--note-file", "-", "--json"],
            input="Keep `chitty list --all` unchanged.\n",
            catch_exceptions=False,
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(json.loads(result.stdout)["notes"], "Keep `chitty list --all` unchanged.")

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
        self.run_cli(
            "edit",
            "2",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
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

    def test_list_orders_and_displays_priority(self):
        self.run_cli("add", "Unset", "-d", "x")
        self.run_cli("add", "Low", "-d", "x", "-p", "low")
        self.run_cli("add", "High", "-d", "x", "-p", "high")
        self.run_cli("add", "Medium", "-d", "x", "-p", "medium")
        self.run_cli("add", "Doing high", "-d", "x", "-p", "high")
        self.run_cli("edit", "5", "-s", "doing")

        listed = self.run_cli("list")

        self.assertEqual(
            listed.stdout.splitlines(),
            [
                "TASK-3  📋 todo   ⏫  High",
                "TASK-1  📋 todo       Unset",
                "TASK-4  📋 todo   🔼  Medium",
                "TASK-2  📋 todo   🔽  Low",
                "TASK-5  🔨 doing  ⏫  Doing high",
            ],
        )
        tasks = self.json("list")
        self.assertEqual(
            [task["id"] for task in tasks], ["TASK-3", "TASK-1", "TASK-4", "TASK-2", "TASK-5"]
        )
        self.assertEqual(
            [task["priority"] for task in tasks], ["high", None, "medium", "low", "high"]
        )

    def test_list_shows_every_status_glyph(self):
        self.run_cli("add", "Backlog", "-s", "backlog")
        self.run_cli("add", "Todo", "-d", "x")
        self.run_cli("add", "Doing", "-d", "x", "-s", "doing")
        self.run_cli("add", "Blocked", "-d", "x", "-s", "blocked", "--note", "reason")
        self.run_cli("add", "Review", "-d", "x", "-s", "review")
        self.run_cli(
            "add",
            "Done",
            "-d",
            "x",
            "-s",
            "review",
        )
        self.run_cli(
            "edit",
            "6",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )

        listed = self.run_cli("list", "--all").stdout
        for glyph, status in (
            ("💤", "bklog"),
            ("📋", "todo "),
            ("🔨", "doing"),
            ("⛔", "blckd"),
            ("👀", "revw "),
            ("✅", "done "),
        ):
            self.assertIn(f"{glyph} {status}", listed)

    def test_list_shortens_titles_to_the_configured_width(self):
        self.run_cli("add", "A title long enough to need cutting", "-d", "x", "-l", "cli")
        self.run_cli("add", "Short", "-d", "x")
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("format = 1", "format = 1\nlist_width = 40"))

        lines = self.run_cli("list").stdout.splitlines()

        self.assertEqual(
            lines, ["TASK-1  📋 todo   A title long e…  [cli]", "TASK-2  📋 todo   Short"]
        )

    def test_list_width_defaults_to_one_hundred_columns(self):
        title = "word " * 30
        self.run_cli("add", title.strip(), "-d", "x")

        line = self.run_cli("list").stdout.splitlines()[0]

        self.assertEqual(len(line) + 1, 100)  # the status glyph takes two columns
        self.assertTrue(line.endswith("…"))

    def test_list_shows_status_glyphs_and_skip_reasons(self):
        self.run_cli("add", "Backlog", "-s", "backlog")
        self.run_cli("add", "Done", "-d", "x")
        self.run_cli("edit", "2", "-s", "review")
        self.run_cli(
            "edit",
            "2",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
        self.run_cli("add", "Waiting", "-d", "x", "--depends-on", "1")
        self.run_cli("add", "Broken", "-d", "x")
        broken_path = self.root / "chitty/tasks/TASK-4--broken.md"
        broken_path.write_text(
            broken_path.read_text().replace("created:", "depends_on:\n  - TASK-99\ncreated:")
        )
        self.run_cli("add", "Human", "-d", "x", "--owner", "human")
        self.run_cli("add", "Doing", "-d", "x")
        doing_path = self.root / "chitty/tasks/TASK-6--doing.md"
        doing_path.write_text(
            doing_path.read_text().replace("created:", "depends_on:\n  - TASK-99\ncreated:")
        )
        self.run_cli("edit", "6", "-s", "doing")
        self.run_cli("add", "Review", "-d", "x")
        review_path = self.root / "chitty/tasks/TASK-7--review.md"
        review_path.write_text(
            review_path.read_text().replace("created:", "depends_on:\n  - TASK-99\ncreated:")
        )
        self.run_cli("edit", "7", "-s", "review")

        listed = self.run_cli("list", "--all")
        lines = listed.stdout.splitlines()
        self.assertEqual(
            lines,
            [
                "TASK-1  💤 bklog      Backlog",
                "TASK-3  📋 todo   🔒  Waiting",
                "TASK-4  📋 todo   ⚠️  Broken",
                "TASK-5  📋 todo   👤  Human",
                "TASK-6  🔨 doing      Doing",
                "TASK-7  👀 revw       Review",
                "TASK-2  ✅ done       Done",
            ],
        )
        self.assertIn("warning: TASK-4 depends on TASK-99", listed.stderr)
        self.assertEqual(self.json("list", "--all")[1]["skipped"], "🔒 waits on TASK-1")
        self.assertIsNone(self.json("list", "--all")[4]["skipped"])

    def test_list_marks_nonhuman_owned_work_as_skipped(self):
        self.run_cli("add", "Agent todo", "-d", "x", "--owner", "agent")
        self.run_cli("add", "Agent doing", "-d", "x", "--owner", "agent")
        self.run_cli("edit", "2", "-s", "doing")
        self.run_cli("add", "Agent review", "-d", "x", "-s", "review", "--owner", "agent")
        self.run_cli("add", "Ready", "-d", "x")

        lines = self.run_cli("list").stdout.splitlines()
        self.assertEqual(sum("👤  Agent" in line for line in lines), 3)
        self.assertNotIn("agent", self.run_cli("list").stdout)
        self.assertEqual(self.run_cli("next").stdout, "work TASK-4\n")

    def test_list_preserves_context_and_numeric_order_for_priority_ties(self):
        for number in range(1, 11):
            self.run_cli("add", f"Task {number}", "-d", "x")
        self.run_cli("add", "Human task", "-c", "human", "-d", "x")

        expected = [*(f"TASK-{number}" for number in range(1, 11)), "HUMAN-1"]
        self.assertEqual(
            [line.split()[0] for line in self.run_cli("list").stdout.splitlines()], expected
        )
        self.assertEqual([task["id"] for task in self.json("list")], expected)

    def test_list(self):
        self.run_cli("add", "Add search to the task list", "-d", "x", "-l", "search", "-l", "cli")
        self.run_cli("add", "Fix login", "-d", "Broken on Safari")
        for n in range(3, 11):
            self.run_cli("add", f"Task {n}", "-d", "x")
        self.run_cli("edit", "1", "-s", "doing")
        self.run_cli("archive", "10")
        lines = self.run_cli("list").stdout.splitlines()
        self.assertEqual(lines[0], "TASK-2  📋 todo   Fix login")
        self.assertEqual(lines[1], "TASK-3  📋 todo   Task 3")
        self.assertEqual(len(lines), 9)
        self.run_cli("edit", "2", "-s", "review")
        self.run_cli(
            "edit",
            "2",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
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
        os.environ["CHITTY_ACTOR"] = "reviewer"
        refused = self.run_cli("edit", "1", "-s", "doing", exit_code=1)
        self.assertIn("review → doing requires --note", refused.stderr)
        self.run_cli(
            "edit",
            "1",
            "-s",
            "doing",
            "--note",
            "Review found a problem.\n1: fail - unfinished",
        )
        os.environ["CHITTY_ACTOR"] = "test-agent"
        self.run_cli("edit", "1", "-s", "review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.\n1: pass - complete",
        )
        self.assertEqual(self.json("show", "1")["status"], "done")

    def fail_review(self, reason):
        self.run_cli("edit", "1", "-s", "review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        result = self.run_cli("edit", "1", "-s", "doing", "--note", f"{reason}\n1: fail - {reason}")
        os.environ["CHITTY_ACTOR"] = "test-agent"
        return result

    def test_third_failed_review_escalates_to_a_human(self):
        self.run_cli("add", "Bounce", "-d", "x", "--ac", "Reviewable")
        self.fail_review("First.")
        self.fail_review("Second.")
        self.assertEqual(self.json("show", "1")["status"], "doing")
        escalated = self.fail_review("Third.")
        self.assertIn("escalated to human review TASK-1", escalated.stdout)
        task = self.json("show", "1")
        self.assertEqual((task["status"], task["owner"]), ("blocked", "human"))
        notes = task["notes"]
        self.assertIn("Third.", notes)
        self.assertIn("failed review 3 times", notes)
        self.assertTrue(task["history"].endswith("review → blocked"))

    def test_escalation_count_restarts_after_a_human_unblocks(self):
        self.run_cli("add", "Bounce", "-d", "x")
        for reason in ("First.", "Second.", "Third."):
            self.fail_review(reason)
        self.run_cli("edit", "1", "-s", "doing", "--note", "Human: try again.")
        self.fail_review("Fourth.")
        self.assertEqual(self.json("show", "1")["status"], "doing")

    def test_review_verdict_requires_complete_matching_lines(self):
        self.run_cli("add", "Review me", "-d", "x", "--ac", "First", "--ac", "Second")
        self.run_cli("edit", "1", "-s", "review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        before = self.json("show", "1")
        invalid = (
            "Reviewed: ready.",
            "Reviewed: ready.\n1: maybe - no",
            "Reviewed: ready.\n1: pass - one\n1: pass - duplicate\n2: pass - two",
            "Reviewed: ready.\n1: pass - one\n2: pass - two\n3: pass - extra",
            "Reviewed: ready.\n1: fail - one\n2: pass - two",
        )
        for note in invalid:
            refused = self.run_cli("edit", "1", "-s", "done", "--note", note, exit_code=1)
            self.assertTrue(
                "review verdict lines" in refused.stderr
                or "every verdict to be pass" in refused.stderr
            )
            self.assertEqual(self.json("show", "1"), before)
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.\n1: pass - one\n2: pass - two",
        )

    def test_review_verdict_allows_a_failed_review_and_requires_a_failure(self):
        self.run_cli("add", "Review me", "-d", "x", "--ac", "First")
        self.run_cli("edit", "1", "-s", "review")
        os.environ["CHITTY_ACTOR"] = "reviewer"
        refused = self.run_cli(
            "edit", "1", "-s", "doing", "--note", "Review\n1: pass - good", exit_code=1
        )
        self.assertIn("at least one fail verdict", refused.stderr)
        self.assertEqual(self.json("show", "1")["status"], "review")
        self.run_cli("edit", "1", "-s", "doing", "--note", "Review\n1: fail - bad")

    def test_self_review_requires_an_explicit_override_flag(self):
        self.run_cli("add", "Review me", "-d", "x", "--ac", "Reviewable")
        self.run_cli("edit", "1", "-s", "review")

        refused = self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.\n1: pass - ready",
            exit_code=1,
        )

        self.assertIn("test-agent cannot review this task", refused.stderr)
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: emergency approval.\n1: pass - ready",
            "--override-review-independence",
        )
        self.assertIn("overrode review independence", self.json("show", "1")["history"])

    def test_show_reports_the_callers_review_work(self):
        self.run_cli("add", "Review me", "-d", "x")
        self.run_cli("edit", "1", "--plan", "Implement it.")

        shown = self.run_cli("show", "1").stdout

        self.assertIn("worked on: wrote the plan", shown)

    def test_review_can_be_disabled(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("autocommit = false", "autocommit = false\nreview = false")
        )
        self.run_cli("add", "Done directly", "-d", "x")
        self.run_cli("edit", "1", "-s", "done")

    def test_context_review_override_can_disable_the_repository_default(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace('prefix = "HUMAN"', 'prefix = "HUMAN"\nreview = false')
        )

        self.run_cli("add", "Human done directly", "-c", "human", "-d", "x", "-s", "done")
        refused = self.run_cli("add", "Task needs review", "-d", "x", "-s", "done", exit_code=1)

        self.assertIn("requires -s review first", refused.stderr)

    def test_context_review_override_can_require_review(self):
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace("autocommit = false", "autocommit = false\nreview = false")
            .replace('prefix = "HUMAN"', 'prefix = "HUMAN"\nreview = true')
        )

        self.run_cli("add", "Task done directly", "-d", "x", "-s", "done")
        refused = self.run_cli(
            "add", "Human needs review", "-c", "human", "-d", "x", "-s", "done", exit_code=1
        )

        self.assertIn("requires -s review first", refused.stderr)


class TestEdit(CliTestCase):
    def setUp(self):
        super().setUp()
        self.run_cli("add", "Blocker", "-c", "human", "-d", "x")
        self.run_cli("add", "Task", "-d", "Describe.", "--ac", "One", "--ac", "Two", "-l", "a")
        self.path = self.root / "chitty/tasks/TASK-1--task.md"

    def test_edit_everything(self):
        result = self.run_cli(
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
        timestamp = rf"{date.today().isoformat()}T\d{{2}}:\d{{2}}:\d{{2}}Z"
        self.assertRegex(
            data["history"],
            rf"^- {timestamp} test-agent → todo"
            rf"\n- {timestamp} test-agent: changed title, labels, priority, owner, dependencies, "
            rf"description, acceptance criteria, notes; wrote the plan; ticked acceptance criteria"
            rf"\n- {timestamp} test-agent todo → doing$",
        )
        self.assertIn("actor test-agent", result.stdout)
        self.path = self.root / "chitty/tasks/TASK-1--renamed.md"
        self.assertTrue(self.path.exists())
        self.run_cli(
            "edit", "1", "-p", "", "--owner", "", "--plan", "", "--rm-depends-on", "HUMAN-1"
        )
        text = self.path.read_text()
        frontmatter_and_body, _ = text.split("## History", maxsplit=1)
        for gone in ("priority", "owner", "## Plan", "depends_on"):
            self.assertNotIn(gone, frontmatter_and_body)

    def test_edit_appends_repeated_notes_in_order(self):
        self.run_cli("edit", "1", "--note", "First.", "--note", "Second.")

        self.assertEqual(self.json("show", "1")["notes"], "First.\n\nSecond.")

    def test_edit_note_file_reads_backticks_from_stdin(self):
        result = CliRunner().invoke(
            cli,
            ["edit", "1", "--note-file", "-"],
            input="Keep `chitty list --all` unchanged.\n",
            catch_exceptions=False,
        )
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(self.json("show", "1")["notes"], "Keep `chitty list --all` unchanged.")

    def test_edit_note_file_follows_inline_notes(self):
        note_file = self.tmp / "note.md"
        note_file.write_text("From a file.")

        self.run_cli("edit", "1", "--note", "Inline.", "--note-file", str(note_file))

        self.assertEqual(self.json("show", "1")["notes"], "Inline.\n\nFrom a file.")

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


class TestCrossBranchWrites(CliTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "--quiet")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.git("branch", "-M", "main")
        self.commit_seconds = 0
        self.run_cli("add", "Task", "-d", "Describe.")
        self.commit("main task")
        self.path = self.root / "chitty/tasks/TASK-1--task.md"

    def git(self, *args: str, cwd: Path | None = None) -> None:
        subprocess.run(["git", *args], cwd=cwd or self.root, check=True, capture_output=True)

    def commit(self, message: str, cwd: Path | None = None) -> None:
        self.commit_seconds += 1
        environment = {
            **os.environ,
            "GIT_AUTHOR_DATE": f"2026-10-23T00:00:{self.commit_seconds:02}+00:00",
            "GIT_COMMITTER_DATE": f"2026-10-23T00:00:{self.commit_seconds:02}+00:00",
        }
        self.git("add", "--all", cwd=cwd)
        subprocess.run(
            ["git", "commit", "--quiet", "-m", message],
            cwd=cwd or self.root,
            check=True,
            capture_output=True,
            env=environment,
        )

    def claim_on_worker(self, worktree: Path | None = None) -> None:
        root = worktree or self.root
        path = root / "chitty/tasks/TASK-1--task.md"
        path.write_text(path.read_text().replace("status: todo", "status: doing"))
        self.commit("claim task", cwd=worktree)

    def test_refuses_all_single_ticket_writes_from_another_worktree(self):
        worktree = self.tmp / "worker"
        self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        self.claim_on_worker(worktree)
        before = self.path.read_text()

        for args in (
            ("edit", "1", "--note", "Blocked."),
            ("note", "1", "Blocked."),
            ("move", "1", "human"),
            ("archive", "1"),
        ):
            with self.subTest(args=args):
                result = self.run_cli(*args, exit_code=1)
                self.assertIn("worker", result.stderr)
                self.assertIn(str(worktree), result.stderr)
                self.assertEqual(self.path.read_text(), before)
                self.git("reset", "--hard", "HEAD")
                self.git("clean", "-fd")

    def test_refuses_a_branch_without_a_worktree(self):
        self.git("checkout", "--quiet", "-b", "worker")
        self.claim_on_worker()
        self.git("checkout", "--quiet", "main")

        result = self.run_cli("note", "1", "Blocked.", exit_code=1)

        self.assertIn("worker", result.stderr)
        self.assertIn("git switch worker", result.stderr)

    def test_refuses_a_remote_tracking_branch(self):
        remote = self.tmp / "remote.git"
        self.git("init", "--bare", "--quiet", str(remote))
        self.git("remote", "add", "origin", str(remote))
        self.git("checkout", "--quiet", "-b", "worker")
        self.claim_on_worker()
        self.git("push", "--quiet", "origin", "worker")
        self.git("checkout", "--quiet", "main")
        self.git("branch", "-D", "worker")

        result = self.run_cli("note", "1", "Blocked.", exit_code=1)

        self.assertIn("origin/worker", result.stderr)
        self.assertIn("git switch --track origin/worker", result.stderr)

    def test_allows_writes_in_the_branch_with_the_latest_version(self):
        worktree = self.tmp / "worker"
        self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        self.claim_on_worker(worktree)
        previous = Path.cwd()
        os.chdir(worktree)
        try:
            self.run_cli("note", "1", "Continued work.")
        finally:
            os.chdir(previous)

    def test_allows_writes_from_a_new_worktree_with_no_commits_of_its_own(self):
        worktree = self.tmp / "worker"
        self.git("worktree", "add", "--quiet", "-b", "worker", str(worktree))
        self.addCleanup(self.git, "worktree", "remove", "--force", str(worktree))
        previous = Path.cwd()
        os.chdir(worktree)
        try:
            self.run_cli("edit", "1", "-s", "doing")
        finally:
            os.chdir(previous)

        worktree_task = worktree / "chitty/tasks/TASK-1--task.md"
        self.assertIn("status: doing", worktree_task.read_text())
        self.assertIn("status: todo", self.path.read_text())

    def test_allows_writes_when_an_earlier_sorting_branch_holds_the_same_version(self):
        self.git("branch", "aaa")

        self.run_cli("note", "1", "Still on main.")

        self.assertIn("Still on main.", self.path.read_text())


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
        dependent_history = self.json("show", "2")["history"]
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )

        result = self.run_cli("archive", "1")

        self.assertIn("deleted TASK-1", result.stdout)
        self.assertIn("removed dependency reference", result.stdout)
        dependent = self.json("show", "2")
        self.assertEqual(dependent["depends_on"], [])
        self.assertEqual(dependent["history"], dependent_history)

    def test_delete_mode_appends_no_history_to_the_deleted_task(self):
        self.run_cli("add", "Done", "-d", "x")
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text().replace("[contexts.tasks]", 'archive = "delete"\n\n[contexts.tasks]')
        )
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
        history = self.json("show", "1")["history"]

        self.assertEqual(self.json("archive", "1")["history"], history)

    def test_archive_all_done_tasks(self):
        self.run_cli("add", "Task done", "-d", "x")
        self.run_cli("add", "Human done", "-c", "human", "-d", "x")
        self.run_cli("edit", "1", "-s", "review")
        self.run_cli(
            "edit",
            "1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )
        self.run_cli("edit", "HUMAN-1", "-s", "review")
        self.run_cli(
            "edit",
            "HUMAN-1",
            "-s",
            "done",
            "--note",
            "Reviewed: ready.",
            "--override-review-independence",
        )

        result = self.run_cli("archive")

        self.assertEqual(
            result.stdout.splitlines(),
            ["archived TASK-1 actor test-agent", "archived HUMAN-1 actor test-agent"],
        )
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


class TestIdentity(CliTestCase):
    def test_whoami_and_pi_guide_diagnostic(self):
        os.environ["PI_SESSION_ID"] = "session-123"
        name = self.run_cli("whoami").stdout.strip()
        self.assertEqual(self.json("whoami"), {"actor": name})
        os.environ.pop("PI_SESSION_ID")
        os.environ["PI_CODING_AGENT"] = "true"
        self.assertIn("set `CHITTY_ACTOR` when starting Pi", self.run_cli("guide").stdout)

    def test_init_removes_ineffective_pi_session_environment_setting(self):
        settings = self.tmp / "home" / ".pi" / "agent" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text('{\n    "other": [1, 2],\n    "exposeSessionEnvironment": false\n}\n')

        result = self.run_cli("init")

        self.assertIn(f"updated {settings}", result.stdout)
        self.assertEqual(settings.read_text(), '{\n    "other": [1, 2]\n}\n')
        self.assertEqual(self.run_cli("init").stdout, "already up to date\n")


class TestGuide(CliTestCase):
    def test_plan_guide_describes_implementing_cold_reads(self):
        planning_guide = " ".join(guide("plan").split())
        for phrase in (
            "implements it from the ticket alone",
            "with and without the fix",
            "Either way, the reader reports done meaning",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning_guide)

    def test_plan_guide_requires_repeat_reads_and_decision_tests(self):
        planning_guide = " ".join(guide("plan").split())
        for phrase in (
            "until a read finds none",
            "what criteria name",
            "must fail without the fix",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning_guide)

    def test_work_guide_requires_regression_test_failure_and_wrong_ticket_stop(self):
        work_guide = " ".join(guide("work").split())
        for phrase in (
            "see it fail without the fix",
            "change the test until it fails without the fix",
            "do not work around it",
            "a person's decision",
            "An unclear detail with a cheap default is not this",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, work_guide)

    def test_branch_discoveries_are_filed_in_backlog(self):
        for role in ("work", "review"):
            with self.subTest(role=role):
                output = " ".join(guide(role).split())
                self.assertIn("plain `chitty add`", output)
                self.assertIn("`BACKLOG`", output)
                self.assertIn("main checkout", output)

    def test_role_guides_recommend_batching_agent_calls(self):
        required_phrases = ("repeated --check", "in one call", "joined with", "autocommit = true")
        for role in ("work", "review"):
            with self.subTest(role=role):
                output = self.run_cli("guide", role).stdout
                for phrase in required_phrases:
                    self.assertIn(phrase, output)

    def test_guide_points_agents_at_ticket_planning_instructions(self):
        planning_guide = guide("plan")
        self.assertIn("nothing built", planning_guide)
        self.assertIn("must not start one", planning_guide)
        self.assertIn("just before promoting", planning_guide)

    def test_prints_the_agent_guide_outside_any_repo(self):
        os.chdir(self.tmp)
        self.assertEqual(self.run_cli("guide").stdout, guide())

    def test_prints_role_guides_without_a_repository(self):
        os.chdir(self.tmp)
        for role in ("work", "review", "plan"):
            with self.subTest(role=role):
                self.assertEqual(self.run_cli("guide", role).stdout, guide(role))
        for role in ("work", "review"):
            with self.subTest(role=role, ticket=True):
                self.assertEqual(
                    self.run_cli("guide", role, "TASK-42").stdout,
                    f"Work only on Chitty ticket TASK-42.\n\n{guide(role)}",
                )

    def test_rejects_unknown_roles_and_ticket_planning(self):
        unknown = self.run_cli("guide", "writer", exit_code=1)
        self.assertIn(
            "unknown role 'writer'; choose from work, review, plan, cold-read", unknown.stderr
        )
        plan_ticket = self.run_cli("guide", "plan", "TASK-42", exit_code=1)
        self.assertIn("does not take a ticket ID", plan_ticket.stderr)

    def test_role_guides_omit_the_pi_session_diagnostic(self):
        os.environ["PI_CODING_AGENT"] = "true"
        self.assertIn("set `CHITTY_ACTOR` when starting Pi", self.run_cli("guide").stdout)
        for role in ("work", "review", "plan"):
            with self.subTest(role=role):
                self.assertNotIn("set `CHITTY_ACTOR`", self.run_cli("guide", role).stdout)

    def test_help_points_agents_at_it(self):
        self.assertIn("chitty guide", self.run_cli("--help").stdout)
