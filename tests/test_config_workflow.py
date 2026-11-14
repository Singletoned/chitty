"""Workflow setting: how a missing `workflow` resolves, and what it sets."""

import itertools
import unittest

from hypothesis import example, given
from hypothesis import strategies as st

from chitty import config as config_module
from chitty.config import CHITTY_VERSION, load_repo_config, version_key
from chitty.errors import ChittyError
from chitty.store import Repo
from tests.support import CONFIG, RepoTestCase

WORKFLOWS = ("tickets", "runner")
SETTINGS_VALUES = (None, True, False)
VERSION_LINE = f'chitty_version = "{CHITTY_VERSION}"\n'
VERSIONS = st.one_of(
    st.none(),
    st.lists(st.integers(min_value=0), min_size=1, max_size=4).map(
        lambda parts: ".".join(str(part) for part in parts)
    ),
    st.text(),
)


def expected_workflow(version: str | None) -> str:
    if version is None:
        return "runner"
    try:
        key = version_key(version)
    except ChittyError:
        return "runner"
    return "runner" if key < version_key("0.5.0") else "tickets"


class TestResolveWorkflow(unittest.TestCase):
    @given(VERSIONS)
    @example("0.4.9")
    @example("0.5")
    @example("0.5.0")
    @example("0.5.0.0")
    @example(None)
    def test_missing_workflow_follows_setup_version(self, version):
        self.assertEqual(config_module.resolve_workflow(None, version), expected_workflow(version))

    @given(st.sampled_from(WORKFLOWS), VERSIONS)
    @example("tickets", "0.4.9")
    @example("runner", "0.5.0")
    def test_explicit_workflow_is_returned_as_is(self, workflow, version):
        self.assertEqual(config_module.resolve_workflow(workflow, version), workflow)


class TestWorkflowConfig(RepoTestCase):
    def config_text(self, version_line: str = VERSION_LINE, extra: str = "") -> str:
        text = CONFIG.replace(VERSION_LINE, version_line)
        return text.replace("autocommit = false", f"{extra}autocommit = false")

    def test_missing_workflow_resolves_from_setup_version(self):
        cases = (
            ("", "runner"),
            ('chitty_version = "0.4.2"\n', "runner"),
            ('chitty_version = "0.5.0"\n', "tickets"),
            ('chitty_version = "1.0rc1"\n', "runner"),
        )
        for version_line, expected in cases:
            with self.subTest(version_line=version_line):
                (self.root / "chitty.toml").write_text(self.config_text(version_line))
                self.assertEqual(load_repo_config(self.root).workflow, expected)

    def test_explicit_workflow_wins_over_setup_version(self):
        cases = (
            ('chitty_version = "0.4.2"\n', 'workflow = "tickets"\n', "tickets"),
            ('chitty_version = "0.5.0"\n', 'workflow = "runner"\n', "runner"),
        )
        for version_line, extra, expected in cases:
            with self.subTest(extra=extra):
                (self.root / "chitty.toml").write_text(self.config_text(version_line, extra))
                self.assertEqual(load_repo_config(self.root).workflow, expected)

    def test_invalid_workflow_names_the_setting_and_allowed_values(self):
        for value in ('"bogus"', "1", "[]", "{}"):
            with self.subTest(value=value):
                (self.root / "chitty.toml").write_text(
                    self.config_text(extra=f"workflow = {value}\n")
                )
                with self.assertRaises(ChittyError) as caught:
                    load_repo_config(self.root)
                message = str(caught.exception)
                self.assertIn("workflow", message)
                self.assertIn("tickets", message)
                self.assertIn("runner", message)

    def test_non_string_setup_version_gives_only_its_own_error(self):
        (self.root / "chitty.toml").write_text(self.config_text("chitty_version = 1\n"))
        with self.assertRaises(ChittyError) as caught:
            load_repo_config(self.root)
        message = str(caught.exception)
        self.assertIn("chitty_version", message)
        self.assertNotIn("workflow", message)

    def test_review_default_and_overrides_under_each_workflow(self):
        for workflow, repo_review, context_review in itertools.product(
            WORKFLOWS, SETTINGS_VALUES, SETTINGS_VALUES
        ):
            with self.subTest(
                workflow=workflow, repo_review=repo_review, context_review=context_review
            ):
                extra = f'workflow = "{workflow}"\n'
                if repo_review is not None:
                    extra += f"review = {str(repo_review).lower()}\n"
                text = self.config_text(extra=extra)
                if context_review is not None:
                    text = text.replace(
                        'prefix = "TASK"',
                        f'prefix = "TASK"\nreview = {str(context_review).lower()}',
                    )
                (self.root / "chitty.toml").write_text(text)

                repo = Repo.open(self.root)
                default = workflow == "runner"
                expected_review = default if repo_review is None else repo_review
                expected_required = expected_review if context_review is None else context_review

                self.assertIs(repo.config.review, expected_review)
                self.assertIs(repo.review_required(repo.default_context), expected_required)
