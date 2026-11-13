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

    def test_planning_guide_specifies_properties(self):
        planning = _flat(self.run_guide("plan"))
        signals = _flat((ROLES / "property-signals.md").read_text())
        expected = _flat(
            """- Specify property tests by default. Compare each decision in the description
            with the criteria, because workers test what criteria name. For each
            behaviour, write the property and what the test generates: the inputs and
            the state the behaviour depends on, such as files present, branches and
            config. For example, "for any criteria list and valid N, only criterion N
            changes", or "for any set of directories, each on disk, only on another
            branch, or both, `show` finds every ticket".
            - Name the repository's property-testing tool. Generated means many inputs
            drawn by that tool, not a few hand-picked cases. If the repository has no
            such tool, say whether the ticket adds one.
            - When a behaviour has no property, give the reason in one line. Valid
            reasons: fixed text with no input, such as a docs-only change; a small fixed
            set, with every member listed in the ticket and each one tested; or
            behaviour that needs real external processes, with why no pure core can be
            taken out of it and given properties.
            - Say which test must fail without the fix, because a nearby test may already
            pass."""
        )
        pure_function = _flat(
            """- Where behaviour can be a pure function, taking values and returning values
            with no file, network or clock access inside it, have the ticket name that
            function and state its properties: it is far easier to test. A function,
            module or internal API (such as a facade) the ticket names is an internal
            surface and part of its spec, so its tests may call it directly."""
        )
        self.assertIn(f"{expected} {signals} {pure_function}", planning)
        self.assertNotIn(
            "Compare each decision in the description with the criteria, because "
            "workers test what criteria name. Say which",
            planning,
        )
        self.assertNotIn("<!-- property-signals -->", planning)

    def test_cold_read_guide_reports_missed_properties(self):
        cold_read = _flat(self.run_guide("cold-read", "TASK-1"))
        signals = _flat((ROLES / "property-signals.md").read_text())
        self.assertIn(signals, cold_read)
        self.assertIn(
            _flat("""- Missed properties: behaviour tested only by example where a signal above
            fits, state the tests never vary (files present, branches, config), a reason
            for having no property that does not hold, and logic that could be a pure
            function but is not specified as one. Give each property and what to
            generate, or `none`."""),
            cold_read,
        )
        self.assertNotIn("<!-- property-signals -->", cold_read)

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
