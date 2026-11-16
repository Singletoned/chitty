import unittest

from chitty.store import _add_missing_settings


class TestPiRetirement(unittest.TestCase):
    def test_generated_agent_command_uses_prompt_without_extension_flags(self):
        generated = _add_missing_settings("", {}, False, "demo")
        self.assertIn('agent_command = "pi -p {prompt}"', generated)
        self.assertNotIn("--no-extensions", generated)
        self.assertNotIn("chitty.ts", generated)
