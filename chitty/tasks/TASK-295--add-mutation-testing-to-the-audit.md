---
title: Add mutation testing to the audit
status: backlog
depends_on:
  - TASK-291
parent: TASK-290
created: 2026-11-11
---

## Description

- Find out whether the tests catch changes to the code, over all of `src/chitty`. A run may take a couple of hours, which is fine: it runs overnight, started by a person.
- Add `make mutate` (`## mutation-test main in a detached worktree; write a report for planning`): it makes a detached worktree of `main` under `.worktrees/`, runs setup there, runs the mutation tool, and writes one Markdown report of surviving mutants grouped by file, each with its line and diff, then removes the worktree. It sends no suggestions and creates no tickets: a planner reads the report and decides what to ticket.
- Planning decides where the report goes (for example a gitignored `reports/` directory, named by date).
- Pick the tool: `mutmut` 3 expects pytest, and this repository uses `unittest`; `cosmic-ray` takes any test command.

## Acceptance Criteria

- [ ] A test mutates a temporary module whose test does not check its return value: one survivor is suggested, with its file and line. It fails today.

## History

- 2026-11-11T16:18:27Z vivid-yellowhammer → backlog
- 2026-11-11T18:50:44Z vivid-yellowhammer: changed description
- 2026-11-16T10:28:59Z intrepid-coral-raven: changed description
