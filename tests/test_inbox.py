from chitty.errors import ChittyError
from chitty.inbox import suggest
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
