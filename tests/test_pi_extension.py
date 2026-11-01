import hashlib
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
            self.assertTrue((agent / "chitty-extension.sha256").exists())
            self.assertIsNone(install_pi_extension(environment))

            installed.write_text("local edits")
            with self.assertRaisesRegex(ChittyError, "may contain local edits"):
                install_pi_extension(environment)

    def test_replaces_an_unedited_extension_from_a_previous_installation(self):
        with tempfile.TemporaryDirectory() as temporary:
            agent = Path(temporary) / "agent"
            extensions = agent / "extensions"
            extensions.mkdir(parents=True)
            installed = extensions / "chitty.ts"
            previous_source = b"previous Chitty extension"
            installed.write_bytes(previous_source)
            (agent / "chitty-extension.sha256").write_text(
                hashlib.sha256(previous_source).hexdigest() + "\n"
            )

            updated = install_pi_extension({"PI_CODING_AGENT_DIR": str(agent)})

            self.assertEqual(updated, installed)
            self.assertNotEqual(installed.read_bytes(), previous_source)

    def test_installs_into_configured_pi_agent_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            agent = Path(temporary) / "custom-agent"
            agent.mkdir()

            installed = install_pi_extension({"PI_CODING_AGENT_DIR": str(agent), "HOME": temporary})

            self.assertEqual(installed, agent / "extensions" / "chitty.ts")
            assert installed is not None
            self.assertTrue(installed.exists())
