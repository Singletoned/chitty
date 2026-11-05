---
title: Tell workers to see a regression test fail, and to stop on a wrong ticket
status: backlog
priority: medium
parent: TASK-106
created: 2026-11-05
---

## Description

Some faults only show up in the real implementation, however the ticket was read. On `TASK-31` in `echonomicon` a test passed with or without the fix, and on `TASK-137` here Luna left out a required test. `src/chitty/roles/work.md` says nothing about either. The human agreed on 2026-11-05 to add this to the guide alongside implementing cold reads, which do not replace it.

Add this bullet to `src/chitty/roles/work.md`, adjusting only line wrapping:

"See a regression test fail without the fix, and say so in a note. If it passes without the fix, it proves nothing: change it. If the ticket itself is wrong, because following it would break something or a claim in it is false, do not work around it: note what you found and set `-s blocked`. An unclear detail with a cheap default is not this: choose it, as below."

Put it before the bullet on cheap-to-reverse defaults, so that "as below" holds. This file ships to every repository, so do not name `make`. `chitty guide work` serves it at run time, and `AGENTS.md` does not hold it, so no `chitty init` or version bump is needed. Other tickets edit this file, including `TASK-173` and `TASK-179`, so add only this bullet.

Out of scope: having Chitty check that a test failed.

## Acceptance Criteria

- [ ] A test in `TestGuide` in `tests/test_cli.py` shows `guide("work")` containing `See a regression test fail without the fix`, `do not work around it` and `An unclear detail with a cheap default is not this`, and fails against the current `work.md`

## History

- 2026-11-05T17:53:54Z mellow-newt → backlog
