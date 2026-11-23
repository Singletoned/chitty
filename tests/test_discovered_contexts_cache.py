import shutil
import subprocess
from unittest.mock import patch

from chitty.store import Repo
from tests.test_cli import CliTestCase


class TestDiscoveredContextsCache(CliTestCase):
    def setUp(self):
        super().setUp()
        for args in (
            ("init", "-b", "main"),
            ("config", "user.name", "Test"),
            ("config", "user.email", "test@example.com"),
        ):
            subprocess.run(["git", *args], cwd=self.root, check=True, capture_output=True)
        self.run_cli("add", "example", "--status", "backlog")
        subprocess.run(["git", "add", "."], cwd=self.root, check=True)
        subprocess.run(
            ["git", "commit", "-m", "fixture"], cwd=self.root, check=True, capture_output=True
        )

    def test_cached(self):
        repo = Repo.open(self.root)
        first = repo.discovered_contexts()
        with patch.object(repo, "_ref_files", wraps=repo._ref_files) as wrapped:
            self.assertEqual(first, repo.discovered_contexts())
            self.assertEqual(wrapped.call_count, 0)

    def test_invalidate_per_instance(self):
        a = Repo.open(self.root)
        b = Repo.open(self.root)
        a.discovered_contexts()
        b.discovered_contexts()
        extra = self.root / "chitty/extra"
        extra.mkdir()
        shutil.copy(next((self.root / "chitty/tasks").glob("*.md")), extra / "EXTRA-1--x.md")
        a._invalidate()
        self.assertIn("extra", [c.name for c in a.discovered_contexts()])
        self.assertNotIn("extra", [c.name for c in b.discovered_contexts()])

    def test_returned_list_is_independent(self):
        repo = Repo.open(self.root)
        expected = repo.discovered_contexts()
        repo.discovered_contexts().clear()
        self.assertEqual(expected, repo.discovered_contexts())
