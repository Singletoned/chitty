---
title: Show `## Questions` as numbered lines in `chitty show`
status: planning
depends_on:
  - TASK-649
parent: TASK-621
created: 2026-11-23
---

## Description

Part of TASK-621. TASK-629 parses `## Questions` and TASK-649 adds it to `as_dict`. This ticket shows the questions in `chitty show`.

`chitty show` (`_format` in `src/chitty/cli.py`, which today special-cases only Acceptance Criteria; add a Questions branch rather than printing the raw section) prints the section after Acceptance Criteria as `n. [x] text`. When there is an answer, it adds a line of three spaces followed by the answer. The section is left out when there are no questions.

Test, in `tests/test_questions_section.py`:

- `chitty show`: in a `RepoTestCase` repository, write a ticket file with the example section from TASK-629. `chitty show TASK-1` prints `## Questions`, `1. [x] Which database?`, `   Postgres, because we already run it.` and `2. [ ] Who owns the migration?` in that order. `show --json` has the two `questions` entries.

Before the change the text assertions fail, because `_format` prints the raw section (`- [x] Which database?`) instead of numbered lines.

Out of scope: CLI and MCP options (TASK-630) and list markers (TASK-631).

## Acceptance Criteria

- [ ] The `chitty show` test in `tests/test_questions_section.py` passes and fails before the change; record its failure message in a note
- [ ] `make check` passes

## History

- 2026-11-23T19:43:27Z friendly-coral-badger → planning
