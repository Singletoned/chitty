import os
from pathlib import Path
from unittest import mock

from chitty.config import load_repo_config, register_project
from chitty.errors import ChittyError
from chitty.inbox import pull, suggest
from chitty.store import Repo
from tests.support import RepoTestCase


class TestInbox(RepoTestCase):
    def setUp(self):
        super().setUp()
        self._actor = mock.patch.dict(os.environ, {"CHITTY_ACTOR": "test-agent"})
        self._actor.start()
        self.addCleanup(self._actor.stop)

    def test_suggestion_is_written_to_this_test_inbox(self):
        real_inbox = Path.home() / ".local/share/chitty/inbox"
        path = suggest("isolated", "Improve docs", None, True, self.root)

        self.assertTrue(path.exists())
        self.assertFalse(path.is_relative_to(real_inbox))

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

    def test_pull_keeps_sequential_default_context_with_backlog_configured(self):
        path = suggest("target", "Inbox task", None, True, self.root)
        config = (self.root / "chitty.toml").read_text().replace(
            'default_context = "tasks"', 'default_context = "tasks"\nproject = "target"'
        ) + '\n[contexts.backlog]\nprefix = "BACKLOG"\nrandom_ids = true\n'
        (self.root / "chitty.toml").write_text(config)

        repo = Repo(self.root, load_repo_config(self.root))
        self.assertEqual(pull(repo), ["TASK-1"])
        self.assertFalse(path.exists())
        self.assertTrue((self.root / "chitty/tasks/TASK-1--inbox-task.md").exists())

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
        self.assertRegex(
            task.section("History") or "", r"^- [0-9-]{10}T[0-9:]{8}Z test-agent → backlog\n"
        )
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

    def test_pull_keeps_imported_tasks_when_inbox_cleanup_fails(self):
        suggest("target", "One", None, True, self.root)
        suggest("target", "Two", None, True, self.root)
        config = (
            (self.root / "chitty.toml")
            .read_text()
            .replace('default_context = "tasks"', 'default_context = "tasks"\nproject = "target"')
        )
        (self.root / "chitty.toml").write_text(config)
        repo = Repo(self.root, load_repo_config(self.root))
        original_unlink = Path.unlink
        attempts = 0

        def fail_second_cleanup(path, *args, **kwargs):
            nonlocal attempts
            if path.suffix == ".done":
                attempts += 1
                if attempts == 2:
                    raise OSError("cleanup failed")
            return original_unlink(path, *args, **kwargs)

        with (
            mock.patch.object(Path, "unlink", fail_second_cleanup),
            self.assertRaisesRegex(OSError, "cleanup failed"),
        ):
            pull(repo)

        self.assertEqual(len(list((self.root / "chitty/tasks").glob("*.md"))), 2)

    def enter_directory_containing_chitty(self):
        """Work from a directory with a `chitty/` folder, as every Chitty repo has."""
        (self.root / "chitty").mkdir()
        previous = Path.cwd()
        os.chdir(self.root)
        self.addCleanup(os.chdir, previous)

    def test_registered_project_wins_over_same_named_local_directory(self):
        self.enter_directory_containing_chitty()
        register_project("chitty", self.root)

        path = suggest("chitty", "Improve docs", None, False, self.root)

        self.assertEqual(path.parent, self.tmp / "data" / "chitty" / "inbox" / "chitty")

    def test_bare_unregistered_local_directory_is_an_unknown_project(self):
        self.enter_directory_containing_chitty()
        with self.assertRaisesRegex(ChittyError, "unknown project 'chitty'.*use --create"):
            suggest("chitty", "Improve docs", None, False, self.root)

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
