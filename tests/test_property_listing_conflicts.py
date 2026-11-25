import os
import tempfile
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tests import examples
from tests.test_source_copy_errors import SourceCopyErrorChecks


class TestListingConflicts(SourceCopyErrorChecks):
    @settings(max_examples=examples(25), deadline=None)
    @given(states=st.lists(st.sampled_from(["plain", "both", "diverged"]), min_size=1, max_size=4))
    def test_conflicts(self, states):
        original_root = self.root
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as temp:
            self.root = Path(temp)
            os.chdir(self.root)
            try:
                (self.root / "chitty.toml").write_text((original_root / "chitty.toml").read_text())
                self.init_git()
                for number in range(1, len(states) + 1):
                    self.file(number)
                self.commit()
                errors = {}
                for number, state in enumerate(states, 1):
                    if state == "plain":
                        continue
                    self.git("checkout", "-b", f"task-{number}")
                    self.file(number, "branch")
                    self.commit()
                    if state == "diverged":
                        self.git(
                            "update-ref",
                            f"refs/remotes/origin/task-{number}",
                            self.git("rev-parse", "HEAD"),
                        )
                        self.git("reset", "--hard", "main")
                        self.file(number, "local")
                        self.commit()
                        errors[f"TASK-{number}"] = (
                            f"ticket `TASK-{number}` has diverged refs: "
                            f"`origin/task-{number}`, `task-{number}`"
                        )
                    self.git("checkout", "main")
                    if state == "both":
                        self.file(number, "main")
                        self.commit()
                        errors[f"TASK-{number}"] = (
                            f"ticket `TASK-{number}` changed on both `task-{number}` and `main`"
                        )
                output = self.run_cli("list").output
                listed = self.json("list")
                self.assertEqual(
                    {item["id"] for item in listed},
                    {f"TASK-{n}" for n in range(1, len(states) + 1)},
                )
                self.assertEqual(len(listed), len(states))
                for item in listed:
                    ticket = item["id"]
                    line = next(
                        line for line in output.splitlines() if line.startswith(ticket + " ")
                    )
                    if ticket in errors:
                        self.assertIn("🔀", line)
                        self.assertIn(errors[ticket], output)
                        self.assertEqual(item["conflict"], errors[ticket])
                    else:
                        self.assertNotIn("🔀", line)
                        self.assertNotIn("conflict", item)
            finally:
                os.chdir(original_cwd)
                self.root = original_root

    def test_next_skips_conflict_and_show_still_fails(self):
        self.setup_changed_both()
        path = self.file(1, "main")
        path.write_text(path.read_text().replace("status: todo", "status: todo\npriority: high"))
        self.commit()
        self.assertIn("TASK-2", self.run_cli("next").output)
        self.assertIn("changed on both", self.run_cli("show", "TASK-1", exit_code=1).output)
