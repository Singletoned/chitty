import re
import unittest
from collections.abc import Callable, Mapping

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from chitty.errors import ChittyError
from chitty.ids import TaskId, provisional_suffix
from chitty.model import SECTION_ORDER, Task, parse
from chitty.renumbering import plan_renumbering, replace_ids, rewrite_task
from tests.ticket_strategies import ticket_texts

PREFIX = st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=1, max_size=4)


def provisional_ids(prefix, seed, count):
    values = set()
    while len(values) < count:
        suffix = provisional_suffix(lambda bound: seed.randrange(bound))
        values.add(TaskId(prefix, suffix))
    return sorted(values)


class TestRenumberingProperties(unittest.TestCase):
    @given(
        prefix=PREFIX,
        used_numbers=st.sets(st.integers(1, 100), min_size=2).filter(
            lambda values: max(values) - min(values) + 1 > len(values)
        ),
        seed=st.randoms(),
    )
    def test_plan_allocates_sorted_ids_after_highest_used(self, prefix, used_numbers, seed):
        ids = provisional_ids(prefix, seed, 1 + seed.randrange(5))
        mapping = plan_renumbering({prefix: used_numbers}, ids)
        start = max(used_numbers) + 1
        self.assertEqual(
            mapping,
            {task_id: TaskId(prefix, start + index) for index, task_id in enumerate(ids)},
        )
        self.assertEqual(len(mapping), len(ids))
        self.assertTrue(all(new_id.number not in used_numbers for new_id in mapping.values()))

    @given(seed=st.randoms())
    def test_mixed_prefix_shuffled_ids_allocate_independently(self, seed):
        prefixes = ["A", "BC", "XYZ"]
        ids_by_prefix = {
            prefix: provisional_ids(prefix, seed, 1 + seed.randrange(4)) for prefix in prefixes
        }
        provisional = [task_id for ids in ids_by_prefix.values() for task_id in ids]
        seed.shuffle(provisional)
        used = {"A": {1, 5}, "BC": {2, 8, 11}, "UNUSED": {4}}

        mapping = plan_renumbering(used, provisional)

        expected = {}
        for prefix, ids in ids_by_prefix.items():
            number = max(used.get(prefix, set()), default=0) + 1
            expected.update(
                (task_id, TaskId(prefix, number + index))
                for index, task_id in enumerate(sorted(ids))
            )
        self.assertEqual(mapping, expected)
        self.assertEqual(len(mapping), len(provisional))
        self.assertTrue(
            all(new_id.number not in used.get(new_id.prefix, set()) for new_id in mapping.values())
        )

    @given(prefix=PREFIX, seed=st.randoms())
    def test_missing_prefix_starts_at_one(self, prefix, seed):
        ids = provisional_ids(prefix, seed, 1 + seed.randrange(4))
        self.assertEqual(
            list(plan_renumbering({}, ids).values()),
            [TaskId(prefix, number) for number in range(1, len(ids) + 1)],
        )

    @given(prefix=PREFIX, seed=st.randoms())
    @settings(deadline=None)
    def test_duplicate_and_numeric_ids_are_errors(self, prefix, seed):
        task_id = provisional_ids(prefix, seed, 1)[0]
        with self.assertRaisesRegex(ChittyError, str(task_id)):
            plan_renumbering({}, [task_id, task_id])
        with self.assertRaises(ChittyError):
            plan_renumbering({}, [TaskId(prefix, 1)])

    @given(
        seed=st.randoms(),
        filler=st.text(alphabet=" .,/()[]_\n", min_size=1, max_size=40),
    )
    def test_replace_mentions_only_at_specified_boundaries(self, seed, filler):
        prefixes = ["TASK", "NOTE", "BUG"]
        olds = [provisional_ids(prefix, seed, 1)[0] for prefix in prefixes]
        mapping = {old: TaskId(old.prefix, 123 + index) for index, old in enumerate(olds)}
        old = olds[0]
        new = mapping[old]
        old_text = str(old)
        # Build the oracle from explicitly selected occurrences, independent of regex.
        pieces = [
            (old_text, str(new)),
            (f"`{old_text}`", f"`{new}`"),
            (f"({old_text})", f"({new})"),
            (f"[{old_text}]", f"[{new}]"),
            (f'"{old_text}"', f'"{new}"'),
            (f"/{old_text}/", f"/{new}/"),
            (f"_{old_text}_", f"_{new}_"),
            (f"{old_text}--slug.md", f"{new}--slug.md"),
            (f"{old_text}-foo", f"{new}-foo"),
            (f"X{old_text}", f"X{old_text}"),
            (f"-{old_text}", f"-{old_text}"),
            (f"{old_text}Y", f"{old_text}Y"),
            (old_text.lower(), old_text.lower()),
            (
                f"{old.prefix}-{str(old).split('-', 1)[1].lower()}",
                f"{old.prefix}-{str(old).split('-', 1)[1].lower()}",
            ),
        ]
        for other in olds[1:]:
            other_text = str(other)
            other_new = str(mapping[other])
            pieces.append((other_text, other_new))
            pieces.append((f"`{other_text}`", f"`{other_new}`"))
        text = filler.join(source for source, _ in pieces)
        expected = filler.join(result for _, result in pieces)
        rewritten = replace_ids(text, mapping)
        self.assertEqual(rewritten, expected)
        self.assertEqual(replace_ids(rewritten, mapping), rewritten)

    @given(text=st.text(alphabet=" .,/()[]_\n", max_size=100))
    def test_text_without_id_is_unchanged(self, text):
        self.assertEqual(replace_ids(text, {TaskId("TASK", "K7Q2MX"): TaskId("TASK", 1)}), text)


