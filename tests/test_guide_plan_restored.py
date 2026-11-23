import re
import unittest
from importlib.resources import files
from pathlib import Path

from chitty.store import ROLE_NAMES, guide

TICKET_ID = re.compile(r"TASK-[0-9]")


def _flat(text: str) -> str:
    return " ".join(text.split())


class TestGuidesStayGeneral(unittest.TestCase):
    def test_no_guide_names_a_ticket(self):
        texts = {role: guide(role, directory=Path.cwd(), workflow="runner") for role in ROLE_NAMES}
        for path in files("chitty").iterdir():
            if path.name.startswith("guide") and path.name.endswith(".md"):
                texts[path.name] = path.read_text()
        for name, text in texts.items():
            with self.subTest(guide=name):
                self.assertIsNone(TICKET_ID.search(text))


if __name__ == "__main__":
    unittest.main()
