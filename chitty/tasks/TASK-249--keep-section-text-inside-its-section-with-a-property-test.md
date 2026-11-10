---
title: Keep section text inside its section, with a property test
status: backlog
created: 2026-11-10
---

## Description

First of two trial tickets for property tests (Hypothesis is already a dev dependency; see `tests/test_check_edit.py`).

**Property:** for any text, `Task.with_section(name, text)` (Description, Plan, Notes, Summary) and `Task.with_note(text)` either raise `TaskError`, or the re-parsed task has that text, as `_text_lines` normalises it, in that section, and every other section unchanged.

**Fails today:**

- Description text with a `## Notes`, `## Plan` or `## Summary` line is accepted, and everything after it moves into that section.
- `## Background` is already rejected, and `###` lines stay inside the section.

**Fix:** in `src/chitty/model.py`, reject section text with a `## ` line outside a code fence, saying to use `###`.

**Test:** `tests/test_property_sections.py`. Draw text that mixes ordinary lines with `## <known section>` lines, fences and `###` lines, so Hypothesis finds the failure at default settings. Note the counterexample it found before the fix.

## Acceptance Criteria

- [ ] The property test fails before the fix with a counterexample containing a known `## ` section line, and passes after.
- [ ] `chitty edit <ID> -d` with text containing a `## Plan` line exits non-zero, says to use `###`, and leaves the file unchanged; text with a `### Plan` line stays in the Description.

## History

- 2026-11-10T21:12:37Z jolly-heron → backlog
