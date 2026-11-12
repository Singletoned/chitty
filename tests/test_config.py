import contextlib
import io
import os
from unittest.mock import patch

from chitty import config as config_module
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
        self.assertEqual(config.agent_timeout, 7200)

    def test_job_order_validates_statuses_and_duplicates(self):
        config_path = self.root / "chitty.toml"
        config_path.write_text(
            CONFIG.replace(
                "autocommit = false", 'job_order = ["todo", "review"]\nautocommit = false'
            )
        )
        self.assertEqual(load_repo_config(self.root).job_order, ["todo", "review"])
        for value, message in (
            ("[]", "empty"),
            ('["typo"]', "typo"),
            ('["todo", "todo"]', "repeat"),
        ):
            with self.subTest(value=value):
                config_path.write_text(
                    CONFIG.replace("autocommit = false", f"job_order = {value}\nautocommit = false")
                )
                with self.assertRaisesRegex(ChittyError, message):
                    load_repo_config(self.root)

    def test_agent_timeout_can_be_disabled_and_uses_patchable_default(self):
        config_path = self.root / "chitty.toml"
        config_path.write_text(
            CONFIG.replace("autocommit = false", "agent_timeout = 0\nautocommit = false")
        )
        self.assertEqual(load_repo_config(self.root).agent_timeout, 0)
        config_path.write_text(CONFIG)
        with patch.object(config_module, "DEFAULT_AGENT_TIMEOUT", 2):
            self.assertEqual(load_repo_config(self.root).agent_timeout, 2)

    def test_agent_timeout_requires_nonnegative_toml_integer(self):
        config_path = self.root / "chitty.toml"
        for value in ("-5", '"10"'):
            with self.subTest(value=value):
                config_path.write_text(
                    CONFIG.replace(
                        "autocommit = false", f"agent_timeout = {value}\nautocommit = false"
                    )
                )
                with self.assertRaisesRegex(ChittyError, "agent_timeout"):
                    load_repo_config(self.root)

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

    def test_main_branch_defaults_and_loads_from_both_sources(self):
        for config_name, config_text in (
            ("chitty.toml", CONFIG),
            ("pyproject.toml", f"[tool.chitty]\n{PYPROJECT_CONFIG}"),
        ):
            with self.subTest(config_name=config_name):
                (self.root / "chitty.toml").unlink(missing_ok=True)
                (self.root / "pyproject.toml").unlink(missing_ok=True)
                path = self.root / config_name
                path.write_text(config_text)
                self.assertEqual(load_repo_config(self.root).main_branch, "main")
                path.write_text(
                    config_text.replace(
                        "autocommit = false", 'main_branch = "master"\nautocommit = false'
                    )
                )
                self.assertEqual(load_repo_config(self.root).main_branch, "master")

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

    def test_unknown_keys_warn_and_load_from_both_sources(self):
        for config_name, config_text in (
            ("chitty.toml", CONFIG),
            ("pyproject.toml", f"[tool.chitty]\n{PYPROJECT_CONFIG}"),
        ):
            for version in ("99.0.0", CHITTY_VERSION, "0.0.0", None):
                with self.subTest(config_name=config_name, version=version):
                    config_module._WARNED_UNKNOWN_KEYS.clear()
                    (self.root / "chitty.toml").unlink(missing_ok=True)
                    config_path = self.root / config_name
                    text = config_text.replace(
                        f'chitty_version = "{CHITTY_VERSION}"',
                        (f'chitty_version = "{version}"\n' if version else "") + 'colour = "blue"',
                    )
                    text = text.replace('prefix = "TASK"', 'prefix = "TASK"\ncolour = true')
                    config_path.write_text(text)
                    stderr = io.StringIO()
                    with contextlib.redirect_stderr(stderr):
                        config = load_repo_config(self.root)
                        load_repo_config(self.root)

                    self.assertEqual(config.default_context, "tasks")
                    self.assertEqual(
                        stderr.getvalue(),
                        f"{config_path}: ignoring unknown configuration key(s) "
                        "colour, contexts.tasks.colour; check the spelling or upgrade Chitty\n",
                    )

    def test_agent_command_names_are_not_unknown(self):
        config_path = self.root / "chitty.toml"
        config_path.write_text(config_path.read_text() + '\n[agent_commands]\ncolour = "x"\n')
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            config = load_repo_config(self.root)
        self.assertEqual(config.agent_commands, {"colour": "x"})
        self.assertEqual(stderr.getvalue(), "")

    def test_non_table_contexts_is_still_rejected(self):
        config_path = self.root / "chitty.toml"
        text = config_path.read_text().split("[contexts.tasks]")[0]
        config_path.write_text(text + 'contexts = "not a table"\n')
        with self.assertRaisesRegex(ChittyError, "contexts"):
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
