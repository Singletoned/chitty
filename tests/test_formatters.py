"""Tool output must survive the supported formatters.

These tests need the pinned formatters (`make install`). They fail, never
skip, when one is missing.
"""

import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from chitty.model import Task, new_task, parse

PRETTIER = Path(__file__).resolve().parent.parent / "node_modules" / ".bin" / "prettier"
LONG = "a criterion long enough that prettier with proseWrap always has to wrap it " * 2

FORMATTERS = {
    "prettier": [str(PRETTIER), "--no-config", "--write"],
    "prettier-wrap": [str(PRETTIER), "--no-config", "--prose-wrap", "always", "--write"],
    "mdformat": [sys.executable, "-m", "mdformat"],
}


def run_formatter(name: str, text: str) -> str:
    if name.startswith("prettier") and not PRETTIER.exists():
        raise AssertionError(f"{PRETTIER} is missing: run `make install`")
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "TASK-1--x.md"
        path.write_text(text)
        subprocess.run([*FORMATTERS[name], str(path)], check=True, capture_output=True)
        return path.read_text()


def sample() -> Task:
    task = new_task(
        title="Add search to the task list",
        created=date(2026, 10, 23),
        description="Free markdown with `code` and a [link](https://example.com).",
        criteria=["Short one", LONG.strip(), "Matching is case-insensitive"],
        fields={
            "labels": ["search", "cli"],
            "priority": "medium",
            "owner": "ed",
            "depends_on": ["TASK-7", "HUMAN-1"],
            "moved_from": "HUMAN-3",
        },
    )
    task = task.with_criteria(add=(), remove=(), check=[3], uncheck=())
    task = task.with_section("Plan", "- First\n- Second")
    return task.with_note("A note.").with_note("Another note.")


class TestFormattersAreNoOps(unittest.TestCase):
    def test_tool_output_is_unchanged(self):
        text = sample().render()
        for name in ("prettier", "mdformat"):
            with self.subTest(formatter=name):
                self.assertEqual(run_formatter(name, text), text)


class TestFormattersPreserveMeaning(unittest.TestCase):
    def test_wrapped_criterion_is_one_criterion(self):
        task = sample()
        wrapped = run_formatter("prettier-wrap", task.render())
        self.assertNotEqual(wrapped, task.render())
        reparsed = parse(wrapped)
        self.assertEqual(reparsed.as_dict(), task.as_dict())

    def test_ticking_a_wrapped_criterion_keeps_the_wrapping(self):
        wrapped = run_formatter("prettier-wrap", sample().render())
        ticked = parse(wrapped).with_criteria(add=(), remove=(), check=[2], uncheck=())
        self.assertEqual(ticked.render(), wrapped.replace("- [ ] a criterion", "- [x] a criterion"))
        self.assertEqual(run_formatter("prettier-wrap", ticked.render()), ticked.render())

    def test_awkward_scalars_keep_their_meaning(self):
        task = sample()
        for value in ("no", "2026-10-23", "1e3", '"quoted" title', "#tag", "a: b"):
            edited = task.with_field("title", value).with_field("labels", [value, "x"])
            for name in FORMATTERS:
                with self.subTest(value=value, formatter=name):
                    reparsed = parse(run_formatter(name, edited.render()))
                    self.assertEqual(reparsed.as_dict(), edited.as_dict())


if __name__ == "__main__":
    unittest.main()
