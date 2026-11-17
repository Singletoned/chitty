import os
import subprocess
from datetime import date
from unittest import mock

from hypothesis import given, settings
from hypothesis import strategies as st

from chitty.config import load_repo_config
from chitty.errors import ChittyError
from chitty.ids import TaskId
from chitty.store import Edit, Repo
from tests.support import RepoTestCase

NOTES = st.text(
    alphabet=st.one_of(st.characters(min_codepoint=32, max_codepoint=126), st.just("\n")),
    min_size=1,
    max_size=80,
).filter(
    lambda text: (
        text.strip() and all(not line.startswith(("#", "```", "~~~")) for line in text.splitlines())
    )
)
TITLES = st.text(
    alphabet=st.characters(min_codepoint=32, max_codepoint=126),
    min_size=1,
    max_size=40,
).filter(lambda title: any(character.isalnum() for character in title))


class TestRefusedEditProperty(RepoTestCase):
    def setUp(self):
        super().setUp()
        actor = mock.patch.dict(os.environ, {"CHITTY_ACTOR": "test-agent"})
        actor.start()
        self.addCleanup(actor.stop)
        config = self.root / "chitty.toml"
        config.write_text(config.read_text().replace("autocommit = false", "autocommit = true"))
        for args in (
            ("init", "--quiet"),
            ("config", "user.email", "test@example.com"),
            ("config", "user.name", "Test"),
        ):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
        self.repo = Repo(self.root, load_repo_config(self.root))
        tasks = self.repo.context("tasks")
        self.repo.add(tasks, "First", "Describe.", [], {}, date(2026, 10, 23))
        self.repo.add(
            tasks, "Second", "Describe.", [], {"depends_on": ["TASK-1"]}, date(2026, 10, 23)
        )
        subprocess.run(
            ["git", "commit", "--quiet", "--allow-empty", "-m", "test baseline"],
            cwd=self.root,
            check=True,
            capture_output=True,
        )

    def _snapshot(self):
        files = {
            path.relative_to(self.root): path.read_bytes()
            for path in (self.root / "chitty").rglob("*")
            if path.is_file()
        }
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self.root,
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        return files, status

    @settings(max_examples=30, deadline=None)
    @given(
        invalid=st.sampled_from(("self-dependency", "cycle", "parent")),
        note=st.one_of(st.none(), NOTES),
        title=st.one_of(st.none(), TITLES),
    )
    def test_refused_edit_restores_repository(self, invalid, note, title):
        before = self._snapshot()
        kwargs = {"note": note, "title": title}
        if invalid == "self-dependency":
            kwargs["depends_on"] = ["TASK-1"]
        elif invalid == "cycle":
            kwargs["depends_on"] = ["TASK-2"]
        else:
            kwargs["parent"] = "TASK-1"
        with self.assertRaisesRegex(ChittyError, "cannot finalize task write"):
            self.repo.edit(TaskId("TASK", 1), Edit(**kwargs))
        self.assertEqual(self._snapshot(), before)
