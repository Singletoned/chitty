import re
import unittest
from importlib.resources import files
from pathlib import Path

from chitty.store import ROLE_NAMES, guide

TICKET_ID = re.compile(r"TASK-[0-9]")


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestPlanGuideRestored(unittest.TestCase):
    def test_restores_advice_outside_the_read_only_change(self):
        planning = _flat(guide("plan", directory=Path.cwd(), workflow="runner"))
        for phrase in (
            "Err on the side of splitting",
            "`chitty check` warns above five criteria; split larger work.",
            "Use its optional `parent` field to group flat IDs.",
            "Ask whether odd existing behaviour is a bug before writing around it.",
            "Write requirements needed to reject the implementation into the ticket",
            "Give the outcomes in your reply, not in a ticket note.",
            "that depends on this one",
            (
                "`chitty edit -s todo` lists the tickets a ticket mentions: "
                "check that its claims about them still hold."
            ),
            "it is not your planning step",
            "to process completed tickets in one batch",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, planning)

    def test_drops_wording_the_read_only_change_added(self):
        planning = _flat(guide("plan", directory=Path.cwd(), workflow="runner"))
        for phrase in (
            "Keep the reader's starting point",
            "cannot be verified together",
            "reject the finding into the ticket",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, planning)


class TestGuidesStayGeneral(unittest.TestCase):
    def test_no_guide_names_a_ticket(self):
        texts = {role: guide(role, directory=Path.cwd(), workflow="runner") for role in ROLE_NAMES}
        for path in files("chitty").iterdir():
            if path.name.startswith("guide") and path.name.endswith(".md"):
                texts[path.name] = path.read_text()
        for name, text in texts.items():
            with self.subTest(guide=name):
                self.assertIsNone(TICKET_ID.search(text))

    def test_cold_read_guide_addresses_only_the_reader(self):
        cold_read = _flat(guide("cold-read", directory=Path.cwd(), workflow="runner"))
        for phrase in (
            "Use these report headings exactly",
            "expected route",
            "Every ticket gets one read-only cold read",
        ):
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, cold_read)


if __name__ == "__main__":
    unittest.main()
