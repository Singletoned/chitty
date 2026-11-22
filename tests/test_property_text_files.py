import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock

from click.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.cli import cli
from tests import examples
from tests.support import CONFIG, RepoTestCase

TEXT = st.text(alphabet="ab1 \n`'\"$\\*é", min_size=1, max_size=60).filter(
    lambda text: any(c in text for c in "ab") and "```" not in text
)
FIELDS = ("description", "plan", "notes", "summary", "acceptance_criteria")


class TestTextFiles(RepoTestCase):
    def setUp(self):
        super().setUp()
        os.environ["CHITTY_ACTOR"] = "test-agent"

    def run_cli(self, *args, input=None) -> Any:
        result = CliRunner().invoke(cli, list(args), input=input, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return json.loads(result.stdout) if "--json" in args else result.stdout

    def compare_option(self, command, option, text):
        results = []
        for mode in ("inline", "file", "stdin"):
            with tempfile.TemporaryDirectory(dir=self.tmp) as directory:
                root = Path(directory)
                (root / "chitty.toml").write_text(CONFIG)
                file = root / "text.txt"
                file.write_text(text, encoding="utf-8")
                with mock.patch("pathlib.Path.cwd", return_value=root):
                    if command == "edit":
                        task_id = self.run_cli("add", "T", "-d", "x", "--json")["id"]
                        args = ["edit", task_id]
                    else:
                        args = ["add", "T"]
                        if option != "--description":
                            args += ["-d", "x"]
                    args += [option if mode == "inline" else option + "-file"]
                    args += [text if mode == "inline" else str(file) if mode == "file" else "-"]
                    result = self.run_cli(*args, "--json", input=text if mode == "stdin" else None)
                    task_id = result["id"]
                    shown = self.run_cli("show", task_id, "--json")
                    results.append({field: shown[field] for field in FIELDS})
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0], results[2])

    def test_suggest_stdin(self):
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            self.run_cli("init")
            self.run_cli("suggest", self.root.name, "T", "-d", "a é")
            self.run_cli("suggest", self.root.name, "T", "--description-file", "-", input="a é")
            items = self.run_cli("inbox", "--json")
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]["description"], items[1]["description"])

    def test_two_stdin_options(self):
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            for args in (("add", "T"), ("edit", "TASK-1")):
                with self.subTest(args=args):
                    result = CliRunner().invoke(
                        cli, [*args, "--description-file", "-", "--note-file", "-"], input="a"
                    )
                    self.assertEqual(result.exit_code, 2, result.output)
                    self.assertIn("--description-file", result.output)
                    self.assertIn("--note-file", result.output)

    def test_add_stdin_description_and_required_check(self):
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            result = CliRunner().invoke(cli, ["add", "T", "--note-file", "-"], input="note")
            self.assertEqual(result.exit_code, 2, result.output)
            self.assertIn("--description is required unless --status backlog", result.output)
            created = self.run_cli(
                "add", "T", "--description-file", "-", "--json", input="description"
            )
            self.assertEqual(
                self.run_cli("show", created["id"], "--json")["description"], "description"
            )


def option_test(command, option):
    @settings(max_examples=examples(25), deadline=None)
    @given(text=TEXT)
    def test(self, text):
        self.compare_option(command, option, text)

    return test


for command, option in (
    ("add", "--description"),
    ("add", "--note"),
    ("edit", "--description"),
    ("edit", "--plan"),
    ("edit", "--note"),
    ("edit", "--set-notes"),
    ("edit", "--summary"),
):
    setattr(
        TestTextFiles,
        f"test_{command}_{option[2:].replace('-', '_')}",
        option_test(command, option),
    )
