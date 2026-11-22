import os
import subprocess
import sys
import unittest
from pathlib import Path

import hypothesis

ROOT = Path(__file__).resolve().parents[1]
PROBE = """
import tests
from hypothesis import given, settings, strategies as st

seen = []

@settings(database=None, max_examples=20)
@given(st.integers())
def probe(x):
    seen.append(x)

probe()
print(seen)
"""


class TestHypothesisProfile(unittest.TestCase):
    def test_deadline_is_disabled(self):
        self.assertIsNone(hypothesis.settings().deadline)

    def run_probe(self, tier, code, ci=False):
        env = os.environ.copy()
        env.pop("TEST_TIER", None)
        # Hypothesis loads its own `ci` profile when `CI` is set (as on GitHub
        # Actions); the tiers must behave the same either way.
        env.pop("CI", None)
        if ci:
            env["CI"] = "true"
        if tier is not None:
            env["TEST_TIER"] = tier
        return subprocess.run(
            [sys.executable, "-c", code],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_examples_and_database(self):
        for ci in (False, True):
            for tier in (None, "check", "thorough"):
                with self.subTest(tier=tier, ci=ci):
                    self.check_tier(tier, ci)

    def check_tier(self, tier, ci):
        runs = [self.run_probe(tier, PROBE, ci) for _ in range(2)]
        for run in runs:
            self.assertEqual(run.returncode, 0, run.stderr)
        if tier == "thorough":
            self.assertNotEqual(runs[0].stdout, runs[1].stdout)
        else:
            self.assertEqual(runs[0].stdout, runs[1].stdout)
        database = self.run_probe(
            tier,
            "import tests; from hypothesis import settings; "
            "print(settings.default.database is None)",
            ci,
        )
        self.assertEqual(database.returncode, 0, database.stderr)
        self.assertEqual(database.stdout.strip(), str(tier != "thorough"))

    def test_unknown_tier_fails(self):
        result = self.run_probe("nope", "import tests")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("InvalidArgument", result.stderr)
        self.assertIn("nope", result.stderr)


if __name__ == "__main__":
    unittest.main()
