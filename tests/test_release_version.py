import importlib.util
import os
import string
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from chitty.model import STATUSES, parse

SCRIPT = Path(__file__).parents[1] / "scripts" / "release_version.py"
_spec = importlib.util.spec_from_file_location("release_version", SCRIPT)
assert _spec is not None and _spec.loader is not None
_release_version = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_release_version)


def parsed_ticket(status: str, labels: list[str], title: str):
    labels_line = f"labels: [{', '.join(labels)}]\n" if labels else ""
    return parse(
        "---\n"
        f"title: {title!r}\n"
        f"status: {status}\n"
        f"{labels_line}"
        "created: 2026-01-01\n"
        "---\n\n"
        "## Description\n\nExample.\n"
    )


@st.composite
def ticket_pairs(draw):
    status = draw(st.sampled_from(STATUSES))
    labels = draw(
        st.sets(
            st.sampled_from(
                [
                    "blocks-release",
                    "needs-minor",
                    "other",
                    "blocks-release-later",
                    "needs-minor-old",
                ]
            )
        )
    )
    title = draw(
        st.text(alphabet=string.ascii_letters + " ", min_size=1).filter(
            lambda value: any(char in string.ascii_letters for char in value)
        )
    )
    directory = draw(
        st.sampled_from(
            [
                "chitty/tasks",
                "chitty/human",
                "chitty/backlog",
                "chitty/tasks/archive",
            ]
        )
    )
    if directory.endswith("backlog"):
        identifier = f"BACKLOG-{draw(st.integers(min_value=1, max_value=99999999)):08d}"
    elif directory.endswith("human"):
        identifier = f"HUMAN-{draw(st.integers(min_value=1, max_value=999999))}"
    else:
        identifier = f"TASK-{draw(st.integers(min_value=1, max_value=999999))}"
    slug = draw(st.sampled_from(["example", "archive-notes"]))
    path = Path(directory) / f"{identifier}--{slug}.md"
    return path, parsed_ticket(status, sorted(labels), title)


class ReleaseVersionTest(unittest.TestCase):
    @given(st.lists(ticket_pairs(), max_size=20))
    def test_ticket_selectors_match_labels_status_and_archive_parts(self, tickets):
        blockers = [
            pair
            for pair in tickets
            if "blocks-release" in pair[1].frontmatter.labels
            and pair[1].frontmatter.status != "done"
            and "archive" not in pair[0].parts
        ]
        minors = [
            pair
            for pair in tickets
            if "needs-minor" in pair[1].frontmatter.labels and pair[1].frontmatter.status == "done"
        ]
        self.assertEqual(_release_version.release_blockers(tickets), blockers)
        self.assertEqual(_release_version.minor_tickets(tickets), minors)

    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        self.git("init", "--quiet", "-b", "main")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Test")
        self.write_version("0.1.9")
        self.commit("initial")
        self.git("tag", "v0.1.9")

    def git(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=self.root, check=True, capture_output=True, text=True
        )
        return result.stdout

    def write(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

    def write_version(self, version: str) -> None:
        self.write("src/chitty/__init__.py", f'__version__ = "{version}"\n')

    def commit(self, message: str) -> None:
        self.git("add", "--all")
        self.git("commit", "--quiet", "-m", message)

    def ticket(self, path: str, labels: str = "", status: str = "done") -> None:
        labels_line = f"labels: [{labels}]\n" if labels else ""
        self.write(
            path,
            "---\n"
            "title: Example\n"
            f"status: {status}\n"
            f"{labels_line}"
            "created: 2026-01-01\n"
            "---\n\n"
            "## Description\n\nExample.\n",
        )

    def run_script(self) -> subprocess.CompletedProcess[str]:
        environment = os.environ.copy()
        environment["PYTHONPATH"] = str(Path(__file__).parents[1] / "src")
        return subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
            env=environment,
        )

    def test_patch_bump_without_label(self):
        self.ticket("chitty/tasks/TASK-1--example.md")
        self.commit("ticket")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.10")
        self.assertEqual(result.stderr, "")

    def test_minor_bump_for_active_or_archived_labelled_ticket(self):
        self.ticket("chitty/tasks/TASK-1--active.md", "needs-minor")
        self.ticket("chitty/tasks/archive/TASK-2--archived.md", "needs-minor")
        self.commit("labelled tickets")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.2.0")
        self.assertIn("TASK-1", result.stderr)
        self.assertIn("TASK-2", result.stderr)

    def test_label_before_tag_is_ignored(self):
        self.ticket("chitty/tasks/TASK-1--example.md", "needs-minor")
        self.commit("old ticket")
        self.git("tag", "v0.1.10")
        self.write("README.md", "changed\n")
        self.commit("unrelated change")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.11")
        self.assertEqual(result.stderr, "")

    def test_open_task_blocker_fails_even_when_unchanged_since_tag(self):
        self.ticket("chitty/tasks/TASK-1--example.md", "blocks-release", "todo")
        self.commit("blocker")
        self.git("tag", "v0.1.10")
        self.write("README.md", "changed\n")
        self.commit("unrelated change")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("TASK-1: Example", result.stderr)

    def test_human_blocker_fails_even_when_unchanged_since_tag(self):
        self.ticket("chitty/human/HUMAN-12--example.md", "blocks-release", "doing")
        self.commit("blocker")
        self.git("tag", "v0.1.10")
        self.write("README.md", "changed\n")
        self.commit("unrelated change")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("HUMAN-12: Example", result.stderr)

    def test_done_blocker_at_tag_does_not_block_release(self):
        self.ticket("chitty/tasks/TASK-1--example.md", "blocks-release")
        self.commit("done blocker")
        self.git("tag", "v0.1.10")
        self.write("README.md", "changed\n")
        self.commit("unrelated change")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.11")
        self.assertEqual(result.stderr, "")

    def test_malformed_ticket_filename_fails(self):
        self.ticket("chitty/tasks/not-a-ticket.md")
        self.commit("malformed ticket filename")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(result.stdout, "")
        self.assertIn("invalid task ID", result.stderr)

    def test_todo_needs_minor_does_not_bump_minor(self):
        self.ticket("chitty/tasks/TASK-1--example.md", "needs-minor", "todo")
        self.commit("ticket")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.10")
        self.assertEqual(result.stderr, "")

    def test_current_version_ahead_of_tag_is_bump_base(self):
        self.write_version("0.1.20")
        self.commit("version ahead")
        result = self.run_script()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "0.1.21")

    def test_missing_tag_fails(self):
        self.git("tag", "--delete", "v0.1.9")
        result = self.run_script()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no v* tags", result.stderr)


if __name__ == "__main__":
    unittest.main()
