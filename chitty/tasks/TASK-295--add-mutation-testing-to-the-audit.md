---
title: Add mutation testing to the audit
status: backlog
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- Find out whether the tests catch changes to the code. Mutation testing over all of `src/chitty` with every test is likely to take hours, so mutate only modules changed on `main` in the last 7 days, within a time budget set as a module constant.
- Pick the tool: `mutmut` 3 expects pytest, and this repository uses `unittest`; `cosmic-ray` takes any test command. Report each surviving mutant as `Audit: mutant survived in <file>:<line>`, with the diff.

## Acceptance Criteria

- [ ] A test mutates a temporary module whose test does not check its return value: one survivor is suggested, with its file and line. It fails today.

## History

- 2026-11-11T16:18:27Z vivid-yellowhammer → backlog
