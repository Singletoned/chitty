import textwrap
import unittest
from datetime import date

from chitty.model import TaskError, new_task, parse, render_scalar


def doc(text: str) -> str:
    return textwrap.dedent(text).lstrip("\n")


SAMPLE = doc(
    """
    ---
    title: Add search to the task list
    status: todo
    # a comment the tool must keep
    labels: [search, cli]
    priority: medium
    owner: 'ed'
    depends_on:
      - TASK-7
      - HUMAN-1
    created: 2026-10-23
    ---

    ## Description

    Free markdown.

    ```
    ## not a heading
    ```

    ## Acceptance Criteria

    - [ ] `chitty list --search` matches title and body, and this criterion
          wraps onto a second line
    - [x] Matching is case-insensitive

    - [X] Loose item

    ## Notes

    First note.
    """
)


class TestParse(unittest.TestCase):
    def test_parses_sample(self):
        task = parse(SAMPLE)
        fm = task.frontmatter
        self.assertEqual(fm.title, "Add search to the task list")
        self.assertEqual(fm.labels, ["search", "cli"])
        self.assertEqual(fm.owner, "ed")
        self.assertEqual(fm.depends_on, ["TASK-7", "HUMAN-1"])
        self.assertEqual(fm.created, date(2026, 10, 23))
        self.assertEqual([c.checked for c in task.criteria], [False, True, True])
        self.assertEqual(
            task.criteria[0].text,
            "`chitty list --search` matches title and body, and this criterion "
            "wraps onto a second line",
        )
        self.assertIn("## not a heading", task.section("Description") or "")
        self.assertEqual(task.section("Notes"), "First note.")
        self.assertIsNone(task.section("Plan"))
        self.assertEqual(task.render(), SAMPLE)

    def test_scalars_are_strings(self):
        task = parse(SAMPLE.replace("owner: 'ed'", "owner: no"))
        self.assertEqual(task.frontmatter.owner, "no")
        with self.assertRaisesRegex(TaskError, "status"):
            parse(SAMPLE.replace("status: todo", "status: on"))

    def test_rejections(self):
        cases = {
            "unknown frontmatter key 'colour'": SAMPLE.replace(
                "status: todo", "status: todo\ncolour: red"
            ),
            "'title' is required": SAMPLE.replace("title: Add search to the task list\n", ""),
            "duplicate frontmatter key": SAMPLE.replace(
                "status: todo", "status: todo\nstatus: done"
            ),
            "not an ISO 8601 date": SAMPLE.replace("2026-10-23", "23/10/2026"),
            "not a task ID": SAMPLE.replace("TASK-7", "task 7"),
            "unknown section 'Design'": SAMPLE.replace("## Notes", "## Design"),
            "'#' headings": SAMPLE.replace("## Notes", "# Notes"),
            "duplicate section": SAMPLE + "\n## Notes\n\nAgain.\n",
            "before the first": SAMPLE.replace(
                "---\n\n## Description", "---\nHello\n## Description"
            ),
            "Description' section is required": SAMPLE.replace("## Description", "## Plan"),
            "must not be empty": SAMPLE.replace("Free markdown.", "").replace(
                "```\n## not a heading\n```", ""
            ),
            "nested lists": SAMPLE.replace("      wraps onto", "  - wraps onto"),
            "may only contain": SAMPLE.replace("- [x] Matching", "Matching"),
            "has no text": SAMPLE.replace("- [x] Matching is case-insensitive", "- [x]"),
            "start with '---'": "title: x\n",
            "not closed": "---\ntitle: x\n",
            "end with a newline": SAMPLE.rstrip("\n"),
            "CR line endings": SAMPLE.replace("\n", "\r\n"),
            "single line": SAMPLE.replace(
                "title: Add search to the task list", 'title: "two\\nlines"'
            ),
        }
        for reason, text in cases.items():
            with self.subTest(reason=reason), self.assertRaisesRegex(TaskError, reason):
                parse(text)


class TestFieldEdits(unittest.TestCase):
    def test_changing_one_key_leaves_everything_else(self):
        task = parse(SAMPLE).with_field("status", "doing")
        self.assertEqual(task.render(), SAMPLE.replace("status: todo", "status: doing"))

    def test_changing_flow_list_rewrites_it_block_style(self):
        task = parse(SAMPLE).with_field("labels", ["search"])
        self.assertIn(
            "# a comment the tool must keep\nlabels:\n  - search\npriority", task.render()
        )

    def test_new_key_goes_in_table_order(self):
        text = SAMPLE.replace("priority: medium\n", "")
        task = parse(text).with_field("priority", "high")
        self.assertEqual(task.render(), SAMPLE.replace("priority: medium", "priority: high"))

    def test_removing_a_key(self):
        task = parse(SAMPLE).with_field("depends_on", [])
        self.assertNotIn("depends_on", task.render())
        self.assertNotIn("HUMAN-1", task.render())

    def test_invalid_value_is_rejected(self):
        with self.assertRaisesRegex(TaskError, "status"):
            parse(SAMPLE).with_field("status", "blocked")

    def test_quoting(self):
        for value in (
            "no",
            "yes",
            "on",
            "Y",
            "null",
            "~",
            "12",
            "1e3",
            "0x1F",
            ".inf",
            "2026-10-23",
            "true",
            "- dash",
            "a: b",
            "#tag",
            "",
            " padded",
        ):
            with self.subTest(value=value):
                self.assertNotEqual(render_scalar(value), value)
        for value in ("ed", "Add search", "claude-code", "v1.2.3", "it's"):
            with self.subTest(value=value):
                self.assertEqual(render_scalar(value), value)
        self.assertEqual(render_scalar('"quoted" title'), "'\"quoted\" title'")

    def test_quoted_values_round_trip(self):
        task = parse(SAMPLE)
        for value in ("no", "2026-10-23", "1e3", '"quoted" title', 'it\'s "both"', "a\\b"):
            with self.subTest(value=value):
                self.assertEqual(task.with_field("title", value).frontmatter.title, value)


