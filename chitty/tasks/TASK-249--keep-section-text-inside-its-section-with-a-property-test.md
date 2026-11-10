---
title: Keep section text inside its section, with a property test
status: backlog
created: 2026-11-10
---

## Description

First of two trial tickets for property tests (Hypothesis is already a dev dependency; see `tests/test_check_edit.py`).

**Property:** for any text, `Task.with_section(name, text)` (Description, Plan, Notes, Summary) and `Task.with_note(text)` either raise `TaskError`, or the re-parsed task holds that text, normalised by `_text_lines`, in that section, with every other section unchanged. `with_note` appends, so compare the end of Notes.

**Fails today** (all found by a cold read's Hypothesis test):

- a `## Notes`, `## Plan` or `## Summary` line, including `##<tab>Plan`, moves what follows into that section;
- an unclosed fence (a lone ```` ``` ```` or `~~~`) swallows every following section.

**Fix:** don't add another heading rule. In `src/chitty/model.py`, after building the new task, re-parse it and check the property itself. On a mismatch, raise `TaskError` naming the section and saying to use `###` for headings and to close code fences.

**Test:** `tests/test_property_sections.py`. Draw lines mixing ordinary text, `## <known section>` (with a space or a tab), `###` lines and fence lines. `tests/test_model.py` `test_heading_in_text_is_rejected` expects the old message; update it.

## Acceptance Criteria

- [ ] The property test fails before the fix with a `## ` section line or an unclosed fence as the counterexample, and passes after.
- [ ] `chitty edit <ID> -d` with text containing a `## Plan` line exits non-zero, says to use `###`, and leaves the file unchanged; text with a `### Plan` line stays in the Description.

## Notes

Haiku cold read 1 (`refs/cold-read/TASK-249/1`): the first fix (reject `## ` lines outside fences) still failed the property on unclosed fences and `##<tab>`. Replaced it with a re-parse check.

## History

- 2026-11-10T21:12:37Z jolly-heron → backlog
- 2026-11-10T21:17:09Z jolly-heron: replaced notes; changed description, acceptance criteria
