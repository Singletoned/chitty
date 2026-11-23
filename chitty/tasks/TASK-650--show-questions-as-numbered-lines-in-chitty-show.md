---
title: Show `## Questions` as numbered lines in `chitty show`
status: cold-read
depends_on:
  - TASK-649
  - TASK-629
parent: TASK-621
created: 2026-11-23
---

## Description

Part of TASK-621. TASK-629 parses `## Questions` and TASK-649 adds it to `as_dict`; this ticket depends on both. It shows the questions in `chitty show`.

`chitty show` (`_format` in `src/chitty/cli.py`, which today special-cases only Acceptance Criteria; add a Questions branch rather than printing the raw section) prints the section after Acceptance Criteria as `n. [x] text`. When there is an answer, it adds a line of three spaces followed by the answer. The section is left out when there are no questions.

Tests, in `tests/test_questions_section.py` (created by TASK-629; add to it):

- In a `RepoTestCase` repository, write a ticket file with the example section from TASK-629. The output of `chitty show TASK-1`, split into lines, contains this exact run of consecutive lines: `"## Questions"`, `""`, `"1. [x] Which database?"`, `"   Postgres, because we already run it."`, `"2. [ ] Who owns the migration?"`, and the last of these is the final line or is followed by a line that does not start with a space (the unanswered question has no answer line). `show --json` has the two `questions` entries.
- A ticket with no `## Questions` section: `chitty show` output does not contain `Questions`.

Baseline for "fails before the change": `main` with TASK-629 and TASK-649 landed, where `_format` prints the raw section (`- [x] Which database?`), so the first test fails on its line assertion. Record that message in a note.

Out of scope: CLI and MCP options (TASK-630) and list markers (TASK-631).

## Acceptance Criteria

- [ ] Both `chitty show` tests in `tests/test_questions_section.py` pass; the first fails on its line assertion at the baseline named in the Description; record that failure message in a note
- [ ] `make check` passes

## History

- 2026-11-23T19:43:27Z friendly-coral-badger → planning
- 2026-11-23T19:43:56Z friendly-coral-badger planning → cold-read
- 2026-11-23T19:45:11Z friendly-coral-badger: changed dependencies, description, acceptance criteria
- 2026-11-23T19:45:11Z friendly-coral-badger cold-read → planning
- 2026-11-23T19:46:09Z friendly-coral-badger planning → cold-read
