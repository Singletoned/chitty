import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import get_args

from chitty.model import SECTION_ORDER, SectionName, TaskError, section_name

ROOT = Path(__file__).resolve().parents[1]


class SectionNameTypesTest(unittest.TestCase):
    def check_literal(self, name: str) -> subprocess.CompletedProcess[str]:
        tmp = ROOT / "tmp"
        tmp.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(dir=tmp) as directory:
            source = Path(directory) / "example.py"
            source.write_text(
                f'from chitty.model import parse\nparse("example").with_section({name!r}, "x")\n'
            )
            return subprocess.run(
                [str(ROOT / ".venv/bin/pyright"), str(source)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
            )

    def test_bogus_literal_is_rejected(self) -> None:
        result = self.check_literal("Bogus")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Bogus", result.stdout + result.stderr)

    def test_notes_literal_is_accepted(self) -> None:
        result = self.check_literal("Notes")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_section_name_validation(self) -> None:
        for name in SECTION_ORDER:
            with self.subTest(name=name):
                self.assertEqual(section_name(name), name)
        for name in ("Bogus", "notes", "Notes "):
            with (
                self.subTest(name=name),
                self.assertRaisesRegex(TaskError, f"^unknown section: {name}$"),
            ):
                section_name(name)

    def test_literal_matches_section_order(self) -> None:
        self.assertEqual(set(get_args(SectionName)), set(SECTION_ORDER))
