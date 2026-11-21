import tempfile
import unittest
from pathlib import Path

BUDGETS = {
    Path("src/chitty/guide.md"): 75,
    Path("src/chitty/roles/cold-read.md"): 460,
    Path("src/chitty/roles/plan.md"): 1340,
    Path("src/chitty/roles/property-signals.md"): 180,
    Path("src/chitty/roles/rebase.md"): 75,
    Path("src/chitty/roles/repair.md"): 175,
    Path("src/chitty/roles/review.md"): 900,
    Path("src/chitty/roles/setup.md"): 570,
    Path("src/chitty/roles/work.md"): 620,
}


def assert_guide_budgets(case: unittest.TestCase, root: Path, budgets: dict[Path, int]) -> None:
    guide = root / "src/chitty/guide.md"
    roles = root / "src/chitty/roles"
    discovered = {path.relative_to(root) for path in roles.glob("*.md") if path.is_file()}
    if guide.is_file():
        discovered.add(guide.relative_to(root))
    case.assertSetEqual(set(budgets), discovered, "Guide files and budgets differ")
    for path, limit in budgets.items():
        count = len((root / path).read_text(encoding="utf-8").split())
        case.assertLessEqual(count, limit, f"{path}: {count} words exceeds limit {limit}")


class TestGuideWordBudget(unittest.TestCase):
    def test_repository_guides(self):
        assert_guide_budgets(self, Path(__file__).resolve().parents[1], BUDGETS)

    def test_temporary_tree_boundaries_and_file_set(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            guide = Path("src/chitty/guide.md")
            role = Path("src/chitty/roles/example.md")
            extra = Path("src/chitty/roles/extra.md")
            budgets = {guide: 2, role: 1}
            (root / role).parent.mkdir(parents=True)
            (root / guide).write_text("one\ntwo", encoding="utf-8")
            (root / role).write_text("one", encoding="utf-8")
            assert_guide_budgets(self, root, budgets)

            (root / guide).write_text("one\ntwo\tthree", encoding="utf-8")
            with self.assertRaisesRegex(
                AssertionError, r"src/chitty/guide\.md: 3 words exceeds limit 2"
            ):
                assert_guide_budgets(self, root, budgets)
            (root / guide).write_text("one two", encoding="utf-8")

            (root / role).unlink()
            with self.assertRaisesRegex(AssertionError, "example.md"):
                assert_guide_budgets(self, root, budgets)
            (root / role).write_text("one", encoding="utf-8")

            (root / extra).write_text("one", encoding="utf-8")
            with self.assertRaisesRegex(AssertionError, "extra.md"):
                assert_guide_budgets(self, root, budgets)
