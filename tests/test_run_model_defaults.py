import os
import stat
import subprocess
import sys
import tomllib

from chitty.config import INITIAL_CONFIG
from chitty.errors import ChittyError
from chitty.run import _model_arguments
from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestRunModelDefaults(CliTestCase):
    def add(self, title, *, status="todo"):
        return self.json("add", title, "-d", "Description.", "-s", status)["id"]

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, capture_output=True, text=True, check=True
        ).stdout

    def setUp(self):
        super().setUp()
        config = self.root / "chitty.toml"
        config.write_text(
            config.read_text()
            .replace(
                'agent_command = "pi --chitty-{mode} {id}"',
                'agent_command = "fake-agent default {mode} {id}"\n'
                'work_model = "work-model"\nreview_model = "review-model"\n'
                'rebase_model = "rebase-model"\n\n'
                '[agent_commands]\nchosen = "fake-agent chosen {mode} {id}"\n'
                'pinned = "fake-agent pinned {mode} {id} --model pinned-model"',
            )
            .replace("autocommit = false", 'autocommit = true\nsetup = "true"')
        )
        self.git("init", "--quiet")
        self.git("branch", "-M", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        fake = self.root / "bin" / "fake-agent"
        fake.parent.mkdir()
        fake.write_text(
            "#!" + sys.executable + "\n"
            "import subprocess, sys\n"
            "from pathlib import Path\n"
            "Path('invocation').write_text(' '.join(sys.argv[1:]))\n"
            "id = next(arg for arg in sys.argv if arg.startswith('TASK-'))\n"
            "path = next(Path('chitty/tasks').glob(f'{id}--*.md'))\n"
            "text = path.read_text().replace('status: doing', 'status: blocked')"
            ".replace('status: review', 'status: blocked')\n"
            "path.write_text(text)\n"
            "subprocess.run(['git', 'add', str(path)], check=True)\n"
            "subprocess.run(['git', 'commit', '--quiet', '-m', 'agent'], check=True)\n"
        )
        fake.chmod(fake.stat().st_mode | stat.S_IXUSR)
        old_path = os.environ.get("PATH", "")
        os.environ["PATH"] = f"{fake.parent}:{old_path}"
        self.addCleanup(os.environ.__setitem__, "PATH", old_path)
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", "setup")

    def run_ticket(self, *, status="todo", agent=None, arguments=(), unqualified=False):
        ticket = self.add("Model ticket", status=status)
        if status == "review":
            self.git(
                "worktree",
                "add",
                "--quiet",
                "-b",
                f"task-{ticket.split('-')[1]}",
                str(self.root / f".worktrees/task-{ticket.split('-')[1]}"),
            )
        command = ["run"] if unqualified else ["run", "--ticket", ticket]
        if agent:
            command.extend(["--agent", agent])
        if arguments:
            command.extend(["--", *arguments])
        self.run_cli(*command)
        return (self.root / f".worktrees/task-{ticket.split('-')[1]}/invocation").read_text()

    def test_unqualified_work_and_review_select_independent_models(self):
        self.assertEqual(
            self.run_ticket(unqualified=True), "default work TASK-1 --model work-model"
        )
        self.assertEqual(
            self.run_ticket(status="review", agent="chosen", unqualified=True),
            "chosen review TASK-2 --model review-model",
        )

    def test_forwarded_and_command_models_suppress_defaults(self):
        self.assertEqual(
            self.run_ticket(agent="chosen", arguments=("--model", "manual")),
            "chosen work TASK-1 --model manual",
        )
        self.assertEqual(
            self.run_ticket(arguments=("--model=other",)),
            "default work TASK-2 --model=other",
        )
        self.assertEqual(
            self.run_ticket(agent="pinned"),
            "pinned work TASK-3 --model pinned-model",
        )
        self.assertEqual(
            self.run_ticket(agent="pinned", arguments=("--model", "manual")),
            "pinned work TASK-4 --model pinned-model --model manual",
        )

    def test_unset_defaults_leave_agent_arguments_unchanged(self):
        config = self.root / "chitty.toml"
        config.write_text(
            "\n".join(
                line
                for line in config.read_text().splitlines()
                if not line.startswith(("work_model =", "review_model ="))
            )
            + "\n"
        )
        self.git("add", "chitty.toml")
        self.git("commit", "--quiet", "-m", "no model defaults")
        self.assertEqual(self.run_ticket(), "default work TASK-1")

    def test_initial_template_places_models_before_tables(self):
        self.assertLess(
            INITIAL_CONFIG.index("# work_model ="), INITIAL_CONFIG.index("[contexts.tasks]")
        )
        self.assertLess(
            INITIAL_CONFIG.index("# review_model ="), INITIAL_CONFIG.index("[contexts.tasks]")
        )
        self.assertLess(
            INITIAL_CONFIG.index("# review_model ="), INITIAL_CONFIG.index("# rebase_model =")
        )

    def test_pyproject_models_and_init_comments_use_chitty_table(self):
        (self.root / "chitty.toml").unlink()
        config = self.root / "pyproject.toml"
        config.write_text(
            "[tool.chitty]\nformat = 1\ndefault_context = 'tasks'\n"
            "autocommit = true\nsetup = 'true'\nreview = true\n"
            "\n[tool.other]\nwork_model = 'not-chitty'\nvalue = true\n"
            "\n[tool.chitty.contexts.tasks]\nprefix = 'TASK'\n"
        )
        self.run_cli("init")
        text = config.read_text()
        self.assertEqual(
            text.splitlines()[
                text.splitlines().index(
                    '# review_model = "provider/model" # default for review sessions'
                )
                + 1
            ],
            '# rebase_model = "provider/model" # default for rebase sessions',
        )
        self.run_cli("init")
        self.assertEqual(config.read_text().count("# rebase_model ="), 1)
        self.assertLess(text.index("[tool.chitty]"), text.index("# work_model ="))
        self.assertLess(text.index("# review_model ="), text.index("[tool.other]"))
        config.write_text(
            text.replace("# work_model =", "work_model =").replace(
                "# review_model =", "review_model ="
            )
        )
        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["tool"]["chitty"]["work_model"], "provider/model")
        self.assertEqual(Repo.open(self.root).config.review_model, "provider/model")

    def test_init_does_not_find_review_model_in_another_pyproject_table(self):
        (self.root / "chitty.toml").unlink()
        config = self.root / "pyproject.toml"
        config.write_text(
            "[tool.chitty]\nformat = 1\ndefault_context = 'tasks'\n"
            "autocommit = true\nsetup = 'true'\nreview = true\n"
            "# review_model = 'provider/model'\n\n"
            "[tool.other]\nreview_model = 'other/model'\nvalue = true\n\n"
            "[tool.chitty.contexts.tasks]\nprefix = 'TASK'\n"
        )

        self.run_cli("init")

        parsed = tomllib.loads(config.read_text())
        self.assertEqual(parsed["tool"]["other"]["review_model"], "other/model")
        self.assertIn(
            '# rebase_model = "provider/model" # default for rebase sessions',
            config.read_text(),
        )

    def test_init_adds_rebase_model_after_review_model_when_upgrading(self):
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('rebase_model = "rebase-model"\n', ""))

        self.run_cli("init")

        lines = config.read_text().splitlines()
        review_line = lines.index('review_model = "review-model"')
        self.assertEqual(
            lines[review_line + 1],
            '# rebase_model = "provider/model" # default for rebase sessions',
        )

    def test_model_arguments_select_each_mode_and_reject_unknown_modes(self):
        repo = Repo.open(self.root)
        for mode, expected in (
            ("work", ("--model", "work-model")),
            ("review", ("--model", "review-model")),
            ("rebase", ("--model", "rebase-model")),
        ):
            with self.subTest(mode=mode):
                self.assertEqual(_model_arguments(repo, mode, (), ()), expected)
                self.assertEqual(_model_arguments(repo, mode, (), ("--model", "manual")), ())

        with self.assertRaisesRegex(ChittyError, "other"):
            _model_arguments(repo, "other", (), ())

        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace('rebase_model = "rebase-model"\n', ""))
        repo = Repo.open(self.root)
        self.assertEqual(_model_arguments(repo, "rebase", (), ()), ())

    def test_blank_models_are_rejected(self):
        config = self.root / "chitty.toml"
        original = config.read_text()
        for name in ("work_model", "review_model", "rebase_model"):
            with self.subTest(name=name):
                config.write_text(
                    original.replace(f'{name} = "{name.split("_")[0]}-model"', f'{name} = "  "')
                )
                with self.assertRaisesRegex(ChittyError, name):
                    Repo.open(self.root)
        config.write_text(original)
