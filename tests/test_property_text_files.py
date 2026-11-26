import json
import os
import tempfile
from pathlib import Path
from typing import Any
from unittest import mock

from click.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.cli import cli, reads_stdin
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
        for mode in ("inline", "file", "stdin", "bare-stdin"):
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
                    args += [option if mode in ("inline", "bare-stdin") else option + "-file"]
                    args += [text if mode == "inline" else str(file) if mode == "file" else "-"]
                    result = self.run_cli(
                        *args, "--json", input=text if mode in ("stdin", "bare-stdin") else None
                    )
                    task_id = result["id"]
                    shown = self.run_cli("show", task_id, "--json")
                    results.append({field: shown[field] for field in FIELDS})
        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0], results[2])
        self.assertEqual(results[2], results[3])

    def test_suggest_stdin(self):
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            self.run_cli("init")
            self.run_cli("suggest", self.root.name, "T", "-d", "a é")
            self.run_cli("suggest", self.root.name, "T", "--description-file", "-", input="a é")
            items = self.run_cli("inbox", "--json")
            self.assertEqual(len(items), 2)
            self.assertEqual(items[0]["description"], items[1]["description"])

    @settings(max_examples=examples(25), deadline=None)
    @given(text=TEXT)
    def test_suggest_bare_stdin(self, text):
        with tempfile.TemporaryDirectory(dir=self.tmp) as directory:
            root = Path(directory)
            (root / "chitty.toml").write_text(CONFIG)
            with mock.patch("pathlib.Path.cwd", return_value=root):
                self.run_cli("init")
                for option in ("--description", "--description-file"):
                    self.run_cli("suggest", str(root), "T", option, "-", input=text)
                items = self.run_cli("inbox", "--json")
                self.assertEqual(items[0]["description"], items[1]["description"])

    def test_bare_stdin_conflicts(self):
        cases = (
            ("--plan", "-", "--note", "-"),
            ("--plan", "-", "--note-file", "-"),
            ("--note", "-", "--note", "-"),
        )
        for options in cases:
            with self.subTest(options=options):
                with mock.patch("pathlib.Path.cwd", return_value=self.root):
                    result = CliRunner().invoke(cli, ["edit", "TASK-1", *options], input="text")
                self.assertEqual(result.exit_code, 2, result.output)
                self.assertIn("only one file option can read stdin:", result.output)
                self.assertIn("--note-file", result.output)
                if options[0] == "--plan":
                    self.assertIn("--plan-file", result.output)
                else:
                    self.assertEqual(result.output.count("--note-file"), 2)

    def test_bare_stdin_and_file_twin_are_mutually_exclusive(self):
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            for command in (("add", "T"), ("edit", "TASK-1"), ("suggest", ".", "T")):
                with self.subTest(command=command):
                    result = CliRunner().invoke(
                        cli, [*command, "--description", "-", "--description-file", "-"], input="x"
                    )
                    self.assertEqual(result.exit_code, 2, result.output)
                    self.assertIn(
                        "give --description or --description-file, not both", result.output
                    )

    @settings(max_examples=examples(15), deadline=None)
    @given(text=st.text(alphabet=st.characters(exclude_categories=("Cs",)), max_size=100))
    def test_arbitrary_stdin_matches_file_twin(self, text):
        cases = (
            ("add", "--description"),
            ("add", "--note"),
            ("edit", "--description"),
            ("edit", "--plan"),
            ("edit", "--note"),
            ("edit", "--set-notes"),
            ("edit", "--summary"),
            ("suggest", "--description"),
        )
        for command, option in cases:
            results = []
            for suffix in ("", "-file"):
                with tempfile.TemporaryDirectory(dir=self.tmp) as directory:
                    root = Path(directory)
                    (root / "chitty.toml").write_text(CONFIG)
                    with mock.patch("pathlib.Path.cwd", return_value=root):
                        if command == "edit":
                            task_id = self.run_cli("add", "T", "-d", "x", "--json")["id"]
                            args = ["edit", task_id]
                        elif command == "add":
                            args = ["add", "T"]
                            if option == "--note":
                                args += ["-d", "x"]
                        else:
                            self.run_cli("init")
                            args = ["suggest", str(root), "T"]
                        result = CliRunner().invoke(cli, [*args, option + suffix, "-"], input=text)
                        if result.exit_code == 0:
                            if command == "suggest":
                                value = self.run_cli("inbox", "--json")[0]["description"]
                            else:
                                shown = self.run_cli("show", "TASK-1", "--json")
                                value = {field: shown[field] for field in FIELDS}
                        else:
                            value = result.output
                        results.append((result.exit_code, value))
            self.assertEqual(results[0], results[1], (command, option, text))

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

    @settings(max_examples=examples(100), deadline=None)
    @given(
        values=st.lists(
            st.sampled_from([None, "-", "/dev/stdin", "/dev/fd/0", "file"]), min_size=4, max_size=4
        ).filter(lambda v: any(x is not None for x in v))
    )
    def test_edit_stdin_aliases(self, values):
        options = ("--description-file", "--plan-file", "--note-file", "--summary-file")
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            task_id = (
                self.run_cli("add", "T", "-d", "x", "--json")["id"]
                if not list((self.root / "chitty/tasks").glob("*.md"))
                else "TASK-1"
            )
            task = next((self.root / "chitty/tasks").glob("*.md"))
            before = task.read_bytes()
            file = self.root / "text.txt"
            file.write_text("text")
            args = ["edit", task_id]
            for option, value in zip(options, values):
                if value is not None:
                    args.extend([option, str(file) if value == "file" else value])
            saved = os.dup(0)
            try:
                with file.open("rb") as stream:
                    os.dup2(stream.fileno(), 0)
                    result = CliRunner().invoke(cli, args, input="text")
            finally:
                os.dup2(saved, 0)
                os.close(saved)
            stdin_options = [
                o for o, v in zip(options, values) if v in ("-", "/dev/stdin", "/dev/fd/0")
            ]
            self.assertEqual(result.exit_code, 2 if len(stdin_options) > 1 else 0, result.output)
            if len(stdin_options) > 1:
                for option in stdin_options:
                    self.assertIn(option, result.output)
                self.assertEqual(task.read_bytes(), before)

    def test_add_stdin_alias(self):
        with mock.patch("pathlib.Path.cwd", return_value=self.root):
            tasks = self.root / "chitty/tasks"
            before = set(tasks.glob("*"))
            with tempfile.TemporaryFile() as stream:
                stream.write(b"description")
                stream.seek(0)
                saved = os.dup(0)
                try:
                    os.dup2(stream.fileno(), 0)
                    result = CliRunner().invoke(
                        cli,
                        ["add", "T", "--description-file", "/dev/stdin", "--note-file", "-"],
                        input="text",
                    )
                finally:
                    os.dup2(saved, 0)
                    os.close(saved)
            self.assertEqual(result.exit_code, 2, result.output)
            self.assertEqual(set(tasks.glob("*")), before)

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


@given(
    name=st.text().filter(
        lambda s: s not in {"<stdin>", "/dev/stdin", "/dev/fd/0", "/proc/self/fd/0"}
    )
)
def test_reads_stdin(name):
    for value in ("<stdin>", "/dev/stdin", "/dev/fd/0", "/proc/self/fd/0"):
        assert reads_stdin(value)
    for value in (name, "/dev/stdin/", "/dev/fd/00", "/dev/fd/0/", "-", "<stdin>x", ""):
        assert not reads_stdin(value)


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
