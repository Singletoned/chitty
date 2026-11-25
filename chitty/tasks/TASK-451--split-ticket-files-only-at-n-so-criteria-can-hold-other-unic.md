---
title: Split ticket files only at \n, so criteria can hold other Unicode line separators
status: planning
labels:
  - bug
priority: medium
created: 2026-11-19
---

## Description

A criterion is refused when it holds a character that only Python treats as a line break. On 2026-11-23, `chitty edit TASK-610 --set-ac 1 ...` was refused with `acceptance criterion must be a single line` because the text held U+2028 LINE SEPARATOR; finding it took guesswork (TASK-638).

Cause, in `src/chitty/model.py`:

- `parse` splits the file with `text.splitlines(keepends=True)`. `str.splitlines` breaks on `\n`, `\r`, `\x0b`, `\x0c`, `\x1c`, `\x1d`, `\x1e`, `\x85`, `\u2028` and `\u2029`. Markdown (CommonMark) ends lines only at `\n` and `\r`, and `parse` already refuses `\r`. So a criterion `- [ ] a\u2028b` is refused by `parse` with `may only contain '- [ ] ...' items`, because the text after the break is not indented; an indented one is read as a continuation line and joined with a space.
- To avoid that, `_criterion_text` refuses any text in which `splitlines` finds a break, including at either end (it adds a sentinel character to each end before splitting), before it strips the text.

Decisions:

- Make the parser accept these characters, rather than refusing them in the criterion text. In `parse`, split lines only at `\n`, keeping the line endings, and leave the rest of `parse` unchanged. Other sections already round-trip byte for byte, because `render` joins the lines back together.
- In `_criterion_text`, strip the text first, then refuse it only if the stripped text still contains `\n` or `\r` (`parse` refuses any `\r` in a file, so a stored `\r` would make the ticket unreadable). The message stays `acceptance criterion must be a single line`. Update the `with_criteria` docstring, which says replacement text must contain no line breaks even at the ends. As a result, `a\u2028b` and `a\x1db` are stored as given, and `a\n` and `a\u2028` are stored as `a`, because `str.strip` removes surrounding whitespace, and Python counts these characters as whitespace.
- Decided 2026-11-23, following the person's standing rule (make tools robust to unusual input, such as a criterion that looks like a checkbox): text that starts with `[x]` or `[ ]` is stored as text, as it is today. Nothing in this ticket refuses it. That reverses the checkbox rejection in this ticket's earlier version.
- Frontmatter: after the change, `parse` no longer splits frontmatter at `\x85`, and PyYAML folds a raw `\x85` inside a scalar into a space, so a title `a\x85b` would silently be read back as `a b` (checked on a trial patch, 2026-11-24). Today such a title makes the file unreadable. Fix it in `render_scalar`: before its other quoting rules, if the value contains `\x85`, return `json.dumps(value, ensure_ascii=False).replace("\x85", "\\u0085")`, a double-quoted YAML scalar whose `\u0085` escape reads back as the character. `\u2028` and `\u2029` already read back unchanged after the change, so they need nothing.
- Headings: a line such as `x\u2028## Plan` in a section is one line after the change, so its `## Plan` is not a heading. That matches CommonMark and is intended.
- Out of scope: the History parsing in `transitions` and `timed_transitions`, which uses `str.splitlines` on History text that Chitty writes itself; `_text_lines`, which right-strips section lines; and `src/chitty/check.py`, which already splits on `\n`.

Tests go in a new file, `tests/test_criteria_line_breaks.py`:

