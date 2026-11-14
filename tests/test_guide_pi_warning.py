import unittest

from click.testing import CliRunner
from hypothesis import given
from hypothesis import strategies as st

from chitty.actor import pi_session_environment_missing
from chitty.cli import cli

_NONEMPTY = st.text(min_size=1).filter(lambda value: bool(value.strip()))
_WHITESPACE = st.text(alphabet=st.sampled_from((" ", "\t", "\n", "\r", "\v", "\f")), min_size=1)
_IDENTITY_VARIABLES = st.sampled_from(("PI_SESSION_ID", "CHITTY_PI_SESSION_ID", "CHITTY_ACTOR"))


class TestGuidePiWarning(unittest.TestCase):
    def guide(self, env: dict[str, str | None]) -> str:
        result = CliRunner().invoke(cli, ["guide"], env=env, catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return result.stdout

    def test_pi_without_identity_is_warned(self):
        output = self.guide({"PI_CODING_AGENT": "true"})
        self.assertIn("no session identity", output)
        self.assertIn("CHITTY_ACTOR", output)
        self.assertNotIn("extension", output.lower())

    @given(_NONEMPTY)
    def test_native_pi_identity_is_not_missing(self, identity: str):
        self.assertFalse(
            pi_session_environment_missing({"PI_CODING_AGENT": "true", "PI_SESSION_ID": identity})
        )

    @given(_IDENTITY_VARIABLES, _NONEMPTY)
    def test_nonempty_identities_are_not_missing_in_pi(self, variable: str, identity: str):
        self.assertFalse(
            pi_session_environment_missing({"PI_CODING_AGENT": "true", variable: identity})
        )

    @given(_IDENTITY_VARIABLES, _WHITESPACE)
    def test_whitespace_identities_are_missing_in_pi(self, variable: str, identity: str):
        self.assertTrue(
            pi_session_environment_missing({"PI_CODING_AGENT": "true", variable: identity})
        )

    @given(_IDENTITY_VARIABLES, _NONEMPTY)
    def test_non_pi_identities_never_warn(self, variable: str, identity: str):
        self.assertFalse(pi_session_environment_missing({variable: identity}))

    @given(_IDENTITY_VARIABLES, _WHITESPACE)
    def test_non_pi_whitespace_identities_never_warn(self, variable: str, identity: str):
        self.assertFalse(pi_session_environment_missing({variable: identity}))

    def test_non_pi_without_identity_never_warns(self):
        self.assertFalse(pi_session_environment_missing({}))


if __name__ == "__main__":
    unittest.main()
