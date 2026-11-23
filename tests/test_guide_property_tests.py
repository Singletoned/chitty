import re
import unittest
from pathlib import Path

from click.testing import CliRunner

from chitty.cli import cli

ROOT = Path(__file__).parents[1]
ROLES = ROOT / "src" / "chitty" / "roles"


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestPropertyTestGuides(unittest.TestCase):
    def run_guide(self, *args: str) -> str:
        result = CliRunner().invoke(cli, ["guide", *args], catch_exceptions=False)
        self.assertEqual(result.exit_code, 0, result.output)
        return result.stdout

    def test_property_signals_are_shared_and_guides_are_language_agnostic(self):
        role_files = list(ROLES.glob("*.md"))
        contents = {path.name: path.read_text() for path in role_files}
        sources = [name for name, text in contents.items() if "These signal a property" in text]
        self.assertEqual(sources, ["property-signals.md"])
        self.assertIn("<!-- property-signals -->", contents["plan.md"].splitlines())
        self.assertIn("<!-- property-signals -->", contents["cold-read.md"].splitlines())
        for name, text in contents.items():
            with self.subTest(role=name):
                self.assertIsNone(
                    re.search(
                        r"python|pytest|unittest|quickcheck|fast-check|jest", text, re.IGNORECASE
                    )
                )


if __name__ == "__main__":
    unittest.main()