- Property, with Hypothesis and `examples(50)` from `tests/__init__.py`. Draw a ticket with criteria using `ticket_texts([TaskId("TASK", 1)])` from `tests/ticket_strategies.py`, filtered as `tests/test_property_criterion_text.py` does. Draw an index and a text: `st.text()` with `\n` and `\r` excluded, mixed through `st.one_of` with drawn text that has one of the other `splitlines` characters above inserted at a drawn position, and filtered so the stripped text is non-empty. Build `parse(task.with_criteria(add=[], remove=[], set_criteria=[(index, text)], check=[], uncheck=[]).render())`. Assert that criterion `index` has text equal to `text.strip()` and is unticked, and that every other criterion keeps its text and its tick. Assert the same for `add=[text]`, where the appended last criterion has that text.
- Existing test: `test_new_criterion_rejects_all_line_breaks` in `tests/test_model.py` asserts that every `splitlines` character is refused; narrow it to `\n` and `\r` (the trial patch showed it is the only existing test the change breaks). `tests/test_cli.py` refusing a suggestion titled `\u2028` is unaffected: `_check_single_line` refuses it as empty after stripping.
- Examples: for each break character in the list above other than `\n` and `\r`, `set_criteria` with `f"a{c}b"` round-trips as that exact text; `f"a{c}"` round-trips as `a`; `a\nb` and `a\rb` each raise `TaskError` with the message `acceptance criterion must be a single line`; `a\n` is stored as `a`; `[x] a` round-trips as the text `[x] a`, unticked.
- Parse example: a ticket file whose Acceptance Criteria section holds `- [ ] a\u2028b\n` parses to one criterion with text `a\u2028b`, and `render` returns the input byte for byte.
- Renumbering-caller example, in the same new file: for `text` in `a\u2028b` and `a\x1db`, `parse(parse(SAMPLE).with_criterion_text(1, text).render()).criteria[0].text == text`, with `SAMPLE` imported from `tests/test_model.py`.
- Frontmatter example, with `subTest` for each of `\x85`, `\u2028` and `\u2029` as `c`: `parse(task.with_field("title", f"a{c}b").render()).frontmatter.title == f"a{c}b"`, where `task = parse(SAMPLE)`. For `\x85`, the rendered title line is also `title: "a\u0085b"`, with the six characters backslash, `u`, `0`, `0`, `8`, `5` between the quotes, not the raw character. All three fail on `main`, where the file cannot be read back.
- CLI test, in a class that inherits `CliTestCase` from `tests/test_cli.py`: `run_cli("add", "T", "-d", "x", "--ac", "one")`, then `run_cli("edit", "TASK-1", "--set-ac", "1", "a\u2028b")` exits 0, and `show TASK-1 --json` gives criterion text `a\u2028b`.

Put the `a\nb` and `a\rb` refusals and the `[x] a` example in a class `TestUnchangedBehaviour`, and every other new test in a class `TestBreaksAccepted`. Write each kind of example as its own test method, using `subTest` for each character, so a run shows which kinds pass. Run every test against `main` before the change and record the results in a note. Expected on `main`: the property, the parse example, the renumbering-caller example, the frontmatter example, the CLI test and the `a{c}b`, `a{c}` and `a\n` examples fail; the `a\nb` and `a\rb` refusals and the `[x] a` example pass, because they pin behaviour this ticket keeps. After the change, all pass.

## Acceptance Criteria

- [ ] The tests in `tests/test_criteria_line_breaks.py` pass. A note records a run of that file against `main`: every test in `TestBreaksAccepted` fails there, and every test in `TestUnchangedBehaviour` passes there, because those pin behaviour this ticket keeps; `test_new_criterion_rejects_all_line_breaks` is narrowed to `\n` and `\r`
- [ ] `tests/test_property_criterion_text.py` and the other existing tests still pass; `make check` passes
- [ ] The renumbering-caller example (`with_criterion_text` with `a\u2028b` and `a\x1db`) passes and fails against `main`; `tests/test_property_renumbering.py` passes
- [ ] The frontmatter example passes (a title `a\x85b` reads back unchanged, written as `"a\u0085b"`) and fails against `main`

## Plan

Run the specified regression tests against main and record baseline results. Add focused tests, update LF-only parsing and criterion validation/docstring, and preserve NEL YAML round-tripping. Run targeted tests and make check, then commit implementation and tests and hand off to review.

## Notes

Suggestion origin: chitty

Planner, 2026-11-24: current state. Every earlier planning blocker is resolved, and the notes that raised them were removed to stop them being re-raised (they are in Git history). In particular, `[x] a` and the `\n`/`\r` refusals are expected to pass on `main`: they are in `TestUnchangedBehaviour`, and criterion 1 asks only `TestBreaksAccepted` to fail there. Two cold reads on 2026-11-24 found nothing serious, and a trial patch of the planned change, run against the whole suite, broke only `test_new_criterion_rejects_all_line_breaks`.

The ticket appears actionable, but implementation was not started in this session. The requested baseline run against main and code/test changes remain outstanding, so no acceptance criterion has been verified. No ticket defect or external obstacle was identified. Decision needed: resume implementation from the current plan; do not split—the scope is a focused parser/criterion fix with specified tests.

