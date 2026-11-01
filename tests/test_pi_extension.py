import tempfile
import unittest
from pathlib import Path

from chitty.actor import install_pi_extension
from chitty.errors import ChittyError


class TestPiExtension(unittest.TestCase):
    def test_installs_only_when_pi_exists_and_extension_is_uninstalled(self):
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            environment = {"HOME": str(home)}
            self.assertIsNone(install_pi_extension(environment))

            agent = home / ".pi" / "agent"
            agent.mkdir(parents=True)
            installed = install_pi_extension(environment)
            assert installed is not None
            self.assertTrue(installed.exists())
            self.assertIsNone(install_pi_extension(environment))

            installed.write_text("local edits")
            with self.assertRaisesRegex(ChittyError, "may contain local edits"):
                install_pi_extension(environment)

    def test_installs_into_configured_pi_agent_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            agent = Path(temporary) / "custom-agent"
            agent.mkdir()

            installed = install_pi_extension({"PI_CODING_AGENT_DIR": str(agent), "HOME": temporary})

            self.assertEqual(installed, agent / "extensions" / "chitty.ts")
            assert installed is not None
            self.assertTrue(installed.exists())
