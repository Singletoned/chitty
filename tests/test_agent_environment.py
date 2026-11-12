import os
import unittest

AGENT_PREFIXES = ("PI_", "CLAUDE_", "CODEX_", "CHITTY_")


class TestAgentEnvironment(unittest.TestCase):
    def test_no_agent_variables_inherited(self):
        leaked = sorted(k for k in os.environ if k.startswith(AGENT_PREFIXES))
        self.assertEqual(leaked, [])


if __name__ == "__main__":
    unittest.main()