Planner, 2026-11-25: fixed the CLI test fixture: `chitty add` needs `-d` outside `backlog`, so it is now `run_cli("add", "T", "-d", "x", "--ac", "one")` (found by a Codex worker in a trial run). Nothing else changed.

Planner, 2026-11-25: back to `planning`. A Sonnet worker in a throwaway trial clone (`tmp/worker-trial/runs/claude-sonnet--task-451`, not this branch) implemented the ticket and found two wrong claims in it. Its note follows unchanged; resolve both before the next cold read. Its partial work is on that clone's `task-451` branch, not here.

Worker, 2026-11-25: back to planning for two wrong claims in the Description. Both need decisions. Partial work, matching the ticket as written, is committed on `task-451` (commit "End ticket file lines only at LF so criteria keep other separators"). It must not land as it is: it exposes the second problem.

1. `U+2028` and `U+2029` do not always read back unchanged.
   - Claim: "`U+2028` and `U+2029` already read back unchanged after the change, so they need nothing."
   - Evidence: with the change, a title or label holding a space next to either character loses the space. `a U+2028b` and `aU+2028 b` both read back as `aU+2028b` (same for `U+2029`). `chitty add` with title `a U+2028b` succeeds and `show --json` gives `aU+2028b`. On `main`, `a U+2028b` is refused as unreadable, so there the change turns a refusal into a silent alteration; `aU+2028 b` is already altered on `main`. `owner` was not probed, but uses the same `render_scalar`.
   - Decision: should `render_scalar` also escape these two? Suggested: yes, treat them as `\x85` is treated (`json.dumps`, then replace each with its `\uXXXX` escape). A `yaml.safe_load` probe read such escaped values back unchanged, including with adjacent spaces and tabs. Add those cases to the frontmatter example.

2. The change breaks a second existing test, through the suggestion inbox.
   - Claim: `test_new_criterion_rejects_all_line_breaks` "is the only existing test the change breaks".
   - Evidence: `make check` gives 1 failed, 1189 passed. The failure is `test_accepted_suggestion_pulls_with_the_same_title_and_description` in `tests/test_property_inbox.py`. That file passes against `main`'s source.
   - Title `0\x85`: `main` refuses it in `suggest`; now `suggest` accepts it and `pull` stores `0 ` (silent alteration).
   - Title `0U+2028\x85`: `main` refuses it; now `suggest` accepts it and `pull` fails with `value '0U+2028\n' must be a single line`.
   - Cause: `suggest` in `src/chitty/inbox.py` writes the inbox file with `yaml.safe_dump(..., allow_unicode=True)`, and PyYAML does not read its own output back for these titles. Its round-trip guard checks only `new_task`, not the inbox file. `main` hid this because the parser refused the titles.
   - Why blocked: the ticket does not describe any change to `inbox.py` or whether such suggestions should be accepted, and criterion 2 cannot pass without one.
   - Decision: how should the inbox write these titles? Suggested: accept them and write the file so they read back. `allow_unicode=False` round-trips both titles in a probe but escapes all non-ASCII text, so prefer escaping only when the title holds `\x85`, `U+2028` or `U+2029`. Describe a fixed example for both titles. `_read_suggestion` also splits with `str.splitlines`; no failure was traced to that, but check it with the chosen fix.

State of the criteria (none ticked):
- 1: new tests pass on the branch. Baseline against `main` `2fc1b7d1` source (`python -m unittest -v tests.test_criteria_line_breaks`, before the fix): all 8 tests in `TestBreaksAccepted` fail (property, break inside, break at end, `a\n`, parse, renumbering caller, frontmatter, CLI); both tests in `TestUnchangedBehaviour` pass. `test_new_criterion_rejects_all_line_breaks` is narrowed to `\n` and `\r`.
- 2: not met, see 2 above. `tests/test_property_criterion_text.py` passes, and ruff and pyright passed.
- 3: renumbering-caller example fails on `main`'s source and passes on the branch; `tests/test_property_renumbering.py` passes.
- 4: frontmatter example fails on `main`'s source for all three characters and passes on the branch, including the `"a\u0085b"` line.

Not checked: `make test` (random examples) and the Linux check. Also added a line to `docs/plan/task-file.md` saying lines end only at `\n`. Unrelated older bug filed as `TASK-XX8E7B` (control characters written as unreadable YAML).

## History

