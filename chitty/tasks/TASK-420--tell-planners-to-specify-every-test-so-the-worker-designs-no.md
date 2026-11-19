---
title: Tell planners to specify every test so the worker designs none
status: todo
labels:
  - untestable
owner: untestable
created: 2026-11-19
---

## Description

Owner decision 2026-11-19: the worker should only implement; it should not have to design tests. A clear description of each test belongs in the ticket. `TASK-382` failed review three times because its criterion 1 listed four failure cases and about twelve checks, and the worker had to invent the fixtures and assertions: it read the worktree instead of the branch tip, asserted a value read before the run, and left out checks. Tickets planned the same day with concrete tests (`TASK-412` to `TASK-418`) were built in one pass.

Change `src/chitty/roles/plan.md`: for each test, the ticket names its file and class, the fixture (files, branches, config, environment), the action, and the exact assertions, including how each value is read (for example `git show <branch>:<path>`, read after the run); for a generated test, the generator and the property. A criterion then names the test it is shown by. Keep the advice general: the guides reach every repository that uses Chitty (`AGENTS.md`).

## History

- 2026-11-19T13:22:19Z quick-ginger-lapwing → todo
