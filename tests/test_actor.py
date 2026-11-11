import os
import unittest
from unittest import mock

from chitty.errors import ChittyError


class TestActor(unittest.TestCase):
    def resolve(self, environment: dict[str, str]) -> str:
        from chitty.actor import actor

        with mock.patch.dict(os.environ, environment, clear=True):
            return actor()

    def test_run_actor_uses_run_source(self):
        from chitty.actor import run_actor

        self.assertEqual(run_actor("run-session"), run_actor("run-session"))
        self.assertRegex(run_actor("run-session"), r"^[a-z]+-[a-z]+-[a-z]+$")
        self.assertNotEqual(
            run_actor("run-session"), self.resolve({"PI_SESSION_ID": "run-session"})
        )

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
                self.assertRegex(first, r"^[a-z]+-[a-z]+-[a-z]+$")
                from chitty.actor import _COLOURS

                self.assertIn(first.split("-")[1], _COLOURS)

    def test_names_vary_independently_across_sessions(self):
        from chitty.actor import _COLOURS

        pairs = set()
        for number in range(500):
            name = self.resolve({"PI_SESSION_ID": f"session-{number}"})
            adjective, colour, _animal = name.split("-")
            self.assertIn(colour, _COLOURS)
            pairs.add((adjective, colour))
        self.assertGreater(len(pairs), 100)

    def test_chitty_pi_session_identity_takes_precedence_over_child_session(self):
        parent = self.resolve({"PI_SESSION_ID": "parent-session"})
        child = self.resolve(
            {"CHITTY_PI_SESSION_ID": "parent-session", "PI_SESSION_ID": "child-session"}
        )
        self.assertEqual(child, parent)

    def test_missing_identity_fails_loudly(self):
        with self.assertRaisesRegex(ChittyError, "cannot determine actor"):
            self.resolve({})