Rewrite = Callable[[Task, Mapping[TaskId, TaskId]], Task]
IDS = [TaskId("TASK", 1), TaskId("TASK", 2)]


@st.composite
def rewrite_cases(draw):
    text = draw(ticket_texts(IDS))
    targets = [TaskId("TASK", 100), TaskId("TASK", 101)]
    for target in targets:
        assume(str(target) not in text)
    chain = draw(st.booleans())
    mapping = {IDS[0]: targets[0]}
    if chain:
        mapping[targets[0]] = targets[1]
    return parse(text), mapping


def section_bytes(task, name):
    match = re.search(rf"(?m)^## {re.escape(name)}\n.*?(?=^## |\Z)", task.render(), re.DOTALL)
    return match.group() if match else None


def criterion_bytes(task, index):
    section = section_bytes(task, "Acceptance Criteria")
    assert section is not None
    item = task.criteria[index]
    return "".join(section.splitlines(keepends=True)[item.start : item.end])


def property_fields(rewrite, task, mapping):
    result = rewrite(task, mapping)
    assert result.frontmatter.title == replace_ids(task.frontmatter.title, mapping)
    parent = task.frontmatter.parent
    assert result.frontmatter.parent == (replace_ids(parent, mapping) if parent else None)
    assert result.frontmatter.depends_on == [
        replace_ids(d, mapping) for d in task.frontmatter.depends_on
    ]
    for name in SECTION_ORDER:
        if name in ("History", "Acceptance Criteria"):
            continue
        text = task.section(name)
        assert result.section(name) == (replace_ids(text, mapping) if text is not None else None)
    assert len(result.criteria) == len(task.criteria)
    for before, after in zip(task.criteria, result.criteria, strict=True):
        assert after.text == replace_ids(before.text, mapping)
        assert after.checked == before.checked


def property_boundaries(rewrite, task, mapping):
    key = next(iter(mapping))
    new = mapping[key]
    text = f"{key}A X{key} X-{key} {key}-x TASK-2 `{key}` https://a/{key}"
    task = task.with_section("Description", text)
    result = rewrite(task, mapping)
    assert (
        result.section("Description")
        == f"{key}A X{key} X-{key} {new}-x TASK-2 `{new}` https://a/{new}"
    )


def property_preserved(rewrite, task, mapping):
    result = rewrite(task, mapping)
    assert section_bytes(result, "History") == section_bytes(task, "History")
    before = task.render().split("---\n", 2)[1]
    after = result.render().split("---\n", 2)[1]
    for field in ("labels", "owner", "moved_from", "priority", "status", "created", "provisional"):
        pattern = rf"(?m)^{field}:.*(?:\n|$)"
        assert re.findall(pattern, before) == re.findall(pattern, after)


def property_checks(rewrite, task, mapping):
    result = rewrite(task, mapping)
    assert [c.checked for c in result.criteria] == [c.checked for c in task.criteria]


def property_empty(rewrite, task, mapping):
    assert rewrite(task, {}).render() == task.render()


def property_formatting(rewrite, task, mapping):
    result = rewrite(task, mapping)
    for name in SECTION_ORDER:
        text = task.section(name)
        if text is not None and replace_ids(text, mapping) == text:
            assert section_bytes(result, name) == section_bytes(task, name)
    for index, item in enumerate(task.criteria):
        if replace_ids(item.text, mapping) == item.text:
            assert criterion_bytes(result, index) == criterion_bytes(task, index)


class TestRewriteProperties(unittest.TestCase):
    @given(rewrite_cases())
    @settings(deadline=None)
    def test_fields(self, case):
        property_fields(rewrite_task, *case)

    @given(rewrite_cases())
    @settings(deadline=None)
    def test_boundaries(self, case):
        property_boundaries(rewrite_task, *case)

    @given(rewrite_cases())
    @settings(deadline=None)
    def test_preserved(self, case):
        property_preserved(rewrite_task, *case)

    @given(rewrite_cases())
    @settings(deadline=None)
    def test_checks(self, case):
        property_checks(rewrite_task, *case)

    @given(rewrite_cases())
    @settings(deadline=None)
    def test_empty(self, case):
        property_empty(rewrite_task, *case)

    @given(rewrite_cases())
    @settings(deadline=None)
    def test_formatting(self, case):
        property_formatting(rewrite_task, *case)


if __name__ == "__main__":
    unittest.main()