class TestSectionEdits(unittest.TestCase):
    def test_replace_description(self):
        task = parse(SAMPLE).with_section("Description", "New text.\n\nTwo paragraphs.\n")
        self.assertEqual(task.section("Description"), "New text.\n\nTwo paragraphs.")
        self.assertIn("Two paragraphs.\n\n## Acceptance Criteria\n", task.render())

    def test_plan_is_inserted_in_order(self):
        task = parse(SAMPLE).with_section("Plan", "Do it.")
        self.assertIn("Loose item\n\n## Plan\n\nDo it.\n\n## Notes\n", task.render())

    def test_section_appended_at_end(self):
        text = SAMPLE.split("## Notes")[0].rstrip("\n") + "\n"
        task = parse(text).with_note("Hello")
        self.assertTrue(task.render().endswith("Loose item\n\n## Notes\n\nHello\n"))

    def test_remove_section(self):
        task = parse(SAMPLE).with_section("Notes", "")
        self.assertTrue(task.render().endswith("- [X] Loose item\n"))

    def test_heading_in_text_is_rejected(self):
        with self.assertRaisesRegex(TaskError, "unknown section"):
            parse(SAMPLE).with_section("Plan", "## Steps\n\nfoo")

    def test_append_note(self):
        task = parse(SAMPLE).with_note("Second note.")
        self.assertTrue(task.render().endswith("First note.\n\nSecond note.\n"))


class TestCriteriaEdits(unittest.TestCase):
    def edit(self, text, add=(), remove=(), check=(), uncheck=()):
        return parse(text).with_criteria(add=add, remove=remove, check=check, uncheck=uncheck)

    def test_check_changes_only_the_bracket(self):
        task = self.edit(SAMPLE, check=[1], uncheck=[2])
        expected = SAMPLE.replace("- [ ] `chitty", "- [x] `chitty").replace(
            "- [x] Matching", "- [ ] Matching"
        )
        self.assertEqual(task.render(), expected)
        self.assertEqual(len(task.criteria), 3)

    def test_remove_wrapped_item(self):
        task = self.edit(SAMPLE, remove=[1])
        self.assertIn("## Acceptance Criteria\n\n- [x] Matching", task.render())
        self.assertEqual(len(task.criteria), 2)

    def test_remove_last_item_drops_gap(self):
        task = self.edit(SAMPLE, remove=[3])
        self.assertIn("- [x] Matching is case-insensitive\n\n## Notes", task.render())

    def test_indices_refer_to_original_list(self):
        task = self.edit(SAMPLE, remove=[1], check=[2], uncheck=[3], add=["New"])
        self.assertEqual(
            [(c.checked, c.text) for c in task.criteria],
            [(True, "Matching is case-insensitive"), (False, "Loose item"), (False, "New")],
        )

    def test_add_creates_section(self):
        text = SAMPLE.replace(SAMPLE[SAMPLE.index("## Acceptance") : SAMPLE.index("## Notes")], "")
        task = self.edit(text, add=["One", "Two"])
        self.assertIn(
            "```\n\n## Acceptance Criteria\n\n- [ ] One\n- [ ] Two\n\n## Notes", task.render()
        )

    def test_removing_all_removes_section(self):
        task = self.edit(SAMPLE, remove=[1, 2, 3])
        self.assertNotIn("Acceptance", task.render())
        self.assertIn("```\n\n## Notes", task.render())

    def test_errors(self):
        with self.assertRaisesRegex(TaskError, "there are 3"):
            self.edit(SAMPLE, check=[4])
        with self.assertRaisesRegex(TaskError, "both"):
            self.edit(SAMPLE, check=[1], remove=[1])
        with self.assertRaisesRegex(TaskError, "single line"):
            self.edit(SAMPLE, add=["a\nb"])


class TestNewTask(unittest.TestCase):
    def test_new_task(self):
        task = new_task(
            title="no",
            created=date(2026, 10, 23),
            description="Describe it.",
            criteria=["First"],
            fields={"labels": ["cli"], "depends_on": ["TASK-1"], "priority": None},
        )
        self.assertEqual(
            task.render(),
            doc(
                """
                ---
                title: "no"
                status: todo
                labels:
                  - cli
                depends_on:
                  - TASK-1
                created: 2026-10-23
                ---

                ## Description

                Describe it.

                ## Acceptance Criteria

                - [ ] First
                """
            ),
        )
