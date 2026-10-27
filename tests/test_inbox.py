from unittest import mock

from chitty.config import load_repo_config
from chitty.errors import ChittyError
from chitty.inbox import pull, suggest
from chitty.store import Repo
from tests.support import RepoTestCase


class TestInbox(RepoTestCase):
    def test_create_writes_atomic_suggestion_with_origin(self):
        path = suggest("open-source", "Improve docs", "Explain setup.", True, self.root)

        self.assertTrue(path.exists())
        text = path.read_text()
        self.assertIn("title: Improve docs", text)
        self.assertIn("origin:", text)
        self.assertIn("## Description", text)

    def test_unknown_project_lists_known_names_and_create(self):
        suggest("known", "One", None, True, self.root)

        with self.assertRaisesRegex(ChittyError, "known projects: known; use --create"):
            suggest("unknown", "Two", None, False, self.root)

    def test_pull_creates_backlog_task_and_removes_suggestion(self):
        path = suggest("target", "Inbox task", None, True, self.root)
        config = (
            (self.root / "chitty.toml")
            .read_text()
            .replace('default_context = "tasks"', 'default_context = "tasks"\nproject = "target"')
        )
        (self.root / "chitty.toml").write_text(config)

        repo = Repo(self.root, load_repo_config(self.root))
        ids = pull(repo)

        self.assertEqual(ids, ["TASK-1"])
        self.assertFalse(path.exists())
        task = repo.find(repo.resolve("TASK-1")).task
        self.assertEqual(task.frontmatter.status, "backlog")
        self.assertIn("→ backlog", task.section("History") or "")
        self.assertIn("Suggestion origin", task.render())

    def test_pull_releases_invalid_suggestion_and_restores_config(self):
        path = suggest("target", "Inbox task", None, True, self.root)
        path.write_text("invalid suggestion")
        config = (
            (self.root / "chitty.toml")
            .read_text()
            .replace('default_context = "tasks"', 'default_context = "tasks"\nproject = "target"')
        )
        (self.root / "chitty.toml").write_text(config)
        repo = Repo(self.root, load_repo_config(self.root))
        configured = repo.config

        with self.assertRaises(ValueError):
            pull(repo)

        self.assertTrue(path.exists())
        self.assertFalse(path.with_suffix(".processing").exists())
        self.assertIs(repo.config, configured)

    def test_pull_releases_suggestion_when_task_creation_fails(self):
        path = suggest("target", "Inbox task", None, True, self.root)
        config = (
            (self.root / "chitty.toml")
            .read_text()
            .replace('default_context = "tasks"', 'default_context = "tasks"\nproject = "target"')
        )
        (self.root / "chitty.toml").write_text(config)
        repo = Repo(self.root, load_repo_config(self.root))
        configured = repo.config

        with (
            mock.patch.object(repo, "add", side_effect=ChittyError("write failed")),
            self.assertRaisesRegex(ChittyError, "write failed"),
        ):
            pull(repo)

        self.assertTrue(path.exists())
        self.assertFalse(path.with_suffix(".processing").exists())
        self.assertIs(repo.config, configured)

    def test_pull_rolls_back_created_task_when_note_creation_fails(self):
        path = suggest("target", "Inbox task", None, True, self.root)
        config = (
            (self.root / "chitty.toml")
            .read_text()
            .replace('default_context = "tasks"', 'default_context = "tasks"\nproject = "target"')
        )
        (self.root / "chitty.toml").write_text(config)
        repo = Repo(self.root, load_repo_config(self.root))

        with (
            mock.patch.object(repo, "edit", side_effect=ChittyError("write failed")),
            self.assertRaisesRegex(ChittyError, "write failed"),
        ):
            pull(repo)

        self.assertTrue(path.exists())
        self.assertEqual(list((self.root / "chitty" / "tasks").glob("*.md")), [])

    def test_path_resolves_project_config(self):
        other = self.tmp / "other"
        other.mkdir()
        (other / "chitty.toml").write_text(
            (self.root / "chitty.toml")
            .read_text()
            .replace('default_context = "tasks"', 'default_context = "tasks"\nproject = "other"')
        )

        path = suggest(str(other), "By path", None, False, self.root)

        self.assertIn("other", str(path))
