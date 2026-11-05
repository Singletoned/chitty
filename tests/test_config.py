import contextlib
import io
import os

from chitty.config import CHITTY_VERSION, find_root, load_repo_config, load_user_contexts
from chitty.errors import ChittyError
from tests.support import CONFIG, RepoTestCase

PYPROJECT_CONFIG = CONFIG.replace("[contexts.", "[tool.chitty.contexts.")


class TestRepoConfig(RepoTestCase):
    def test_loads(self):
        config = load_repo_config(self.root)
        self.assertEqual(config.default_context, "tasks")
        self.assertEqual(config.contexts["human"].prefix, "HUMAN")
        self.assertIsNone(config.contexts["human"].review)
        self.assertEqual(config.archive, "move")
        self.assertTrue(config.review)
        self.assertEqual(config.agent_command, "pi --chitty-{mode} {id}")

    def test_context_review_override_loads(self):
        config_path = self.root / "chitty.toml"
        config_path.write_text(
            config_path.read_text().replace('prefix = "HUMAN"', 'prefix = "HUMAN"\nreview = false')
        )

        config = load_repo_config(self.root)

        self.assertFalse(config.contexts["human"].review)

    def test_loads_pyproject_tool_table(self):
        (self.root / "chitty.toml").unlink()
        (self.root / "pyproject.toml").write_text(f"[tool.chitty]\n{PYPROJECT_CONFIG}")

        config = load_repo_config(self.root)

        self.assertEqual(config.default_context, "tasks")
        self.assertEqual(config.contexts["human"].prefix, "HUMAN")
        self.assertEqual(config.agent_command, "pi --chitty-{mode} {id}")

    def test_rejects_both_config_sources(self):
        (self.root / "pyproject.toml").write_text(f"[tool.chitty]\n{PYPROJECT_CONFIG}")

        with self.assertRaisesRegex(ChittyError, "both chitty.toml and pyproject.toml"):
            load_repo_config(self.root)

    def test_project_name_is_validated(self):
        text = CONFIG.replace(
            'default_context = "tasks"', 'default_context = "tasks"\nproject = "Bad Name"'
        )
        (self.root / "chitty.toml").write_text(text)
        with self.assertRaisesRegex(ChittyError, "lowercase"):
            load_repo_config(self.root)

    def test_newer_config_ignores_unknown_top_level_keys_once(self):
        config_path = self.root / "chitty.toml"
        config_path.write_text(
            config_path.read_text().replace(
                f'chitty_version = "{CHITTY_VERSION}"',
                'chitty_version = "99.0.0"\nnew_setting = "supported later"',
            )
        )
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            config = load_repo_config(self.root)
            load_repo_config(self.root)

        self.assertEqual(config.default_context, "tasks")
        self.assertIn("new_setting", stderr.getvalue())
        self.assertEqual(stderr.getvalue().count("new_setting"), 1)

    def test_unknown_top_level_keys_refuse_without_a_newer_version(self):
        original = (self.root / "chitty.toml").read_text()
        cases = {
            "equal": original + "new_setting = 1\n",
            "older": original.replace(
                f'chitty_version = "{CHITTY_VERSION}"',
                'chitty_version = "0.0.0"',
            )
            + "new_setting = 1\n",
            "absent": original.replace(f'chitty_version = "{CHITTY_VERSION}"\n', "")
            + "new_setting = 1\n",
        }
        for version, text in cases.items():
            with self.subTest(version=version):
                (self.root / "chitty.toml").write_text(text)
                with self.assertRaisesRegex(ChittyError, "Extra inputs"):
                    load_repo_config(self.root)

    def test_unknown_context_keys_still_refuse_in_newer_config(self):
        config_path = self.root / "chitty.toml"
        config_path.write_text(
            config_path.read_text()
            .replace(
                f'chitty_version = "{CHITTY_VERSION}"',
                'chitty_version = "99.0.0"',
            )
            .replace('prefix = "TASK"', 'prefix = "TASK"\nnew_setting = 1')
        )
        with self.assertRaisesRegex(ChittyError, "Extra inputs"):
            load_repo_config(self.root)

    def test_rejections(self):
        cases = {
            "default_context 'nope'": CONFIG.replace('"tasks"', '"nope"', 1),
            "used by more than one": CONFIG.replace('"HUMAN"', '"TASK"'),
            "upper-case": CONFIG.replace('"HUMAN"', '"human"'),
            "autocommit": CONFIG.replace("autocommit = false", 'autocommit = "no"'),
            "archive": CONFIG.replace("autocommit = false", 'archive = "remove"'),
            "review": CONFIG.replace("autocommit = false", 'review = "sometimes"'),
            "contexts.human.review": CONFIG.replace(
                'prefix = "HUMAN"', 'prefix = "HUMAN"\nreview = "sometimes"'
            ),
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

    def test_walks_up_to_pyproject_tool_table(self):
        (self.root / "chitty.toml").unlink()
        (self.root / "pyproject.toml").write_text(f"[tool.chitty]\n{PYPROJECT_CONFIG}")
        nested = self.root / "a" / "b"
        nested.mkdir(parents=True)

        self.assertEqual(find_root(nested), self.root)

    def test_ignores_pyproject_without_chitty_config(self):
        (self.root / "chitty.toml").unlink()
        (self.root / "pyproject.toml").write_text("[project]\nname = 'other'\n")

        with self.assertRaisesRegex(ChittyError, "chitty init"):
            find_root(self.root)

    def test_env_override(self):
        os.environ["CHITTY_ROOT"] = str(self.root)
        self.assertEqual(find_root(self.tmp), self.root)
        os.environ["CHITTY_ROOT"] = str(self.tmp)
        with self.assertRaisesRegex(ChittyError, "has no Chitty configuration"):
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
