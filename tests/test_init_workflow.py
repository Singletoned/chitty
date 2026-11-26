import json
import os
import subprocess
import tomllib
from datetime import date
from pathlib import Path
from unittest import mock

from click.testing import CliRunner
from hypothesis import example, given
from hypothesis import strategies as st

from chitty import config as config_module
from chitty import store as store_module
from chitty.cli import cli
from chitty.config import resolve_workflow
from chitty.errors import ChittyError
from chitty.model import new_task, parse
from chitty.store import add_runner_workflow, init_repo
from tests.support import CONFIG, RepoTestCase

VERSIONS = st.one_of(
    st.sampled_from(("0.4.2", "0.5.0", "0.5.0.0", "0.5.1", "0.6", "0.10.0")),
    st.lists(st.integers(0, 6), min_size=1, max_size=4).map(
        lambda parts: ".".join(map(str, parts))
    ),
    st.text(
        st.characters(max_codepoint=0xFFFF, exclude_characters="\x7f", exclude_categories=("Cs",))
    ),
)
SECTION_LINES = (
    "format = 1",
    'default_context = "tasks"',
    "autocommit = true",
    "review = true",
    "# a comment",
    '# workflow = "tickets"',
    '# chitty_version = "0.1.0"',
    "",
)


@st.composite
def config_cases(draw):
    version = draw(VERSIONS)
    pyproject = draw(st.booleans())
    extras = draw(st.lists(st.sampled_from(SECTION_LINES), unique=True))
    workflow = draw(st.one_of(st.none(), st.sampled_from(("runner", "tickets"))))
    section_lines = extras + [f"chitty_version = {json.dumps(version)}"]
    if workflow is not None:
        section_lines.append(f"workflow = {json.dumps(workflow)}")
    section_lines = draw(st.permutations(section_lines))
    version_index = section_lines.index(f"chitty_version = {json.dumps(version)}")
    if pyproject:
        prefix = '[project]\nname = "x"\nchitty_version = "9.9.9"\n[tool.chitty]\n'
        suffix = (
            '[tool.other]\nworkflow = "tickets"\nchitty_version = "9.9.9"\n'
            if draw(st.booleans())
            else ""
        )
    else:
        prefix = ""
        suffix = '[contexts.tasks]\nprefix = "TASK"\n'
        if draw(st.booleans()):
            suffix += '[agent_commands]\nworkflow = "pi -p {prompt}"\n'
    text = prefix + "\n".join(section_lines) + "\n" + suffix
    return text, version, pyproject, prefix.count("\n") + version_index, workflow


class TestAddRunnerWorkflow(RepoTestCase):
    @example(('chitty_version = "0.4.2"\n', "0.4.2", False, 0, None))
    @example(('chitty_version = "0.5.0"\n', "0.5.0", False, 0, None))
    @example(('chitty_version = "0.5.0.0"\n', "0.5.0.0", False, 0, None))
    @example(('chitty_version = "0.5.1"\n', "0.5.1", False, 0, None))
    @example(('chitty_version = "0.6"\n', "0.6", False, 0, None))
    @example(('chitty_version = "0.10.0"\n', "0.10.0", False, 0, None))
    @given(config_cases())
    def test_section_is_migrated_idempotently(self, case):
        text, version, pyproject, version_index, workflow = case
        should_add = workflow is None and resolve_workflow(None, version) == "runner"
        result = add_runner_workflow(text, version, pyproject)
        if should_add:
            lines = text.splitlines()
            lines.insert(version_index + 1, 'workflow = "runner"')
            self.assertEqual(result.splitlines(), lines)
            data = tomllib.loads(result)
            section = data["tool"]["chitty"] if pyproject else data
            self.assertEqual(section["workflow"], "runner")
        else:
            self.assertEqual(result, text)
        self.assertEqual(add_runner_workflow(result, version, pyproject), result)

    def test_missing_version_cases(self):
        with self.assertRaisesRegex(ChittyError, "chitty_version"):
            add_runner_workflow("format = 1\n", None, False)
        with self.assertRaisesRegex(ChittyError, "chitty_version"):
            add_runner_workflow("format = 1\n", "0.4.2", False)
        self.assertEqual(add_runner_workflow("format = 1\n", "0.6.0", False), "format = 1\n")

    def test_version_at_eof_gets_separating_newline(self):
        text = 'chitty_version = "0.4.2"'
        result = add_runner_workflow(text, "0.4.2", False)
        self.assertEqual(result, text + '\nworkflow = "runner"\n')
        self.assertEqual(tomllib.loads(result)["workflow"], "runner")


