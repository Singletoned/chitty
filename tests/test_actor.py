import os
import unittest
from unittest import mock

from chitty.errors import ChittyError


class TestActor(unittest.TestCase):
    def resolve(self, environment: dict[str, str]) -> str:
        from chitty.actor import actor

        with mock.patch.dict(os.environ, environment, clear=True):
            return actor()

    def test_override_takes_precedence(self):
        self.assertEqual(
            self.resolve({"CHITTY_ACTOR": "Ada", "PI_SESSION_ID": "pi-session"}), "Ada"
        )

    def test_harness_session_names_are_stable_and_readable(self):
        for variable in (
            "CLAUDE_CODE_SESSION_ID",
            "PI_SESSION_ID",
            "CODEX_THREAD_ID",
            "CODEX_SESSION_ID",
        ):
            with self.subTest(variable=variable):
                first = self.resolve({variable: "session-123"})
                self.assertEqual(first, self.resolve({variable: "session-123"}))
                self.assertRegex(first, r"^[a-z]+-[a-z]+$")

    def test_chitty_pi_session_identity_takes_precedence_over_child_session(self):
        parent = self.resolve({"PI_SESSION_ID": "parent-session"})
        child = self.resolve(
            {"CHITTY_PI_SESSION_ID": "parent-session", "PI_SESSION_ID": "child-session"}
        )
        self.assertEqual(child, parent)

    def test_missing_identity_fails_loudly(self):
        with self.assertRaisesRegex(ChittyError, "cannot determine actor"):
            self.resolve({})
