import json
import os
import string
import unittest
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner
from hypothesis import given, settings
from hypothesis import strategies as st
from pydantic import ValidationError

from chitty.cli import cli
from chitty.config import RepoConfig
from chitty.ids import TaskId
from chitty.model import parse
from chitty.selection import TicketFacts, choose, priority_rank
from chitty.store import StoredTask, ordered
from tests import examples
from tests.support import RepoTestCase


class PriorityOrderingCliTests(RepoTestCase):
    def test_default_priority_order(self) -> None:
        previous = os.getcwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)
        self.enterContext(patch.dict(os.environ, {"CHITTY_ACTOR": "test-agent"}))
        runner = CliRunner()
        for priority in ("low", None, "medium", "high"):
            args = ["add", str(priority), "-d", "x"]
            if priority is not None:
                args.extend(("-p", priority))
            result = runner.invoke(cli, args, catch_exceptions=False)
            self.assertEqual(result.exit_code, 0, result.output)
        result = runner.invoke(cli, ["list", "--json"], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        self.assertEqual(
            [task["priority"] for task in json.loads(result.stdout)],
            ["high", "medium", None, "low"],
        )


class PriorityOrderingProperties(unittest.TestCase):
    @settings(max_examples=examples(50))
    @given(
        priorities=st.permutations(["high", "medium", "low", ""]),
        status=st.sampled_from(("todo", "doing", "review")),
        values=st.lists(st.sampled_from(("high", "medium", "low", None)), min_size=1, max_size=8),
    )
    def test_ordering(self, priorities, status, values) -> None:
        tasks = []
        facts = []
        for number, value in enumerate(values, 1):
            field = f"priority: {value}\n" if value is not None else ""
            task = parse(
                f"---\ntitle: Test\nstatus: {status}\n{field}created: 2026-01-01\n---\n"
                "\n## Description\n\nTest.\n"
            )
            tasks.append(
                StoredTask(TaskId("TASK", number), "tasks", Path(str(number)), False, task)
            )
            facts.append(TicketFacts(f"TASK-{number}", "tasks", status, value, None, False, False))

        def rank(value):
            return priorities.index("" if value is None else value)

        result = ordered(tasks, statuses=(status,), priorities=priorities)
        self.assertEqual(
            result, sorted(tasks, key=lambda task: rank(task.task.frontmatter.priority))
        )
        selected = choose(tuple(facts), priorities=priorities)
        self.assertIsNotNone(selected)
        assert selected is not None
        self.assertEqual(rank(selected.priority), min(map(rank, values)))

    @settings(max_examples=examples(50))
    @given(
        names=st.lists(st.text(min_size=1, max_size=10), unique=True, max_size=8),
        name=st.one_of(st.none(), st.text(max_size=10)),
        position=st.integers(min_value=0, max_value=8),
    )
    def test_rank(self, names, name, position) -> None:
        priorities = list(names)
        priorities.insert(position, "")
        value = "" if name is None else name
        expected = next((i for i, item in enumerate(priorities) if item == value), len(priorities))
        self.assertEqual(priority_rank(name, priorities), expected)


class PrioritiesConfigTests(unittest.TestCase):
    def config(self, **extra: object) -> RepoConfig:
        return RepoConfig.model_validate(
            {
                "format": 1,
                "default_context": "tasks",
                "autocommit": False,
                "contexts": {"tasks": {"prefix": "TASK"}},
                **extra,
            }
        )

    def assert_refused(self, priorities: list[str], message: str) -> None:
        with self.assertRaises(ValidationError) as caught:
            self.config(priorities=priorities)
        self.assertIn(message, str(caught.exception))

    def test_default(self) -> None:
        self.assertEqual(self.config().priorities, ["high", "medium", "", "low"])

    def test_missing_empty(self) -> None:
        self.assert_refused(
            ["high"], 'priorities must contain "" exactly once, to place tickets with no priority'
        )

    def test_repeated_empty(self) -> None:
        self.assert_refused(
            ["", ""], 'priorities must contain "" exactly once, to place tickets with no priority'
        )

    def test_duplicate_name(self) -> None:
        self.assert_refused(["a", "a", ""], "priorities lists 'a' twice")

    def test_surrounding_whitespace(self) -> None:
        self.assert_refused(
            [" a", ""],
            "priority ' a' must be one word or phrase on one line, without surrounding spaces",
        )

    @settings(max_examples=examples(50))
    @given(
        name=st.text(alphabet=string.ascii_letters, min_size=1, max_size=5),
        boundary=st.sampled_from("\n\r\x0b\x0c\x1c\x1d\x1e\x85\u2028\u2029"),
        data=st.data(),
    )
    def test_line_break(self, name: str, boundary: str, data: st.DataObject) -> None:
        position = data.draw(st.integers(min_value=0, max_value=len(name)))
        name = name[:position] + boundary + name[position:]
        self.assert_refused(
            [name, ""],
            f"priority {name!r} must be one word or phrase on one line, without surrounding spaces",
        )