class TestSharedPlanningUpgrade(RepoTestCase):
    def setUp(self):
        super().setUp()
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.planning = self.ticket("tasks", "TASK-1--planning.md", "planning", "planner")
        self.todo = self.ticket("human", "HUMAN-1--todo.md", "todo", None)
        self.archived = self.ticket("tasks/archive", "TASK-2--archived.md", "planning", "planner")

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        ).stdout

    def ticket(self, context, name, status, owner):
        path = self.root / "chitty" / context / name
        path.parent.mkdir(parents=True, exist_ok=True)
        task = new_task(
            name, date(2026, 1, 1), "Description", (), {"status": status, "owner": owner}
        )
        path.write_text(task.render())
        return path

    def commit_version(self, version):
        config = self.root / "chitty.toml"
        config.write_text(CONFIG.replace(config_module.CHITTY_VERSION, version))
        self.git("add", ".")
        self.git("commit", "-m", "initial setup")

    def test_old_setup_migrates_active_planning_and_commits_it(self):
        self.commit_version("0.7.1")
        untouched = self.todo.read_bytes(), self.archived.read_bytes()
        written = init_repo(self.root, False, "chitty: upgrade repository setup")
        task = parse(self.planning.read_text())
        self.assertEqual(task.frontmatter.status, "to-plan")
        self.assertIsNone(task.frontmatter.owner)
        self.assertRegex(task.section("History") or "", r"chitty planning → to-plan")
        self.assertEqual((self.todo.read_bytes(), self.archived.read_bytes()), untouched)
        self.assertIn(self.planning, written)
        self.assertIn(
            str(self.planning.relative_to(self.root)), self.git("log", "-1", "--name-only")
        )

    def test_second_upgrade_changes_nothing(self):
        self.commit_version("0.7.1")
        init_repo(self.root, False, "chitty: upgrade repository setup")
        before = self.planning.read_bytes(), self.git("rev-parse", "HEAD")
        self.assertEqual(init_repo(self.root, False, "chitty: upgrade repository setup"), [])
        self.assertEqual((self.planning.read_bytes(), self.git("rev-parse", "HEAD")), before)

    def test_current_version_does_not_migrate(self):
        self.commit_version(config_module.CHITTY_VERSION)
        before = self.planning.read_bytes()
        init_repo(self.root, False, "chitty: upgrade repository setup")
        self.assertEqual(self.planning.read_bytes(), before)


class TestUpgradeWorkflow(RepoTestCase):
    def setUp(self):
        super().setUp()
        text = CONFIG.replace('workflow = "runner"\n', "")
        text = text.replace("autocommit = false", "autocommit = true")
        text = text.replace(
            'chitty_version = "' + config_module.CHITTY_VERSION + '"', 'chitty_version = "0.4.2"'
        )
        (self.root / "chitty.toml").write_text(text)
        self.git("init", "-b", "main")
        self.git("config", "user.name", "Test")
        self.git("config", "user.email", "test@example.com")
        self.git("add", "chitty.toml")
        self.git("commit", "-m", "init")
        self.old_cwd = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, self.old_cwd)
        self.actor = mock.patch.dict(os.environ, {"CHITTY_ACTOR": "tester"})
        self.actor.start()
        self.addCleanup(self.actor.stop)

    def git(self, *args):
        subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)

    def invoke(self, *args):
        with (
            mock.patch.object(store_module, "CHITTY_VERSION", "0.5.1"),
            mock.patch.object(config_module, "CHITTY_VERSION", "0.5.1"),
        ):
            return CliRunner().invoke(cli, list(args), catch_exceptions=False)

    def test_init_migration_is_stable(self):
        self.invoke("init")
        config = self.root / "chitty.toml"
        agents = self.root / "AGENTS.md"
        self.assertIn('workflow = "runner"', config.read_text())
        before = config.read_bytes(), agents.read_bytes()
        self.invoke("init")
        self.assertEqual((config.read_bytes(), agents.read_bytes()), before)
        self.assertIn("chitty guide work", agents.read_text())

    def test_autocommit_upgrade_precedes_add(self):
        self.invoke("add", "First", "--description", "x")
        commit = subprocess.run(
            ["git", "show", "HEAD~1:chitty.toml"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        subject = subprocess.run(
            ["git", "show", "-s", "--format=%s", "HEAD~1"],
            cwd=self.root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        self.assertEqual(subject, "chitty: upgrade repository setup")
        self.assertIn('workflow = "runner"', commit)
