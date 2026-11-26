---
title: Show `## Questions` as numbered lines in `chitty show`
status: review
depends_on:
  - TASK-649
  - TASK-629
  - TASK-10035
parent: TASK-621
created: 2026-11-23
---

## Description

Part of TASK-621. TASK-629 parses `## Questions` and TASK-649 adds it to `as_dict`; this ticket depends on both. It shows the questions in `chitty show`.

`chitty show` (`_format` in `src/chitty/cli.py`, which today special-cases only Acceptance Criteria; add a Questions branch rather than printing the raw section) prints the section directly after Acceptance Criteria and before Plan (its place in `SECTION_ORDER`, set by TASK-629) as `n. [x] text`. When there is an answer, it adds one line of three spaces followed by the answer (`Question.answer` is already one line, its lines joined by TASK-629). The section is left out when there are no questions.

Tests, in `tests/test_questions_section.py` (created by TASK-629; add to it):

- In a `RepoTestCase` repository, write a ticket file with the example section from TASK-629. The output of `chitty show TASK-1`, split into lines, contains this exact run of consecutive lines: `"## Questions"`, `""`, `"1. [x] Which database?"`, `"   Postgres, because we already run it."`, `"2. [ ] Who owns the migration?"`, and the last of these is the final line or is followed by a line that does not start with a space (the unanswered question has no answer line). `show --json` has the two `questions` entries.
- A ticket with no `## Questions` section: no line of `chitty show` output equals `## Questions`. This guards the left-out rule and passes at baseline; the first test is the fail-first evidence.

Baseline for "fails before the change": `main` with TASK-629 and TASK-649 landed, where `_format` prints the raw section (`- [x] Which database?`), so the first test fails on its line assertion. Record that message in a note.

Out of scope: CLI and MCP options (TASK-630) and list markers (TASK-631).

## Acceptance Criteria

- [x] Both `chitty show` tests in `tests/test_questions_section.py` pass; the first fails on its line assertion at the baseline named in the Description; record that failure message in a note
- [x] `make check` passes

## Plan

Add CLI show tests and confirm the formatted questions test fails at baseline; render parsed questions in section order, then run formatting and checks.

## Notes

Second cold read (2026-11-23): nothing serious. Its baseline and `SECTION_ORDER` points repeat ones already settled (baseline is `main` with TASK-629 and TASK-649 landed; TASK-629 adds the name). Fixed: placement before Plan, one-line answers, and the no-questions check is now an exact line match.

Baseline: `.venv/bin/pytest -q tests/test_questions_section.py::TestShowQuestions` failed as expected: `AssertionError: Lists differ`; first differing element 2 was `- [x] Which database?` instead of `1. [x] Which database?`. The no-questions test passed.

## Summary

Show numbered questions and indented answers in section order; JSON remains unchanged. Added CLI coverage and confirmed the formatting test fails at baseline. make check passes.

## History

- 2026-11-23T19:43:27Z friendly-coral-badger → planning
- 2026-11-23T19:43:56Z friendly-coral-badger planning → cold-read
- 2026-11-23T19:45:11Z friendly-coral-badger: changed dependencies, description, acceptance criteria
- 2026-11-23T19:45:11Z friendly-coral-badger cold-read → planning
- 2026-11-23T19:46:09Z friendly-coral-badger planning → cold-read
- 2026-11-23T19:47:23Z friendly-coral-badger: changed description, notes
- 2026-11-23T19:47:23Z friendly-coral-badger cold-read → planning
- 2026-11-23T19:47:26Z friendly-coral-badger planning → todo
- 2026-11-26T11:27:48Z brisk-bronze-adder: changed dependencies
- 2026-11-26T14:48:22Z youthful-fawn-wren todo → doing
- 2026-11-26T14:52:24Z youthful-fawn-wren: wrote the plan
- 2026-11-26T14:53:19Z youthful-fawn-wren: changed notes
- 2026-11-26T14:57:32Z youthful-fawn-wren: changed summary; ticked acceptance criteria
- 2026-11-26T15:00:04Z youthful-fawn-wren doing → review