- 2026-11-19T20:55:25Z sunny-white-dormouse → backlog
- 2026-11-19T20:55:27Z sunny-white-dormouse: changed notes
- 2026-11-19T21:00:22Z sunny-white-dormouse: changed title, labels, priority, description, acceptance criteria
- 2026-11-19T21:00:22Z sunny-white-dormouse backlog → planning
- 2026-11-19T21:01:24Z sunny-white-dormouse: changed acceptance criteria
- 2026-11-19T21:01:24Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:03:38Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:03:38Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:03:49Z sunny-white-dormouse planning → cold-read
- 2026-11-19T21:05:29Z sunny-white-dormouse: changed description, acceptance criteria
- 2026-11-19T21:05:29Z sunny-white-dormouse cold-read → planning
- 2026-11-19T21:05:47Z sunny-white-dormouse planning → todo
- 2026-11-20T00:41:45Z nimble-fawn-eel todo → doing
- 2026-11-22T21:26:06Z rosy-pearl-falcon: changed owner, notes
- 2026-11-22T21:26:06Z rosy-pearl-falcon doing → planning
- 2026-11-22T22:01:15Z human planning → review
- 2026-11-22T22:04:08Z witty-ebony-puffin: changed owner, acceptance criteria, notes
- 2026-11-22T22:04:08Z witty-ebony-puffin review → planning
- 2026-11-23T12:02:04Z witty-russet-gannet: changed title, description, acceptance criteria, notes
- 2026-11-23T12:02:04Z witty-russet-gannet planning → cold-read
- 2026-11-23T12:04:56Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:06:43Z witty-russet-gannet: changed description, acceptance criteria, notes
- 2026-11-23T12:06:43Z witty-russet-gannet cold-read → todo
- 2026-11-23T12:34:57Z plucky-jade-dormouse todo → doing
- 2026-11-23T12:38:43Z plucky-jade-dormouse: changed owner, notes
- 2026-11-23T12:38:43Z plucky-jade-dormouse doing → planning
- 2026-11-23T23:05:38Z mellow-amber-toad: changed acceptance criteria
- 2026-11-23T23:05:38Z mellow-amber-toad planning → cold-read
- 2026-11-23T23:07:50Z mellow-amber-toad: changed description
- 2026-11-23T23:07:50Z mellow-amber-toad cold-read → planning
- 2026-11-23T23:07:56Z mellow-amber-toad planning → todo
- 2026-11-23T23:25:25Z mellow-amber-urchin todo → doing
- 2026-11-23T23:27:54Z mellow-amber-urchin: changed owner, notes
- 2026-11-23T23:27:54Z mellow-amber-urchin doing → planning
- 2026-11-24T07:33:08Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T07:33:08Z sunny-hazel-gannet planning → cold-read
- 2026-11-24T07:41:10Z sunny-hazel-gannet: changed description, acceptance criteria
- 2026-11-24T07:43:37Z sunny-hazel-gannet: changed description
- 2026-11-24T07:43:37Z sunny-hazel-gannet cold-read → planning
- 2026-11-24T07:43:39Z sunny-hazel-gannet planning → todo
- 2026-11-24T07:44:08Z sunny-hazel-gannet: changed description
- 2026-11-24T09:18:36Z kind-teal-urchin todo → doing
- 2026-11-24T09:21:07Z kind-teal-urchin: wrote the plan
- 2026-11-24T09:21:21Z kind-teal-urchin: changed owner, notes
- 2026-11-24T09:21:21Z kind-teal-urchin doing → planning
- 2026-11-24T09:27:09Z sunny-hazel-gannet: replaced notes; changed owner, description, acceptance criteria
- 2026-11-24T09:27:12Z sunny-hazel-gannet planning → todo
- 2026-11-24T09:35:19Z open-pearl-raven todo → doing
- 2026-11-24T09:37:40Z open-pearl-raven: wrote the plan
- 2026-11-24T09:38:18Z open-pearl-raven: changed owner, notes
- 2026-11-24T09:38:18Z open-pearl-raven doing → planning
- 2026-11-25T11:34:54Z sunny-hazel-gannet: changed description, notes
- 2026-11-25T11:34:54Z sunny-hazel-gannet planning → todo
- 2026-11-25T12:11:52Z sunny-hazel-gannet: changed notes
- 2026-11-25T12:11:52Z sunny-hazel-gannet todo → planning
