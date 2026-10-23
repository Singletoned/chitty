import os

from chitty.config import find_root, load_repo_config, load_user_contexts
from chitty.errors import ChittyError
from tests.support import CONFIG, RepoTestCase


class TestRepoConfig(RepoTestCase):
    def test_loads(self):
        config = load_repo_config(self.root)
        self.assertEqual(config.default_context, "tasks")
        self.assertEqual(config.contexts["human"].prefix, "HUMAN")

    def test_rejections(self):
        cases = {
            "default_context 'nope'": CONFIG.replace('"tasks"', '"nope"', 1),
            "used by more than one": CONFIG.replace('"HUMAN"', '"TASK"'),
            "upper-case": CONFIG.replace('"HUMAN"', '"human"'),
            "autocommit": CONFIG.replace("autocommit = false", 'autocommit = "no"'),
            "Extra inputs": CONFIG + "colour = 1\n",
            "format": CONFIG.replace("format = 1", "format = 2"),
            "invalid TOML": CONFIG + "[[[",
            "not allowed": CONFIG.replace("contexts.human", "contexts.archive"),
        }
        for reason, text in cases.items():
            with self.subTest(reason=reason):
                (self.root / "chitty.toml").write_text(text)
                with self.assertRaisesRegex(ChittyError, reason):
                    load_repo_config(self.root)


class TestFindRoot(RepoTestCase):
    def test_walks_up(self):
        nested = self.root / "a" / "b"
        nested.mkdir(parents=True)
        self.assertEqual(find_root(nested), self.root)

    def test_env_override(self):
        os.environ["CHITTY_ROOT"] = str(self.root)
        self.assertEqual(find_root(self.tmp), self.root)
        os.environ["CHITTY_ROOT"] = str(self.tmp)
        with self.assertRaisesRegex(ChittyError, "has no chitty.toml"):
            find_root(self.root)

    def test_missing(self):
        with self.assertRaisesRegex(ChittyError, "chitty init"):
            find_root(self.tmp)


class TestUserContexts(RepoTestCase):
    def test_absent_file_is_empty(self):
        self.assertEqual(load_user_contexts().contexts, {})

    def test_loads(self):
        path = self.config_home / "chitty" / "contexts.toml"
        path.parent.mkdir(parents=True)
        path.write_text('[contexts.notes]\nrepo = "~/notes"\n')
        self.assertEqual(load_user_contexts().contexts["notes"].repo, "~/notes")
