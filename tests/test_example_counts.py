import ast
import os
import subprocess
import sys
import unittest
from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from tests import CHECK_EXAMPLE_DIVISOR, THOROUGH_EXAMPLE_FACTOR, example_count, examples

ROOT = Path(__file__).resolve().parent.parent


class TestExampleCounts(unittest.TestCase):
    @given(st.integers(1, 100000))
    @settings(max_examples=examples(100))
    def test_counts(self, base):
        self.assertEqual(example_count("check", base), max(1, base // CHECK_EXAMPLE_DIVISOR))
        self.assertEqual(example_count("thorough", base), base * THOROUGH_EXAMPLE_FACTOR)

    @given(st.text().filter(lambda t: t not in {"check", "thorough"}))
    @settings(max_examples=examples(100))
    def test_unknown_profile(self, profile):
        with self.assertRaises(ValueError) as error:
            example_count(profile, 1)
        self.assertIn(repr(profile), str(error.exception))

    def test_decorators_use_examples(self):
        violations = []
        for path in (ROOT / "tests").rglob("*.py"):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                for decorator in getattr(node, "decorator_list", []):
                    if not (
                        isinstance(decorator, ast.Call)
                        and isinstance(decorator.func, ast.Name)
                        and decorator.func.id == "settings"
                    ):
                        continue
                    for keyword in decorator.keywords:
                        if keyword.arg == "max_examples" and not (
                            isinstance(keyword.value, ast.Call)
                            and isinstance(keyword.value.func, ast.Name)
                            and keyword.value.func.id == "examples"
                        ):
                            violations.append(f"{path.relative_to(ROOT)}:{decorator.lineno}")
        self.assertEqual(violations, [])

    def test_profiles_in_subprocess(self):
        for tier, expected in (("check", "20 5"), ("thorough", "500 125")):
            with self.subTest(tier=tier):
                result = subprocess.run(
                    [
                        sys.executable,
                        "-c",
                        (
                            "import tests; from hypothesis import settings; "
                            "print(settings.default.max_examples, tests.examples(25))"
                        ),
                    ],
                    cwd=ROOT,
                    env={**os.environ, "TEST_TIER": tier},
                    capture_output=True,
                    text=True,
                    check=True,
                )
                self.assertEqual(result.stdout.strip(), expected)
